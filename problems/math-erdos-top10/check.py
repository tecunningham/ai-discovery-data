#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "erdos-top10-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_ids = [row["problem_id"] for row in rows if row["status"] == "open"]
    by_year = " · ".join(f"{year}: {dated.count(year)}"
                         for year in sorted(set(dated)))
    ai_rows = [row for row in rows if row["problem_id"] == "90"]
    failures: list[str] = []
    if len(rows) != len(dated) + len(open_ids):
        failures.append("rows are neither dated-resolved nor open; the "
                        "**rows:** fact line only counts those two states")
    if not (ai_rows and ai_rows[0]["status"] == "resolved"
            and ai_rows[0]["resolved_year"] == "2026"):
        failures.append("row 90 is no longer a 2026 resolution; the AI "
                        "attribution section rests on it")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {len(open_ids)} open": "rows fact",
        f"**by-year:** {by_year}": "by-year fact",
        f"**ai-attributed:** 1 of {len(dated)} dated resolutions": "AI fact",
        "**open rows:** " + ", ".join(open_ids): "open-rows fact",
        f"{dated.count(2026)} resolution in 2026": "verdict 2026 count",
    }
    # Every non-open row appears in the register with the CSV's own values,
    # in the fixed key order status / resolved / resolver.
    for row in rows:
        if row["status"] == "open":
            continue
        claims[
            f"### {row['problem_id']} — {row['short_name']} "
            f"- **status:** {row['status']} "
            f"- **resolved:** {row['resolved_year']} "
            f"- **resolver:** {row['resolver']}"
        ] = f"register entry {row['problem_id']}"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
