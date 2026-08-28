#!/usr/bin/env python3
"""Recompute this page's fact lines from the CSVs beside it."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    annual = read_csv(HERE / "ossfuzz-by-year.csv")
    counts = {row["year"]: int(row["discoveries"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    pace = annualized(counts[current["year"]], current["data_through"])
    total = sum(counts.values())
    quarterly = read_csv(HERE / "ossfuzz-by-quarter.csv")
    published = sum(int(row["discoveries"]) for row in quarterly
                    if row["quarter"].startswith(current["year"]))
    by_year = " · ".join(f"{year}: {counts[year]:,}"
                         for year in sorted(counts) if year != current["year"])
    claims = {
        f"**by-year (record id):** {by_year} · {current['year']} "
        f"(through {current['data_through']}): {counts[current['year']]}":
            "by-year fact",
        f"**2026 annualized:** roughly {round(pace)} records":
            "annualized fact",
        f"**total:** {total:,} records over 2020–{current['year']}":
            "total fact",
        f"**clock gap:** quarters by published date sum to {published} "
        f"records in {current['year']} against {counts[current['year']]} "
        "by record id": "clock-gap fact",
        f"{counts['2020']:,} records in 2020 to {counts['2025']} in 2025; "
        f"2026 annualizes to roughly {round(pace)}": "verdict clause",
        f"Coverage:** 2020–2026, partial through {current['data_through']}":
            "coverage field",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
