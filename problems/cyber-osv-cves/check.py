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
    annual = read_csv(HERE / "osv-cves-by-year.csv")
    counts = {row["year"]: int(row["distinct_cves"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    through = current["data_through"]
    pace = annualized(counts[current["year"]], through)
    claims = {
        f"from {counts['2016']:,} in 2016": "2016 count",
        f"{counts['2020']:,} in 2020": "2020 count",
        f"{counts['2022']:,} in 2022": "2022 count",
        f"{counts['2024']:,} in 2024": "2024 count",
        f"{counts['2025']:,} in 2025": "2025 count",
        f"{counts['2026']:,} through": "part-year count",
        f"about {round(pace, -2):,.0f}": "annualized pace",
        f"{pace / counts['2025']:.1f} times the\n2025 count".replace("\n", " "):
            "pace against 2025",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
