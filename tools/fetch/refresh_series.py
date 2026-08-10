#!/usr/bin/env python3
"""Refetch the living time-series CSVs and report drift against the vendored copies.

    python3 tools/refresh_series.py                # fetch everything, report only
    python3 tools/refresh_series.py arxiv github   # just these series
    python3 tools/refresh_series.py --write        # update the vendored CSVs in place
    python3 tools/refresh_series.py --probe-only   # only the cheap staleness probes

Why this exists. Several entries in the apple-picking source log quote figures
from series that keep moving — arXiv submissions, Stack Overflow questions,
GitHub pushes, solver and speedrun records. The claims auditor
(tools/audit_claims.py) catches prose that drifted from a vendored CSV, but
nothing catches a vendored CSV that drifted from the world. This script closes
that gap: it refetches each series from the same primary source the entry
names, diffs against the vendored file, and reports. After --write, run

    python3 tools/audit_claims.py

to see which prose claims the new data invalidates — that is the intended
workflow, not a bug: the CSV moves first, then the prose is re-checked.

Two tiers:
- FETCHERS rebuild a series completely from the source (arxiv, crossref,
  stackoverflow, github).
- PROBES only detect staleness for series whose sources need judgment to
  transcribe (nanogpt README, nextchessmove dev builds, the Hutter Prize
  page). A probe never writes; it tells you to update by hand, because those
  entries record authorship and caveats no parser should guess at.

Stdlib only; no dependencies.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
UA = {"User-Agent": "tecunningham.github.io refresh_series (tom.cunningham@metr.org)"}


def get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def read_vendored(name: str) -> list[dict]:
    path = DATA / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def diff_report(name: str, old: list[dict], new: list[dict], key: str) -> bool:
    """Print what changed; return True if anything did."""
    old_by = {r[key]: r for r in old}
    new_by = {r[key]: r for r in new}
    added = [k for k in new_by if k not in old_by]
    removed = [k for k in old_by if k not in new_by]
    changed = [k for k in new_by if k in old_by and new_by[k] != old_by[k]]
    if not (added or removed or changed):
        print(f"  {name}: unchanged ({len(new)} rows)")
        return False
    print(f"  {name}: {len(added)} added, {len(changed)} changed, "
          f"{len(removed)} removed (of {len(new)} rows)")
    for k in added[:5]:
        print(f"    + {k}: {new_by[k]}")
    for k in changed[:5]:
        print(f"    ~ {k}: {old_by[k]} -> {new_by[k]}")
    for k in removed[:5]:
        print(f"    - {k}")
    return True


def write_csv(name: str, fieldnames: list[str], rows: list[dict]) -> None:
    with (DATA / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {name}")


# --------------------------------------------------------------------------
# Full fetchers
# --------------------------------------------------------------------------
def fetch_arxiv() -> tuple[str, list[str], list[dict]]:
    """arXiv monthly submissions, from arXiv's own stats download."""
    raw = get("https://arxiv.org/stats/get_monthly_submissions").decode("utf-8")
    rows = []
    for r in csv.DictReader(io.StringIO(raw)):
        # raw columns: month, submissions, historical_delta (dropped, per entry)
        rows.append({"month": r["month"], "submissions": r["submissions"]})
    return "arxiv-monthly.csv", ["month", "submissions"], rows


def fetch_crossref() -> tuple[str, list[str], list[dict]]:
    """DOI records by created (deposit) year, one rows=0 count per year."""
    import datetime as dt
    this_year = dt.date.today().year
    rows = []
    for year in range(2010, this_year + 1):
        url = ("https://api.crossref.org/works?filter="
               f"from-created-date:{year}-01-01,until-created-date:{year}-12-31"
               "&rows=0&mailto=tom.cunningham@metr.org")
        total = json.loads(get(url))["message"]["total-results"]
        note = f"YTD through {dt.date.today()}" if year == this_year else ""
        rows.append({"year": str(year), "dois_created": str(total), "note": note})
        time.sleep(1.5)
    return "crossref-dois-by-year.csv", ["year", "dois_created", "note"], rows


def fetch_stackoverflow() -> tuple[str, list[str], list[dict]]:
    """Surviving questions by creation month, via the Stack Exchange API."""
    import calendar
    import datetime as dt
    today = dt.date.today()
    rows = []
    year, month = 2019, 1
    while (year, month) < (today.year, today.month):  # full months only
        start = int(dt.datetime(year, month, 1,
                                tzinfo=dt.timezone.utc).timestamp())
        last = calendar.monthrange(year, month)[1]
        end = int(dt.datetime(year, month, last, 23, 59, 59,
                              tzinfo=dt.timezone.utc).timestamp())
        url = ("https://api.stackexchange.com/2.3/questions?site=stackoverflow"
               f"&fromdate={start}&todate={end}&filter=total")
        payload = json.loads(get(url))
        rows.append({"month": f"{year}-{month:02d}",
                     "questions": str(payload["total"])})
        if payload.get("backoff"):
            time.sleep(payload["backoff"])
        time.sleep(0.3)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return "stackoverflow-questions-monthly.csv", ["month", "questions"], rows


def fetch_github() -> tuple[str, list[str], list[dict]]:
    """Innovation Graph quarterly totals, summed over economies, EU row excluded."""
    base = "https://raw.githubusercontent.com/github/innovationgraph/main/data"
    sums: dict[str, dict[str, int]] = {}
    for metric, column in (("git_pushes", "git_pushes"),
                           ("repositories", "repositories"),
                           ("developers", "developers")):
        raw = get(f"{base}/{metric}.csv").decode("utf-8")
        for r in csv.DictReader(io.StringIO(raw)):
            if r.get("iso2") == "EU":  # aggregate of member states
                continue
            q = f"{r['year']}-Q{r['quarter']}"
            sums.setdefault(q, {})
            sums[q][column] = sums[q].get(column, 0) + int(r[column])
    note = ("sum over economies in github/innovationgraph data (EU aggregate row "
            "excluded); economies below 100-developer reporting threshold not included")
    rows = [{"quarter": q, "git_pushes": str(v.get("git_pushes", "")),
             "repositories": str(v.get("repositories", "")),
             "developers": str(v.get("developers", "")), "note": note}
            for q, v in sorted(sums.items())]
    return ("github-innovationgraph-global.csv",
            ["quarter", "git_pushes", "repositories", "developers", "note"], rows)


FETCHERS = {
    "arxiv": (fetch_arxiv, "month"),
    "crossref": (fetch_crossref, "year"),
    "stackoverflow": (fetch_stackoverflow, "month"),
    "github": (fetch_github, "quarter"),
}


# --------------------------------------------------------------------------
# Staleness probes: detect that a hand-transcribed series has moved, without
# trying to parse authorship or caveats automatically.
# --------------------------------------------------------------------------
def probe_nanogpt() -> str | None:
    vendored = read_vendored("nanogpt-records.csv")
    last_n = int(vendored[-1]["record"]) if vendored else 0
    last_minutes = vendored[-1]["minutes"] if vendored else "?"
    text = get("https://raw.githubusercontent.com/KellerJordan/modded-nanogpt/"
               "master/README.md").decode("utf-8", errors="replace")
    # Record rows look like: "86 | 1.266 minutes | <description> | 05/27/26 | ..."
    rows = re.findall(r"(?m)^(\d+) \| ([\d.]+) minutes \|", text)
    if not rows:
        return ("nanogpt-records.csv: no record-table rows parsed from the "
                "README — its format changed; check by hand")
    newest_n, newest_minutes = max((int(n), m) for n, m in rows)
    if newest_n > last_n:
        return (f"nanogpt-records.csv: README now has record {newest_n} at "
                f"{newest_minutes} min; vendored series ends at record {last_n} "
                f"({last_minutes} min) — update the CSV and the #src-nanogpt "
                "entry by hand (authorship needs judgment)")
    return None


def probe_stockfish() -> str | None:
    vendored = read_vendored("stockfish-ncm-elo.csv")
    last_date = vendored[-1]["date"] if vendored else "?"
    text = get("https://nextchessmove.com/dev-builds").decode("utf-8", errors="replace")
    dates = re.findall(r"\b(20\d\d-\d\d-\d\d)", text)
    newest = max(dates) if dates else None
    if newest and newest > last_date:
        return (f"stockfish-ncm-elo.csv: newest build on the page is {newest}, "
                f"vendored series ends {last_date} — re-extract the dev-builds "
                "data array and re-vendor")
    if not dates:
        return ("stockfish-ncm-elo.csv: could not find dates on the page — "
                "page format may have changed; check by hand")
    return None


def probe_hutter() -> str | None:
    vendored = [r for r in read_vendored("compression-records.csv")
                if r["series"] == "hutter_enwik9" and r["award"] == "yes"]
    record = vendored[-1]["total_bytes"] if vendored else "?"
    # the prize site's TLS certificate is expired; it is read over plain HTTP
    text = get("http://prize.hutter1.net/").decode("utf-8", errors="replace")
    pretty = f"{int(record):,}".replace(",", "'")
    if record not in text.replace("'", "").replace(",", "") and pretty not in text:
        return (f"compression-records.csv: vendored record {record} bytes no longer "
                "on the prize page — a new record was likely awarded; update the CSV "
                "and the #src-compression-records entry by hand")
    return None


PROBES = {
    "nanogpt": probe_nanogpt,
    "stockfish": probe_stockfish,
    "hutter": probe_hutter,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series", nargs="*",
                        help=f"which to refresh (default all): {', '.join(FETCHERS)}")
    parser.add_argument("--write", action="store_true",
                        help="update the vendored CSVs in place")
    parser.add_argument("--probe-only", action="store_true",
                        help="only run the staleness probes")
    args = parser.parse_args()

    drift = False
    if not args.probe_only:
        names = args.series or list(FETCHERS)
        for name in names:
            if name not in FETCHERS:
                print(f"unknown series {name!r}; know: {', '.join(FETCHERS)}")
                return 2
            fetcher, key = FETCHERS[name]
            print(f"fetching {name} …")
            try:
                fname, fields, rows = fetcher()
            except Exception as exc:
                print(f"  FAILED: {exc}")
                drift = True
                continue
            changed = diff_report(fname, read_vendored(fname), rows, key)
            drift = drift or changed
            if changed and args.write:
                write_csv(fname, fields, rows)

    print("probes:")
    for name, probe in PROBES.items():
        try:
            message = probe()
        except Exception as exc:
            message = f"{name}: probe failed ({exc})"
        if message:
            print(f"  ⚠️  {message}")
            drift = True
        else:
            print(f"  {name}: vendored record still current")

    if drift:
        print("\nSomething moved. After updating, run: python3 tools/audit_claims.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
