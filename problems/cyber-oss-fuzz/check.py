#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    annual = read_csv(HERE / "ossfuzz-discoveries.csv")
    counts = {row["year"]: int(row["discoveries"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    pace = annualized(counts[current["year"]], current["data_through"])
    total = sum(counts.values())
    quarterly = read_csv(HERE / "ossfuzz-by-quarter.csv")
    published = sum(int(row["discoveries"]) for row in quarterly
                    if row["quarter"].startswith(current["year"]))
    claims = {
        f"{counts['2020']:,} records in 2020": "2020 count",
        f"then {counts['2021']}, {counts['2022']}, {counts['2023']}, "
        f"{counts['2024']} and\n{counts['2025']} in 2025".replace("\n", " "):
            "middle-year counts",
        f"{counts['2026']} through": "part-year count",
        f"roughly {round(pace)}": "annualized pace",
        f"total is {total:,} records": "cumulative total",
        f"quarters sum to {published} records against "
        f"{counts[current['year']]} by record id": "id-year vs published-quarter gap",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
