#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "green-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_count = sum(row["status"] == "open" for row in rows)
    partial = sum(row["status"] == "partial" for row in rows)
    undated = sum(row["status"] == "resolved" and not row["resolved_year"]
                  for row in rows)
    per_year = {year: dated.count(year) for year in set(dated)}
    span_years = max(dated) - min(dated) + 1
    failures: list[str] = []
    if undated:
        failures.append(f"{undated} resolved rows lack a year; the prose "
                        "assumes every resolution is dated")
    rate = len(dated) / (2026 - int(rows[0]["list_year"]))
    if not 1.2 <= rate <= 2.2:
        failures.append(f"resolution rate is {rate:.2f} per year, and the "
                        "prose calls it under two")
    claims = {
        f"{len(rows)} scored rows": "row count",
        f"{len(dated)} of them carry a dated resolution": "dated count",
        f"running {min(dated)} to {max(dated)}": "resolution span",
        f"{open_count} rows stand open": "open count",
        f"{per_year.get(2023, 0)} in 2023": "peak year",
        f"{per_year.get(2025, 0)} in 2025": "latest full year",
        f"{len(dated)} resolutions in {span_years} years": "rate numerator",
    }
    if partial != 1:
        failures.append(f"{partial} partial rows, but the prose describes "
                        "exactly one (Problem 11)")
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
