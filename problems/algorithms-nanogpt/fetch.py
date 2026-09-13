#!/usr/bin/env python3
"""Probe the modded-nanogpt README for new records; vendor pending claims.

Run: python3 problems/algorithms-nanogpt/fetch.py

Accepted records are transcribed by hand: each row carries the agent and the
credited AI system, which the README states in prose that needs judgment to
attribute. For those this script is a staleness probe — it reports, and exits
non-zero, when the README lists a record past the vendored series.

Pending claims it does vendor. An entrant opens a pull request titled "New
Record: <minutes> ..." before the maintainer reproduces it, and until that
happens the claim is real but unverified. Every open pull request whose title
claims a time below the standing record, opened on or before lib/dates.py's
AS_OF_DATE, is written as a row with ``kind=pending``: ``record`` is
``PR<number>``, ``date`` is the day it was opened, ``agent`` and ``ai_system``
are left empty because attribution waits for acceptance, and ``note`` is the
title. Pending rows are machine-owned: a claim that is merged becomes a
hand-transcribed record, one that is closed disappears, and the next run
rewrites the set either way. Nothing counts a pending row as a record — not
the fact lines, not the figures — but the comparison page's tentative view
draws them, which is what they are for.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import AS_OF_DATE  # noqa: E402
from lib.table import read_csv, write_csv  # noqa: E402
from lib.web import fetch, fetch_json  # noqa: E402

URL = ("https://raw.githubusercontent.com/KellerJordan/modded-nanogpt/"
       "master/README.md")
PULLS = ("https://api.github.com/repos/KellerJordan/modded-nanogpt/pulls"
         "?state=open&per_page=100")
CSV = HERE / "nanogpt-records.csv"
FIELDS = ["record", "kind", "date", "minutes", "agent", "ai_system", "note"]

# "New Record: 0.665 minutes (39.9 seconds): ..." and the looser
# "New record: 1384 steps / 1.312 min — ..." both name the claimed time in
# minutes after the words "new record".
CLAIM = re.compile(r"(?i)\bnew record\b.*?(\d+(?:\.\d+)?)\s*min")


def pending_rows(standing: float) -> list[dict[str, str]]:
    """Open pull requests claiming a time below the standing record."""
    pulls = fetch_json(PULLS, refresh=True, accept="application/vnd.github+json")
    rows = []
    for pull in pulls:
        match = CLAIM.search(pull["title"])
        if not match:
            continue
        opened = pull["created_at"][:10]
        if float(match.group(1)) >= standing or date.fromisoformat(opened) > AS_OF_DATE:
            continue
        rows.append({
            "record": f"PR{pull['number']}", "kind": "pending", "date": opened,
            "minutes": match.group(1), "agent": "", "ai_system": "",
            "note": f"open pull request #{pull['number']}: {pull['title']}",
        })
    return sorted(rows, key=lambda row: (row["date"], row["record"]))


def probe(records: list[dict[str, str]]) -> str | None:
    """Report when the README lists an accepted record past the vendored ones."""
    last_n = int(records[-1]["record"]) if records else 0
    last_minutes = records[-1]["minutes"] if records else "?"
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    # Record rows look like: "86 | 1.266 minutes | <description> | 05/27/26 | ..."
    rows = re.findall(r"(?m)^(\d+) \| ([\d.]+) minutes \|", text)
    if not rows:
        return ("nanogpt-records.csv: no record-table rows parsed from the "
                "README — its format changed; check by hand")
    newest_n, newest_minutes = max((int(n), m) for n, m in rows)
    if newest_n > last_n:
        return (f"nanogpt-records.csv: README now has record {newest_n} at "
                f"{newest_minutes} min; vendored series ends at record {last_n} "
                f"({last_minutes} min) — update the CSV and this folder's "
                "README.md by hand (authorship needs judgment)")
    return None


def main() -> int:
    vendored = read_csv(CSV)
    kept = [row for row in vendored if row["kind"] != "pending"]
    records = [row for row in kept if row["kind"] == "record"]
    standing = float(records[-1]["minutes"]) if records else float("inf")

    pending = pending_rows(standing)
    before = [row for row in vendored if row["kind"] == "pending"]
    if pending != before:
        write_csv(CSV, kept + pending, FIELDS)
        print(f"wrote {CSV.name}: {len(pending)} pending claim(s) "
              f"({len(before)} before)")
    else:
        print(f"{CSV.name}: {len(pending)} pending claim(s), unchanged")
    for row in pending:
        print(f"  {row['record']} {row['date']} {row['minutes']} min")

    message = probe(records)
    if message:
        print(f"⚠️  {message}")
        return 1
    print("nanogpt-records.csv: README lists no record past the vendored series")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
