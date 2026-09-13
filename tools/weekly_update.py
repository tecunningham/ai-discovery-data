#!/usr/bin/env python3
"""Weekly refresh: refetch, rank what moved, and report how the repo was updated.

Driven by .github/workflows/weekly-update.yml, one subcommand per step so the
workflow can put its own decisions (open a PR, merge it) between them:

    python3 tools/weekly_update.py fetch        # every automatable fetcher, per-script status
    python3 tools/weekly_update.py scan         # diff the tree against HEAD; tier and chart it
    python3 tools/weekly_update.py bump-as-of   # move lib/dates.py's AS_OF_DATE to today
    python3 tools/weekly_update.py review       # after the prose pass: does this need a person?
    python3 tools/weekly_update.py pr-body      # the pull request description, on stdout
    python3 tools/weekly_update.py email        # the digest, over SMTP

Everything between steps lives under .weekly/ (gitignored): fetch.json,
news.json, review.json, the charts, and the judgment-calls.md the prose pass
writes when a change was more than arithmetic.

The prose pass has two homes. With a CLAUDE_CODE_OAUTH_TOKEN secret it runs
inside the Monday workflow. Without one the workflow opens the PR with the
prose still stale, a scheduled Claude Code session restates the facts and
pushes to the branch, and .github/workflows/refresh-finish.yml picks up that
push: `--base origin/main` makes scan and review see the whole branch rather
than the last commit, and it merges when the review allows.

The diff is against HEAD, not against a previous fetch. The nightly scan this
replaced kept its own baseline so that a series the repo had not caught up
with was reported once; now the repository catches up every week, so "what
changed since the last commit" is exactly the question, and a week whose PR
was held for review reports the same news again, which is right: it is still
news until it lands.

What the email leads with is decided by tiering each changed row:

    headline  a status flip (unsolved -> solved_ai), a new row in a record
              ledger, a new or changed AI credit, an is_record flip
    notable   any other change in a mathematics or algorithms series
    routine   count series ticking along: vulnerability tallies, arXiv and
              Crossref volumes, data_through dates advancing

Headline and notable series get a chart each; routine ones get one line at
the bottom. The chart is drawn with whatever matplotlib the runner has: it is
an email body, not a committed figure, so the pinned-renderer rule for
problems/*/figure.py does not apply and nothing here writes into a problem
folder.

Email is plain SMTP (STARTTLS), configured through the environment:

    SCAN_SMTP_HOST      default smtp.gmail.com
    SCAN_SMTP_PORT      default 587
    SCAN_SMTP_USERNAME  login, and the default From address
    SCAN_SMTP_PASSWORD  for Gmail this is an app password, not the account one
    SCAN_EMAIL_TO       recipient
    SCAN_EMAIL_FROM     optional, defaults to SCAN_SMTP_USERNAME

and the outcome the workflow reached comes in as UPDATE_OUTCOME (merged,
needs-review, unchanged, failed), with PR_URL and RUN_URL for the links.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import smtplib
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.dates import period_bounds  # noqa: E402  (matplotlib-free)
from lib.document import front_matter, title  # noqa: E402
from lib.palette import AI, UNATTRIBUTED  # noqa: E402

STATE = ROOT / ".weekly"
REPO_URL = "https://github.com/tecunningham/ai-discovery-data"

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

# An AI credit is a column named for it (ai_attributed, explicit_ai,
# ai_affiliated, unique_ai_affiliated, ai_involved, ai_system, corroborated_ai)
# or an "ai" value in a column that names who gets the credit.
AI_COL = re.compile(r"(^|_)ai($|_)")
CREDIT_COLS = ("credit", "attribution", "category", "band", "agent")
AI_VALUE = re.compile(r"(^|[^a-z])ai([^a-z]|$)|(^|_)ai($|_)")
FALSY = {"", "0", "0.0", "no", "none", "false", "n/a", "-"}

# A CSV with this many rows is a catalogue (a leaderboard, every CVE, every
# build); a new row there is a data point, not a record step.
LEDGER_MAX_ROWS = 200

MAX_LINES_PER_CSV = 8
MAX_CHARTS = 16
RECENT_PERIODS = 30

DOMAIN_ORDER = ("mathematics", "algorithms", "vulnerabilities",
                "outside the three domains")
TIERS = ("headline", "notable", "routine")

# The fetchers `make fetch` skips, for the same reasons the Makefile gives.
HAND_RUN_FETCHERS = {
    "problems/math-antedb/fetch.py",               # needs expdb and pycddlib<3
    "problems/math-alphaevolve-inventory/fetch.py",  # needs --paper-text and --repo
}


# ---------------------------------------------------------------- CSV diffing

def parse_rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    return list(fields), [dict(row) for row in reader]


# The commit the working tree is compared with. HEAD in the Monday run, where
# HEAD is main; origin/main in the finishing run, which checks out the refresh
# branch after the prose pass has been pushed to it (--base sets it).
BASE = "HEAD"


def committed_text(relpath: str) -> str:
    result = subprocess.run(["git", "show", f"{BASE}:{relpath}"],
                            capture_output=True, cwd=ROOT)
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


def is_ai_value(value: str) -> bool:
    return bool(AI_VALUE.search(value.strip().lower())) and \
        value.strip().lower() not in FALSY


def row_shows_ai(fields: list[str], row: dict[str, str]) -> bool:
    for col in fields:
        value = (row.get(col) or "").strip()
        if AI_COL.search(col) and value.lower() not in FALSY:
            return True
        if col in CREDIT_COLS and is_ai_value(value):
            return True
    return False


@dataclass
class Item:
    """One reported change: an added row, a revised row, or a dropped row."""
    text: str
    tier: str
    why: str


@dataclass
class CsvDiff:
    relpath: str
    fields: list[str]
    rows: list[dict[str, str]]
    added: list[dict[str, str]]
    removed: list[dict[str, str]]
    domain: str
    schema_changed: bool = False

    @property
    def name(self) -> str:
        return Path(self.relpath).name

    @property
    def is_ledger(self) -> bool:
        return len(self.rows) < LEDGER_MAX_ROWS and \
            not any(c in self.fields for c in VALUE_COLS)

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

    def _shown(self, row: dict[str, str]) -> str:
        return ", ".join(f"{k}={row[k]}" for k in self.fields
                         if (row.get(k) or "").strip())[:5 * 40]

    def tier_of_revision(self, old: dict[str, str], new: dict[str, str],
                         changed: list[str]) -> tuple[str, str]:
        if "status" in changed:
            return "headline", f"status {old.get('status')} → {new.get('status')}"
        if "is_record" in changed:
            return "headline", "record flag changed"
        for col in changed:
            if AI_COL.search(col) or (col in CREDIT_COLS and (
                    is_ai_value(old.get(col, "")) or is_ai_value(new.get(col, "")))):
                return "headline", f"AI credit column {col} changed"
        if self.domain in ("mathematics", "algorithms"):
            return "notable", "revision in a mathematics/algorithms series"
        return "routine", "count revision"

    def tier_of_addition(self, row: dict[str, str]) -> tuple[str, str]:
        if "-ai-" in self.name:
            return "headline", "new AI-credited entry"
        if row_shows_ai(self.fields, row):
            return "headline", "new row carrying an AI credit"
        if self.domain in ("mathematics", "algorithms"):
            if self.is_ledger:
                return "headline", "new entry in a record ledger"
            return "notable", "new row in a mathematics/algorithms table"
        return "routine", "new period or finder row"

    def items(self) -> list[Item]:
        """Human summary, pairing a revised row with its previous version.

        A count CSV revises a period by replacing its row, which the multiset
        diff sees as one removal plus one addition; showing "2025-Q3: total
        12 → 14" instead of two full rows is the difference between an email
        and a diff dump. The same pairing shows a ledger resolution as one
        status change on the named problem.
        """
        if self.schema_changed:
            return [Item(f"{self.name}: column layout changed — see the "
                         "repository", "notable", "schema changed")]
        out: list[Item] = []
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
                changed = [k for k in self.fields if old.get(k) != row.get(k)]
                shown = [f"{k} {old.get(k) or '(empty)'} → {row.get(k) or '(empty)'}"
                         for k in changed][:4]
                tier, why = self.tier_of_revision(old, row, changed)
                out.append(Item(f"{self.label(row)}: " + ", ".join(shown), tier, why))
            else:
                tier, why = self.tier_of_addition(row)
                out.append(Item("new — " + self._shown(row), tier, why))
        for row in removed_left:
            tier = "notable" if self.domain in ("mathematics", "algorithms") \
                else "routine"
            out.append(Item("dropped — " + self._shown(row), tier, "row dropped"))
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
    chart: str | None = None

    @property
    def tier(self) -> str:
        tiers = [item.tier for d in self.diffs for item in d.items()]
        return min(tiers, key=TIERS.index) if tiers else "routine"

    @property
    def url(self) -> str:
        return f"{REPO_URL}/tree/main/problems/{self.slug}/"


def diff_csv(relpath: str, domain: str) -> CsvDiff | None:
    current = (ROOT / relpath).read_text(encoding="utf-8")
    old_text = committed_text(relpath)
    if current == old_text:
        return None
    fields, rows = parse_rows(current)
    old_fields, old_rows = parse_rows(old_text)
    if old_text and old_fields != fields:
        return CsvDiff(relpath, fields, rows, [], [], domain, schema_changed=True)

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
    return CsvDiff(relpath, fields, rows, added, removed, domain)


def scan_tree() -> list[ProblemNews]:
    news: dict[str, ProblemNews] = {}
    for path in sorted(ROOT.glob("problems/*/*.csv")):
        slug = path.parent.name
        readme = path.parent / "README.md"
        text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        domain = front_matter(text).get("Domain", "other").lower()
        diff = diff_csv(path.relative_to(ROOT).as_posix(), domain)
        if diff is None:
            continue
        if slug not in news:
            news[slug] = ProblemNews(slug=slug, title=title(text) or slug,
                                     domain=domain)
        news[slug].diffs.append(diff)
    return list(news.values())


def ordered(news: list[ProblemNews]) -> list[ProblemNews]:
    rank = {d: i for i, d in enumerate(DOMAIN_ORDER)}
    return sorted(news, key=lambda p: (TIERS.index(p.tier),
                                       rank.get(p.domain, len(rank)), p.slug))


# ---------------------------------------------------------------- charts

def chartable(diff: CsvDiff) -> bool:
    return not diff.schema_changed and time_col(diff.fields) is not None


def draw_chart(problem: ProblemNews, out_dir: Path) -> Path | None:
    """One bar chart: the series' recent window, changed periods in red.

    Muted slate carries the context and the AI red carries "new since the
    last commit"; identity is doubled by the legend and by the value printed
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
    ax.legend(handles, ["already committed", "new or revised this week"],
              frameon=False, fontsize=8, loc="upper left")
    ax.text(0.0, -0.24, f"Source: {diff.name}", transform=ax.transAxes,
            fontsize=7.5, color="#888888")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"scan-{problem.slug}.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# ---------------------------------------------------------------- state files

def read_json(name: str, default):
    path = STATE / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, data) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False),
                              encoding="utf-8")


def github_output(**values: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def step_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(markdown + "\n")


def news_to_json(news: list[ProblemNews]) -> list[dict]:
    out = []
    for problem in ordered(news):
        out.append({
            "slug": problem.slug, "title": problem.title,
            "domain": problem.domain, "tier": problem.tier,
            "chart": problem.chart,
            "diffs": [{
                "name": d.name, "relpath": d.relpath,
                "items": [asdict(i) for i in d.items()],
            } for d in problem.diffs],
        })
    return out


# ---------------------------------------------------------------- subcommands

def cmd_fetch(args: argparse.Namespace) -> int:
    """Run every automatable fetcher, recording which ones failed.

    The Makefile's `fetch` target runs the same scripts; this runs them one
    at a time so the digest can say *which* upstream was unreachable, which
    the aggregate exit status cannot. Exit status is 0 regardless: several
    upstreams rate-limit or go down, and a transient failure is not news.
    A CSV a failed fetcher left untouched simply matches HEAD.
    """
    results = []
    for script in sorted(ROOT.glob("problems/*/fetch.py")):
        rel = script.relative_to(ROOT).as_posix()
        if rel in HAND_RUN_FETCHERS:
            continue
        print(f"== {rel}", flush=True)
        started = time.time()
        run = subprocess.run([sys.executable, str(script)], cwd=ROOT,
                             capture_output=True, text=True)
        tail = "\n".join((run.stdout + run.stderr).strip().splitlines()[-6:])
        print(tail, flush=True)
        results.append({
            "script": rel, "slug": script.parent.name,
            "ok": run.returncode == 0, "seconds": round(time.time() - started),
            "tail": tail,
        })
    write_json("fetch.json", results)
    failed = [r["slug"] for r in results if not r["ok"]]
    print(f"{len(results)} fetchers ran; failed: {', '.join(failed) or 'none'}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    news = scan_tree()
    if not news:
        write_json("news.json", [])
        github_output(changed="false", headline="0")
        print("no vendored CSV differs from HEAD")
        step_summary("No upstream changes since the last commit.")
        return 0
    charts = STATE / "charts"
    for problem in [p for p in ordered(news) if p.tier != "routine"][:MAX_CHARTS]:
        path = draw_chart(problem, charts)
        problem.chart = path.relative_to(ROOT).as_posix() if path else None
    data = news_to_json(news)
    write_json("news.json", data)
    headline = sum(1 for p in data if p["tier"] == "headline")
    github_output(changed="true", headline=str(headline))
    digest = digest_markdown(data)
    (STATE / "digest.md").write_text(digest, encoding="utf-8")
    print(digest)
    step_summary(digest)
    return 0


def cmd_bump_as_of(args: argparse.Namespace) -> int:
    """Set AS_OF_DATE to today, the date the fetchers were told to clip at.

    The fetch step runs with AI_DISCOVERY_AS_OF=today so the fetchers that
    clip at the snapshot date see this week's rows; committing that data
    means the committed date has to move to the same day, or tools/check.py
    rejects the CSVs as newer than the snapshot.
    """
    today = os.environ.get("AI_DISCOVERY_AS_OF") or date.today().isoformat()
    path = ROOT / "lib" / "dates.py"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"else date\((\d{4}), (\d{1,2}), (\d{1,2})\)")
    match = pattern.search(text)
    if not match:
        raise SystemExit("lib/dates.py: could not find the AS_OF_DATE literal")
    old = date(*map(int, match.groups()))
    new = date.fromisoformat(today)
    if new < old:
        raise SystemExit(f"refusing to move AS_OF_DATE backwards: {old} -> {new}")
    text = pattern.sub(f"else date({new.year}, {new.month}, {new.day})", text)
    path.write_text(text, encoding="utf-8")
    write_json("as_of.json", {"old": old.isoformat(), "new": new.isoformat()})
    print(f"AS_OF_DATE {old} -> {new}")
    return 0


# Files the pipeline is allowed to have changed by the time the PR opens. The
# fetch writes CSVs, bump-as-of writes lib/dates.py, the prose pass writes
# folder READMEs, and the render writes PNGs, docs and the generated tables.
ALLOWED_CHANGES = (
    re.compile(r"^problems/[^/]+/[^/]+\.csv$"),
    re.compile(r"^problems/[^/]+/README\.md$"),
    re.compile(r"^problems/[^/]+/[^/]+\.png$"),
    re.compile(r"^lib/dates\.py$"),
    re.compile(r"^(README|CUMULATIVE)\.md$"),
    re.compile(r"^docs/.*"),
)


def changed_paths() -> list[str]:
    """Every path that differs from BASE: committed on the branch or not."""
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True, cwd=ROOT, check=True).stdout
    # A rename prints "old -> new"; the new path is the one that exists.
    paths = {line[3:].split(" -> ")[-1].strip()
             for line in status.splitlines() if line.strip()}
    if BASE != "HEAD":
        diff = subprocess.run(["git", "diff", "--name-only", BASE],
                              capture_output=True, text=True, cwd=ROOT, check=True).stdout
        paths.update(line.strip() for line in diff.splitlines() if line.strip())
    return sorted(paths)


def verdict_term(text: str) -> str:
    return front_matter(text).get("Verdict", "").split(" —")[0].strip()


def cmd_review(args: argparse.Namespace) -> int:
    """Decide whether the refresh can merge on its own.

    Anything that is not arithmetic holds the PR for a person: a Verdict
    whose controlled term changed, a note the prose pass left in
    judgment-calls.md, a file outside the pipeline's remit, or a failing
    check. The reasons are written for the PR body and the email.
    """
    reasons: list[str] = []
    for path in changed_paths():
        if path.startswith(".weekly/"):
            continue
        if not any(p.match(path) for p in ALLOWED_CHANGES):
            reasons.append(f"unexpected file changed: `{path}`")
    for readme in sorted(ROOT.glob("problems/*/README.md")):
        rel = readme.relative_to(ROOT).as_posix()
        before = verdict_term(committed_text(rel))
        after = verdict_term(readme.read_text(encoding="utf-8"))
        if before and after and before != after:
            reasons.append(f"{readme.parent.name}: Verdict moved from "
                           f"“{before}” to “{after}”")
    notes = STATE / "judgment-calls.md"
    judgment = notes.read_text(encoding="utf-8").strip() if notes.exists() else ""
    if BASE != "HEAD":
        # A prose pass made outside the workflow has no .weekly/ to write
        # into; it reports judgment calls in its commit message, under a
        # "Judgment calls:" line, which the branch carries to this run.
        log = subprocess.run(["git", "log", "--format=%B%x00", f"{BASE}..HEAD"],
                             capture_output=True, text=True, cwd=ROOT).stdout
        for body in log.split("\0"):
            _, marker, tail = body.partition("Judgment calls:")
            if marker and tail.strip():
                judgment = (judgment + "\n\n" + tail.strip()).strip()
    if judgment:
        reasons.append("the prose pass flagged judgment calls (below)")
    for step in args.failed or []:
        reasons.append(f"the {step} step failed; see the workflow run")
    reasons.extend(args.reason or [])
    if args.check_failed:
        log = Path(args.check_log).read_text(encoding="utf-8") \
            if args.check_log and Path(args.check_log).exists() else ""
        failing = [line for line in log.splitlines()
                   if line.startswith(("FAIL", "ERROR")) or ": " in line][-30:]
        reasons.append("the checks failed:\n```\n"
                       + "\n".join(failing or log.splitlines()[-30:]
                                   or ["no log captured"]) + "\n```")
    review = {
        "hold": bool(reasons),
        "reasons": reasons,
        "judgment_calls": judgment,
    }
    write_json("review.json", review)
    github_output(hold="true" if reasons else "false")
    print("hold for review" if reasons else "safe to merge")
    for reason in reasons:
        print(f"- {reason.splitlines()[0]}")
    return 0


# ---------------------------------------------------------------- reporting

def fetch_failures() -> list[dict]:
    return [r for r in read_json("fetch.json", []) if not r["ok"]]


def digest_markdown(news: list[dict]) -> str:
    out = []
    for tier, heading in (("headline", "Headline findings"),
                          ("notable", "Also moved"),
                          ("routine", "Routine updates")):
        group = [p for p in news if p["tier"] == tier]
        if not group:
            continue
        out += [f"### {heading}", ""]
        for problem in group:
            out.append(f"- **{problem['title']}** ({problem['slug']}, "
                       f"{problem['domain']})")
            limit = MAX_LINES_PER_CSV if tier != "routine" else 2
            for diff in problem["diffs"]:
                items = diff["items"]
                for item in items[:limit]:
                    out.append(f"    - `{diff['name']}` — {item['text']}")
                if len(items) > limit:
                    out.append(f"    - `{diff['name']}` — … and "
                               f"{len(items) - limit} more")
        out.append("")
    failed = fetch_failures()
    if failed:
        out += ["### Fetchers that failed", ""]
        out += [f"- `{r['script']}` — {r['tail'].splitlines()[-1] if r['tail'] else 'no output'}"
                for r in failed]
        out.append("")
    return "\n".join(out).strip() + "\n"


def cmd_pr_body(args: argparse.Namespace) -> int:
    news = read_json("news.json", [])
    review = read_json("review.json", {"hold": False, "reasons": [], "judgment_calls": ""})
    as_of = read_json("as_of.json", {})
    out = ["Weekly refresh by the "
           f"[weekly-update workflow]({REPO_URL}/actions/workflows/weekly-update.yml): "
           "`make fetch`, prose brought back in line with the data, then "
           "`make figures`, `make index` and `make docs`."]
    if as_of:
        out.append(f"`AS_OF_DATE` {as_of['old']} → {as_of['new']}.")
    out.append("")
    if review["hold"]:
        out += ["## Needs a person", ""]
        out += [f"- {reason}" for reason in review["reasons"]]
        out.append("")
        if review["judgment_calls"]:
            out += ["### Judgment calls recorded by the prose pass", "",
                    review["judgment_calls"], ""]
    else:
        out += ["Every change is arithmetic and every check passes; merged "
                "automatically.", ""]
    out.append(digest_markdown(news))
    run_url = os.environ.get("RUN_URL")
    if run_url:
        out.append(f"\nCharts and logs: [workflow run]({run_url}).")
    print("\n".join(out))
    return 0


def esc(text: str) -> str:
    # Quotes included: escaped text also lands in attributes (img alt).
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;"))


def status_text(outcome: str, review: dict, pr_url: str, run_url: str) -> tuple[str, str]:
    """(plain, html) for the box at the top of the email."""
    if outcome == "merged":
        plain = f"Repository updated: the refresh PR was merged. {pr_url}"
        html = (f"<b>Repository updated.</b> The refresh "
                f"<a href='{esc(pr_url)}'>pull request</a> passed every check "
                "and was merged.")
    elif outcome == "needs-review":
        why = review.get("reasons") or [
            "nothing needed a judgment call, but the merge was switched off "
            "or did not go through; merge it yourself"]
        plain = ("SIGN-OFF NEEDED: the refresh PR is open and waiting for you. "
                 f"{pr_url}\n" + "\n".join(f"  - {r.splitlines()[0]}" for r in why))
        html = (f"<b>Sign-off needed.</b> The refresh "
                f"<a href='{esc(pr_url)}'>pull request</a> is open and waiting "
                "for you:<ul style='margin:4px 0'>"
                + "".join(f"<li>{esc(r.splitlines()[0])}</li>" for r in why)
                + "</ul>")
        if review.get("judgment_calls"):
            plain += "\n\nJudgment calls recorded:\n" + review["judgment_calls"]
            html += ("<p style='margin:4px 0'><b>Judgment calls recorded:</b></p>"
                     f"<pre style='white-space:pre-wrap;font-size:12px'>"
                     f"{esc(review['judgment_calls'])}</pre>")
    elif outcome == "unchanged":
        plain = "No upstream changes since the last commit; nothing to update."
        html = "<b>No upstream changes</b> since the last commit; nothing to update."
    else:
        plain = f"The refresh FAILED before it could open a PR. See the run: {run_url}"
        html = (f"<b>The refresh failed</b> before it could open a PR. See the "
                f"<a href='{esc(run_url)}'>workflow run</a>.")
    if run_url and outcome != "failed":
        html += f" <a href='{esc(run_url)}' style='color:#888'>(run)</a>"
    return plain, html


def text_report(news: list[dict], today: str, outcome: str, review: dict,
                pr_url: str, run_url: str) -> str:
    plain, _ = status_text(outcome, review, pr_url, run_url)
    out = [f"AI discovery data — week of {today}", "", plain, ""]
    for tier, heading in (("headline", "HEADLINE FINDINGS"),
                          ("notable", "ALSO MOVED"),
                          ("routine", "ROUTINE UPDATES")):
        group = [p for p in news if p["tier"] == tier]
        if not group:
            continue
        out += [heading, ""]
        limit = MAX_LINES_PER_CSV if tier != "routine" else 2
        for problem in group:
            out.append(f"* {problem['title']} ({problem['slug']})")
            for diff in problem["diffs"]:
                items = diff["items"]
                for item in items[:limit]:
                    out.append(f"    {diff['name']} — {item['text']}")
                if len(items) > limit:
                    out.append(f"    {diff['name']} — … and {len(items) - limit} more")
            out.append("")
    failed = fetch_failures()
    if failed:
        out += ["FETCHERS THAT FAILED (series not refreshed this week)", ""]
        out += [f"* {r['slug']}: {r['tail'].splitlines()[-1] if r['tail'] else 'no output'}"
                for r in failed]
        out.append("")
    links = STATE / "links.log"
    if links.exists() and links.read_text(encoding="utf-8").strip():
        out += ["DOCUMENTED URLS THAT DID NOT RESOLVE", "",
                links.read_text(encoding="utf-8").strip(), ""]
    return "\n".join(out)


def html_report(news: list[dict], today: str, cids: dict[str, str],
                outcome: str, review: dict, pr_url: str, run_url: str) -> str:
    _, status_html = status_text(outcome, review, pr_url, run_url)
    tone = {"merged": "#e8f4ea", "needs-review": "#fff4d6",
            "unchanged": "#f1f1f1", "failed": "#fbe3e3"}.get(outcome, "#f1f1f1")
    out = [
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,'
        'sans-serif;max-width:680px;color:#1a1a1a">',
        f"<h2 style='margin-bottom:2px'>AI discovery data — week of {esc(today)}</h2>",
        f"<div style='background:{tone};padding:10px 12px;border-radius:6px;"
        f"font-size:14px;margin:8px 0 16px'>{status_html}</div>",
    ]

    def problem_block(problem: dict, limit: int, with_chart: bool) -> None:
        out.append(f"<h4 style='margin:10px 0 4px'>"
                   f"<a href='{REPO_URL}/tree/main/problems/{problem['slug']}/' "
                   f"style='color:#1a1a1a'>{esc(problem['title'])}</a> "
                   f"<span style='color:#888;font-weight:normal;font-size:12px'>"
                   f"{esc(problem['domain'])}</span></h4>")
        out.append("<ul style='margin-top:2px'>")
        for diff in problem["diffs"]:
            items = diff["items"]
            for item in items[:limit]:
                out.append(f"<li style='font-size:13px'><code>{esc(diff['name'])}"
                           f"</code> — {esc(item['text'])}</li>")
            if len(items) > limit:
                out.append(f"<li style='font-size:13px;color:#666'>… and "
                           f"{len(items) - limit} more in "
                           f"<code>{esc(diff['name'])}</code></li>")
        out.append("</ul>")
        if with_chart and problem["slug"] in cids:
            out.append(f"<img src='cid:{cids[problem['slug']]}' width='640' "
                       f"alt='Recent series for {esc(problem['title'])}, changed "
                       f"periods highlighted' style='max-width:100%;height:auto'>")

    headline = [p for p in news if p["tier"] == "headline"]
    notable = [p for p in news if p["tier"] == "notable"]
    routine = [p for p in news if p["tier"] == "routine"]
    if headline:
        out.append("<h3 style='border-bottom:2px solid #1a1a1a;padding-bottom:3px'>"
                   "Headline findings</h3>")
        for problem in headline:
            problem_block(problem, MAX_LINES_PER_CSV, True)
    if notable:
        out.append("<h3 style='border-bottom:1px solid #ddd;padding-bottom:3px'>"
                   "Also moved</h3>")
        for problem in notable:
            problem_block(problem, MAX_LINES_PER_CSV, True)
    if routine:
        out.append("<h3 style='border-bottom:1px solid #ddd;padding-bottom:3px;"
                   "color:#666'>Routine updates</h3>")
        out.append("<p style='color:#666;font-size:12px;margin-top:0'>Count "
                   "series ticking along: no status, record or AI-credit change.</p>")
        out.append("<ul style='font-size:12.5px;color:#444'>")
        for problem in routine:
            first = next((i["text"] for d in problem["diffs"] for i in d["items"]), "")
            total = sum(len(d["items"]) for d in problem["diffs"])
            more = f" <span style='color:#888'>(+{total - 1} more)</span>" if total > 1 else ""
            out.append(f"<li><a href='{REPO_URL}/tree/main/problems/{problem['slug']}/' "
                       f"style='color:#444'>{esc(problem['title'])}</a>: "
                       f"{esc(first)}{more}</li>")
        out.append("</ul>")
    if not news:
        out.append("<p style='color:#666'>No series changed.</p>")
    failed = fetch_failures()
    if failed:
        out.append("<h3 style='border-bottom:1px solid #ddd;padding-bottom:3px;"
                   "color:#666'>Fetchers that failed</h3>")
        out.append("<p style='color:#666;font-size:12px;margin-top:0'>These "
                   "series were not refreshed this week.</p>")
        out.append("<ul style='font-size:12.5px;color:#444'>")
        out += [f"<li><code>{esc(r['slug'])}</code>: "
                f"{esc(r['tail'].splitlines()[-1] if r['tail'] else 'no output')}</li>"
                for r in failed]
        out.append("</ul>")
    links = STATE / "links.log"
    if links.exists() and links.read_text(encoding="utf-8").strip():
        out.append("<h3 style='border-bottom:1px solid #ddd;padding-bottom:3px;"
                   "color:#666'>Documented URLs that did not resolve</h3>")
        out.append(f"<pre style='font-size:11.5px;color:#444;white-space:pre-wrap'>"
                   f"{esc(links.read_text(encoding='utf-8').strip())}</pre>")
    out.append("<p style='color:#888;font-size:12px'>Sent by the "
               f"<a href='{REPO_URL}/actions/workflows/weekly-update.yml'>"
               "weekly-update workflow</a>. Charts compare this week's fetch "
               "with the previously committed data.</p></div>")
    return "\n".join(out)


def cmd_email(args: argparse.Namespace) -> int:
    news = read_json("news.json", [])
    review = read_json("review.json", {"hold": False, "reasons": [], "judgment_calls": ""})
    outcome = os.environ.get("UPDATE_OUTCOME", "failed")
    pr_url = os.environ.get("PR_URL", "")
    run_url = os.environ.get("RUN_URL", "")
    today = os.environ.get("AI_DISCOVERY_AS_OF") or date.today().isoformat()

    headline = sum(1 for p in news if p["tier"] == "headline")
    notable = sum(1 for p in news if p["tier"] == "notable")
    what = (f"{headline} headline finding{'s' if headline != 1 else ''}"
            if headline else
            f"{notable} series moved" if notable else
            f"{len(news)} routine update{'s' if len(news) != 1 else ''}"
            if news else "no upstream changes")
    prefix = {"needs-review": "[sign-off needed] ", "failed": "[failed] "}.get(outcome, "")
    subject = f"{prefix}AI discovery weekly: {what} ({today})"

    cids = {p["slug"]: f"chart-{p['slug']}" for p in news if p.get("chart")}
    text = text_report(news, today, outcome, review, pr_url, run_url)
    html = html_report(news, today, cids, outcome, review, pr_url, run_url)
    if args.dry_run:
        Path(args.dry_run).mkdir(parents=True, exist_ok=True)
        (Path(args.dry_run) / "email.txt").write_text(f"Subject: {subject}\n\n{text}",
                                                       encoding="utf-8")
        html_file = html
        for problem in news:
            if problem.get("chart"):
                html_file = html_file.replace(f"cid:{cids[problem['slug']]}",
                                              str(ROOT / problem["chart"]))
        (Path(args.dry_run) / "email.html").write_text(html_file, encoding="utf-8")
        print(f"Subject: {subject}\n\n{text}")
        return 0

    host = os.environ.get("SCAN_SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SCAN_SMTP_PORT", "587"))
    user = os.environ.get("SCAN_SMTP_USERNAME", "")
    password = os.environ.get("SCAN_SMTP_PASSWORD", "")
    to = os.environ.get("SCAN_EMAIL_TO", "")
    sender = os.environ.get("SCAN_EMAIL_FROM", user)
    if not (user and password and to):
        raise SystemExit(
            "SCAN_SMTP_USERNAME, SCAN_SMTP_PASSWORD or SCAN_EMAIL_TO is unset; "
            "add them as repository secrets / variables"
        )
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to
    message.set_content(text)
    message.add_alternative(html, subtype="html")
    html_part = message.get_payload()[1]
    for problem in news:
        if problem.get("chart"):
            html_part.add_related((ROOT / problem["chart"]).read_bytes(),
                                  maintype="image", subtype="png",
                                  cid=f"<{cids[problem['slug']]}>")
    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)
    print(f"emailed {to}: {subject}")
    return 0


def main() -> int:
    global BASE
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base", default="HEAD", metavar="REF",
                        help="commit to compare the tree with (default HEAD; "
                             "the finishing run passes origin/main)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch", help="run every automatable fetcher").set_defaults(func=cmd_fetch)
    sub.add_parser("scan", help="diff the tree against the base, tier and chart").set_defaults(func=cmd_scan)
    sub.add_parser("bump-as-of", help="move AS_OF_DATE to today").set_defaults(func=cmd_bump_as_of)
    review = sub.add_parser("review", help="decide whether a person is needed")
    review.add_argument("--check-log", help="output of make index / check-figures")
    review.add_argument("--check-failed", action="store_true",
                        help="the check exited non-zero")
    review.add_argument("--failed", action="append", metavar="STEP",
                        help="an earlier step that failed (repeatable)")
    review.add_argument("--reason", action="append", metavar="TEXT",
                        help="a further reason to hold the PR (repeatable)")
    review.set_defaults(func=cmd_review)
    sub.add_parser("pr-body", help="print the PR description").set_defaults(func=cmd_pr_body)
    email = sub.add_parser("email", help="send the digest")
    email.add_argument("--dry-run", metavar="DIR",
                       help="write email.txt and email.html to DIR instead of sending")
    email.set_defaults(func=cmd_email)
    args = parser.parse_args()
    BASE = args.base
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
