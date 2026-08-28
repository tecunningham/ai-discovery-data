#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, register_entry, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "millennium-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_ids = [row["problem_id"] for row in rows if row["status"] == "open"]
    by_year = " · ".join(f"{year}: {dated.count(year)}"
                         for year in sorted(set(dated)))
    list_year = rows[0]["list_year"]
    failures: list[str] = []
    if len(dated) != 1:
        failures.append("the ledger no longer has exactly one dated "
                        "resolution; the verdict clause and the singular "
                        "phrasing throughout are stale")
    if dated and dated[-1] > 2025:
        failures.append("a dated resolution in 2026 exists; the verdict "
                        "clause stating 0 in 2026 is stale")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {len(open_ids)} open": "rows fact",
        f"**by-year:** {by_year}": "by-year fact",
        f"**ai-attributed:** 0 of {len(dated)} dated resolutions": "AI fact",
        "**open rows:** " + ", ".join(open_ids): "open-rows fact",
        f"0 resolutions in 2026; {len(dated)} dated resolution ({dated[0]}) "
        f"over {list_year}–2025": "verdict clause",
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
