#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, register_entry, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "smale-problems.csv")
    status = Counter(row["status"] for row in rows)
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_ids = [row["problem_id"] for row in rows if row["status"] == "open"]
    by_year = " · ".join(f"{year}: {dated.count(year)}"
                         for year in sorted(set(dated)))
    prior = [year for year in dated if year != 2026]
    ai_rows = [row for row in rows if row["problem_id"] == "16"]
    failures: list[str] = []
    if status["resolved"] != len(dated):
        failures.append("a resolved row has no resolved_year; the facts "
                        "count dated resolutions only")
    if not (ai_rows and ai_rows[0]["status"] == "resolved"
            and ai_rows[0]["resolved_year"] == "2026"):
        failures.append("row 16 is no longer a 2026 resolution; the AI "
                        "attribution section and figure.py's ai_problem "
                        "argument rest on it")
    if dated.count(2026) != 1:
        failures.append("the ledger no longer has exactly one 2026 "
                        "resolution; the verdict clause is stale")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {len(open_ids)} open; {status['contested']} contested":
            "rows fact",
        f"**span:** dated resolutions {dated[0]}–{dated[-1]}": "span fact",
        f"**by-year:** {by_year}": "by-year fact",
        f"**ai-attributed:** 1 of {len(dated)} dated resolutions": "AI fact",
        "**open rows:** " + ", ".join(open_ids): "open-rows fact",
        f"1 resolution in 2026 against {len(prior)} over "
        f"{prior[0]}–{prior[-1]}; a series of {len(dated)} events sets no "
        "rate": "verdict clause",
    }
    # Every non-open row appears in the register with the CSV's own values,
    # in the fixed key order status / resolved / resolver.
    for row in rows:
        if row["status"] == "open":
            continue
        claims[register_entry(row)] = f"register entry {row['problem_id']}"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
