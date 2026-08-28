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
    rows = read_csv(HERE / "landau-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_ids = [row["problem_id"] for row in rows if row["status"] == "open"]
    list_year = rows[0]["list_year"]
    failures: list[str] = []
    if dated:
        failures.append("a dated resolution exists; the page is written "
                        "around an empty event set and is stale throughout")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {len(open_ids)} open": "rows fact",
        "**open rows:** " + ", ".join(open_ids): "open-rows fact",
        f"**ai-attributed:** 0 of {len(rows)} scored rows": "AI fact",
        f"0 resolutions in 2026; {len(dated)} dated resolutions over "
        f"{list_year}–2025": "verdict clause",
    }
    # Every non-open row appears in the register with the CSV's own values;
    # with all four rows open, the loop asserts nothing, and the page states
    # the register is empty.
    for row in rows:
        if row["status"] == "open":
            continue
        claims[register_entry(row)] = f"register entry {row['problem_id']}"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
