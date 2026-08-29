#!/usr/bin/env python3
"""Nightly scan: diff every vendored CSV against the last scan, email what's new.

Run by .github/workflows/daily-scan.yml after `make fetch` (with
AI_DISCOVERY_AS_OF set to today, so the fetchers that clip at the snapshot
date can see rows published since the last commit):

    python3 tools/daily_scan.py --baseline .scan-baseline --charts scan-charts --email

The baseline is a mirror of problems/*/*.csv as the previous scan fetched
them, kept between runs in an Actions cache. Diffing against the previous
*scan* rather than against HEAD is what keeps the email quiet: a series that
moved once and has not been re-vendored yet is reported the night it moves and
never again. A CSV with no baseline copy falls back to the committed version,
so the first run reports drift since the last commit.

For every problem whose data moved, the email carries one chart: the series
over its recent window, with the periods that gained or changed rows picked
out in the collection's AI red against a muted slate. The chart is drawn with
whatever matplotlib the runner has — it is an email body, not a committed
figure, so the pinned-renderer rule for problems/*/figure.py does not apply
and nothing here writes into a problem folder.

Email is plain SMTP (STARTTLS), configured through the environment:

    SCAN_SMTP_HOST      default smtp.gmail.com
    SCAN_SMTP_PORT      default 587
    SCAN_SMTP_USERNAME  login, and the default From address
    SCAN_SMTP_PASSWORD  for Gmail this is an app password, not the account one
    SCAN_EMAIL_TO       recipient
    SCAN_EMAIL_FROM     optional, defaults to SCAN_SMTP_USERNAME

The baseline is refreshed only after the news has actually gone out (or when
there is none), so a night with missing credentials or a dead SMTP host exits
nonzero, keeps the old baseline, and the next run reports the same changes
again instead of losing them.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import shutil
import smtplib
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.dates import period_bounds  # noqa: E402  (matplotlib-free)
from lib.document import front_matter, title  # noqa: E402
from lib.palette import AI, UNATTRIBUTED  # noqa: E402

# First matching column names the row's period. Exact matches only: the ledger
# CSVs carry list_year and resolved_year but no bare year, so they fall through
# to resolved_year and chart resolutions rather than the list's founding date.
TIME_COLS = ("quarter", "month", "year", "date", "recorded_date",
             "release_date", "published", "datetime_utc", "resolved_year",
             "solution_year")

# Count-like columns worth summing into the chart. A CSV with none of these
# (record tables, ledgers, finder lists) is charted as rows per period, which
# for those shapes is the discovery rate.
VALUE_COLS = ("total", "unique_cves", "distinct_cves", "discoveries",
              "kev_added", "nvd_published", "cves", "submissions",
              "dois_created", "git_pushes", "total_problems",
              "better_incumbents")

# Columns that name a row rather than date or measure it, for pairing a
# revised row with its previous version. resolved_year and solution_year are
# excluded from pairing on purpose: they are the outcome that changes when a
# ledger row is resolved, so keying on them would report one resolution as an
# unrelated addition and removal.
ID_COLS = ("problem_id", "cve", "slug", "problem", "instance", "curve_id",
           "finder", "record", "release", "solufile", "series", "quantity",
           "step")

# What to call a row in a one-line summary, most specific name first.
LABEL_COLS = ("short_name", "title", "cve", "finder", "problem", "slug",
              "instance", "release", "record")

MAX_LINES_PER_CSV = 8
MAX_CHARTS = 16
RECENT_PERIODS = 30


def parse_rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    return list(fields), [dict(row) for row in reader]


def committed_text(relpath: str) -> str:
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        capture_output=True, cwd=ROOT,
    )
    return result.stdout.decode("utf-8") if result.returncode == 0 else ""


def time_col(fields: list[str]) -> str | None:
    return next((c for c in TIME_COLS if c in fields), None)


def period_of(row: dict[str, str], col: str) -> str:
    """The row's period as a label period_bounds accepts, or ''.

    Full dates aggregate to their year: the discovery charts in this
    collection count events per year, and an email chart with one bar per
    published-date would be a barcode, not a series.
    """
    value = (row.get(col) or "").strip()
    if len(value) >= 10 and value[4] == "-":  # date or datetime
        return value[:4]
    return value


@dataclass
class CsvDiff:
    relpath: str
    fields: list[str]
    rows: list[dict[str, str]]
    added: list[dict[str, str]]
    removed: list[dict[str, str]]
    schema_changed: bool = False

    @property
    def name(self) -> str:
        return Path(self.relpath).name

    def pair_key(self, row: dict[str, str]) -> tuple:
        """What identifies a row across revisions: its ids plus its period."""
        cols = [c for c in ID_COLS if c in self.fields]
        col = time_col(self.fields)
        if col and col not in ("resolved_year", "solution_year"):
            cols.append(col)
        return tuple(row.get(c, "") for c in cols) if cols else ()

    def label(self, row: dict[str, str]) -> str:
        for col in LABEL_COLS:
            if (row.get(col) or "").strip():
                return row[col]
        col = time_col(self.fields)
        return row.get(col, "") if col else ""

    def lines(self) -> list[str]:
        """Human summary, pairing a revised row with its previous version.

        A count CSV revises a period by replacing its row, which the multiset
        diff sees as one removal plus one addition; showing "2025-Q3: total
        12 → 14" instead of two full rows is the difference between an email
        and a diff dump. The same pairing shows a ledger resolution as one
        status change on the named problem.
        """
        if self.schema_changed:
            return [f"{self.name}: column layout changed — see the repository"]
        out: list[str] = []
        removed_left = list(self.removed)
        for row in self.added:
            old = None
            key = self.pair_key(row)
            if key:
                match = [r for r in removed_left if self.pair_key(r) == key]
                if match:
                    old = match[0]
                    removed_left.remove(old)
            if old:
                changes = [
                    f"{k} {old.get(k) or '(empty)'} → {row.get(k) or '(empty)'}"
                    for k in self.fields if old.get(k) != row.get(k)
                ][:4]
                out.append(f"{self.label(row)}: " + ", ".join(changes))
            else:
                shown = [f"{k}={row[k]}" for k in self.fields
                         if (row.get(k) or "").strip()][:5]
                out.append("new — " + ", ".join(shown))
        for row in removed_left:
            shown = [f"{k}={row[k]}" for k in self.fields
                     if (row.get(k) or "").strip()][:5]
            out.append("dropped — " + ", ".join(shown))
        return out

    def changed_periods(self) -> set[str]:
        col = time_col(self.fields)
        if not col:
            return set()
        return {p for row in self.added + self.removed
                if (p := period_of(row, col))}


@dataclass
class ProblemNews:
    slug: str
    title: str
    domain: str
    diffs: list[CsvDiff] = field(default_factory=list)
    chart: Path | None = None


def diff_csv(relpath: str, baseline_dir: Path | None) -> CsvDiff | None:
    current = (ROOT / relpath).read_text(encoding="utf-8")
    old_text = ""
    if baseline_dir is not None and (baseline_dir / relpath).exists():
        old_text = (baseline_dir / relpath).read_text(encoding="utf-8")
    else:
        old_text = committed_text(relpath)
    if current == old_text:
        return None
    fields, rows = parse_rows(current)
    old_fields, old_rows = parse_rows(old_text)
    if old_text and old_fields != fields:
        return CsvDiff(relpath, fields, rows, [], [], schema_changed=True)

    def key(row: dict[str, str]) -> tuple:
        return tuple(row.get(f, "") for f in fields)

    new_count = Counter(key(r) for r in rows)
    old_count = Counter(key(r) for r in old_rows)
    by_key = {key(r): r for r in rows}
    old_by_key = {key(r): r for r in old_rows}
    added = [by_key[k] for k, n in (new_count - old_count).items() for _ in range(n)]
    removed = [old_by_key[k] for k, n in (old_count - new_count).items() for _ in range(n)]
    if not added and not removed:
        return None  # e.g. only a newline-style difference
    return CsvDiff(relpath, fields, rows, added, removed)


def scan(baseline_dir: Path | None) -> list[ProblemNews]:
    news: dict[str, ProblemNews] = {}
    for path in sorted(ROOT.glob("problems/*/*.csv")):
        relpath = path.relative_to(ROOT).as_posix()
        diff = diff_csv(relpath, baseline_dir)
        if diff is None:
            continue
        slug = path.parent.name
        if slug not in news:
            text = (path.parent / "README.md").read_text(encoding="utf-8") \
                if (path.parent / "README.md").exists() else ""
            news[slug] = ProblemNews(
                slug=slug,
                title=title(text) or slug,
                domain=front_matter(text).get("Domain", "other"),
            )
        news[slug].diffs.append(diff)
    return list(news.values())


# ---------------------------------------------------------------- charts

def chartable(diff: CsvDiff) -> bool:
    return not diff.schema_changed and time_col(diff.fields) is not None


def draw_chart(problem: ProblemNews, out_dir: Path) -> Path | None:
    """One bar chart: the series' recent window, changed periods in red.

    Muted slate carries the context and the AI red carries "new since the
    last scan"; identity is doubled by the legend and by the value printed
    over each changed bar, so the chart survives greyscale and CVD.
    """
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    diff = max((d for d in problem.diffs if chartable(d)),
               key=lambda d: len(d.added), default=None)
    if diff is None:
        return None
    col = time_col(diff.fields)
    value_col = next((c for c in VALUE_COLS if c in diff.fields), None)
    totals: dict[str, float] = defaultdict(float)
    for row in diff.rows:
        period = period_of(row, col)
        if not period:
            continue
        try:
            period_bounds(period)
        except ValueError:
            continue
        if value_col:
            try:
                totals[period] += float(row[value_col] or 0)
            except ValueError:
                totals[period] += 1
        else:
            totals[period] += 1
    if not totals:
        return None
    periods = sorted(totals, key=lambda p: period_bounds(p)[0])
    changed = diff.changed_periods() & set(totals)
    start = len(periods) - RECENT_PERIODS
    if changed:
        start = min(start, periods.index(min(changed, key=lambda p: period_bounds(p)[0])))
    periods = periods[max(start, 0):]

    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=140)
    for period in periods:
        left, right = period_bounds(period)
        new = period in changed
        ax.bar((left + right) / 2, totals[period], width=(right - left) * 0.82,
               color=AI if new else UNATTRIBUTED, alpha=1.0 if new else 0.55,
               zorder=3)
        if new:
            ax.annotate(f"{totals[period]:g}",
                        ((left + right) / 2, totals[period]),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", fontsize=8, color=AI, fontweight="bold")
    ax.set_title(problem.title, loc="left", fontsize=11, fontweight="bold")
    unit = value_col or ("resolutions" if col in ("resolved_year",
                                                  "solution_year") else "entries")
    cadence = col if col in ("quarter", "month") else "year"
    ax.set_ylabel(f"{unit} per {cadence}", fontsize=8.5, color="#444444")
    ax.set_ylim(0, max(totals[p] for p in periods) * 1.18)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(axis="y", color="#e3e3e3", linewidth=0.7, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#bbbbbb")
    ax.tick_params(colors="#666666", labelsize=8)
    if len(periods) > 10:
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=8))
    handles = [plt.Rectangle((0, 0), 1, 1, color=UNATTRIBUTED, alpha=0.55),
               plt.Rectangle((0, 0), 1, 1, color=AI)]
    ax.legend(handles, ["already recorded", "new or revised since last scan"],
              frameon=False, fontsize=8, loc="upper left")
    ax.text(0.0, -0.24, f"Source: {diff.name}", transform=ax.transAxes,
            fontsize=7.5, color="#888888")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"scan-{problem.slug}.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# ---------------------------------------------------------------- reporting

# The **Domain:** vocabulary of FORMAT.md front matter, in the index's order.
DOMAIN_ORDER = ("vulnerabilities", "mathematics", "algorithms",
                "outside the three domains")


def in_domain_order(news: list[ProblemNews]) -> list[ProblemNews]:
    rank = {d: i for i, d in enumerate(DOMAIN_ORDER)}
    return sorted(news, key=lambda p: (rank.get(p.domain.lower(), len(rank)),
                                       p.slug))


def text_report(news: list[ProblemNews], today: str) -> str:
    out = [f"New results in {len(news)} series, scan of {today}", ""]
    last_domain = None
    for problem in in_domain_order(news):
        if problem.domain != last_domain:
            out += [problem.domain.upper(), ""]
            last_domain = problem.domain
        out.append(f"* {problem.title} ({problem.slug})")
        for diff in problem.diffs:
            lines = diff.lines()
            for line in lines[:MAX_LINES_PER_CSV]:
                out.append(f"    {diff.name} — {line}")
            if len(lines) > MAX_LINES_PER_CSV:
                out.append(f"    {diff.name} — … and "
                           f"{len(lines) - MAX_LINES_PER_CSV} more")
        out.append("")
    out.append("Charts compare against the previous night's fetch; the "
               "repository itself is unchanged until the series is re-vendored "
               "with `make fetch`.")
    return "\n".join(out)


def html_report(news: list[ProblemNews], today: str,
                cids: dict[str, str]) -> str:
    def esc(text: str) -> str:
        # Quotes included: escaped text also lands in attributes (img alt).
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("'", "&#39;")
                .replace('"', "&quot;"))

    out = [
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,'
        'sans-serif;max-width:680px;color:#1a1a1a">',
        f"<h2 style='margin-bottom:2px'>New results in {len(news)} series</h2>",
        f"<p style='color:#666;margin-top:0'>Overnight scan of {today}, "
        "compared with the previous scan.</p>",
    ]
    last_domain = None
    for problem in in_domain_order(news):
        if problem.domain != last_domain:
            out.append(f"<h3 style='border-bottom:1px solid #ddd;"
                       f"padding-bottom:3px'>{esc(problem.domain.title())}</h3>")
            last_domain = problem.domain
        url = (f"https://github.com/tecunningham/ai-discovery-data/tree/main/"
               f"problems/{problem.slug}/")
        out.append(f"<h4 style='margin-bottom:4px'>"
                   f"<a href='{url}' style='color:#1a1a1a'>"
                   f"{esc(problem.title)}</a></h4>")
        out.append("<ul style='margin-top:4px'>")
        for diff in problem.diffs:
            lines = diff.lines()
            for line in lines[:MAX_LINES_PER_CSV]:
                out.append(f"<li style='font-size:13px'><code>{esc(diff.name)}"
                           f"</code> — {esc(line)}</li>")
            if len(lines) > MAX_LINES_PER_CSV:
                out.append(f"<li style='font-size:13px;color:#666'>… and "
                           f"{len(lines) - MAX_LINES_PER_CSV} more in "
                           f"<code>{esc(diff.name)}</code></li>")
        out.append("</ul>")
        if problem.slug in cids:
            out.append(f"<img src='cid:{cids[problem.slug]}' width='640' "
                       f"alt='Recent series for {esc(problem.title)}, new "
                       f"periods highlighted' "
                       f"style='max-width:100%;height:auto'>")
    out.append("<p style='color:#888;font-size:12px'>Sent by the "
               "<a href='https://github.com/tecunningham/ai-discovery-data/"
               "actions/workflows/daily-scan.yml'>daily-scan workflow</a>. "
               "The repository is unchanged until the series is re-vendored "
               "with <code>make fetch</code>.</p></div>")
    return "\n".join(out)


def send_email(news: list[ProblemNews], today: str) -> None:
    host = os.environ.get("SCAN_SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SCAN_SMTP_PORT", "587"))
    user = os.environ.get("SCAN_SMTP_USERNAME", "")
    password = os.environ.get("SCAN_SMTP_PASSWORD", "")
    to = os.environ.get("SCAN_EMAIL_TO", "")
    sender = os.environ.get("SCAN_EMAIL_FROM", user)
    if not (user and password and to):
        raise SystemExit(
            "email requested but SCAN_SMTP_USERNAME, SCAN_SMTP_PASSWORD or "
            "SCAN_EMAIL_TO is unset; add them as repository secrets"
        )
    cids = {p.slug: f"chart-{p.slug}" for p in news if p.chart}
    message = EmailMessage()
    message["Subject"] = (f"AI discovery data: new results in {len(news)} "
                          f"series ({today})")
    message["From"] = sender
    message["To"] = to
    message.set_content(text_report(news, today))
    message.add_alternative(html_report(news, today, cids), subtype="html")
    html_part = message.get_payload()[1]
    for problem in news:
        if problem.chart:
            html_part.add_related(problem.chart.read_bytes(), maintype="image",
                                  subtype="png", cid=f"<{cids[problem.slug]}>")
    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)
    print(f"emailed {to}: {len(news)} series, "
          f"{sum(1 for p in news if p.chart)} charts")


def refresh_baseline(baseline_dir: Path) -> None:
    for path in sorted(ROOT.glob("problems/*/*.csv")):
        target = baseline_dir / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    print(f"baseline refreshed under {baseline_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--baseline", type=Path, default=None,
                        help="snapshot dir from the previous scan; kept in an "
                             "Actions cache and refreshed after a sent email")
    parser.add_argument("--charts", type=Path,
                        default=ROOT / "scan-charts",
                        help="where the email charts are written")
    parser.add_argument("--email", action="store_true",
                        help="send the digest over SMTP (env-configured)")
    args = parser.parse_args()

    today = os.environ.get("AI_DISCOVERY_AS_OF") or date.today().isoformat()
    news = scan(args.baseline)
    if not news:
        print("no new results since the last scan")
        if args.baseline:
            refresh_baseline(args.baseline)
        return

    for problem in in_domain_order(news)[:MAX_CHARTS]:
        problem.chart = draw_chart(problem, args.charts)

    report = text_report(news, today)
    print(report)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(f"```\n{report}\n```\n")

    if args.email:
        send_email(news, today)  # SystemExit on missing config keeps baseline
    if args.baseline:
        refresh_baseline(args.baseline)


if __name__ == "__main__":
    main()
