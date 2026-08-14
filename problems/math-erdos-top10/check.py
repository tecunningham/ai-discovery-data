#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {4: "four", 8: "eight", 12: "twelve"}


def main() -> int:
    rows = read_csv(HERE / "erdos-top10-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_count = sum(row["status"] == "open" for row in rows)
    failures: list[str] = []
    if len(rows) - len(dated) != open_count:
        failures.append("rows are neither dated-resolved nor open; the prose "
                        "describes only those two states")
    ai_rows = [row for row in rows if row["problem_id"] == "90"]
    if not (ai_rows and ai_rows[0]["status"] == "resolved"
            and ai_rows[0]["resolved_year"] == "2026"):
        failures.append("row 90 is no longer a 2026 resolution; the AI "
                        "reading in the prose rests on it")
    claims = {
        f"{WORDS.get(len(rows), len(rows))} scored rows": "row count",
        f"{WORDS.get(len(dated), len(dated))} carry a dated resolution":
            "dated count",
        f"{WORDS.get(open_count, open_count)} stand open": "open count",
        f"in {min(dated)}": "first resolution year",
        f"two fell in {sorted(dated)[1]}": "middle resolution years",
        f"one in {max(dated)}": "latest resolution year",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
