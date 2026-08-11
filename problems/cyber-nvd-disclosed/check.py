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
    annual = read_csv(HERE / "nvd-by-year.csv")
    counts = {row["year"]: int(row["nvd_published"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    through = current["data_through"]
    pace = annualized(counts[current["year"]], through)

    def growth(earlier: str, later: str) -> int:
        return round((counts[later] / counts[earlier] - 1) * 100)

    claims = {
        f"{counts['2016']:,} CVEs in 2016": "2016 count",
        f"{counts['2017']:,} in 2017": "2017 count",
        f"{counts['2020']:,} in 2020": "2020 count",
        f"{counts['2022']:,} in 2022": "2022 count",
        f"{counts['2024']:,} in 2024": "2024 count",
        f"{counts['2025']:,} in 2025": "2025 count",
        f"{counts['2026']:,} through {through}": "part-year count",
        f"annualizes to about {round(pace, -3):,.0f}".replace(",000", ",000"):
            "annualized pace",
        f"roughly {pace / counts['2025']:.1f} times 2025": "pace against 2025",
        f"+{growth('2023', '2024')}% into 2024": "2024 growth",
        f"+{growth('2024', '2025')}% into 2025": "2025 growth",
        f"about +{round((pace / counts['2025'] - 1) * 100)}% annualized for 2026":
            "annualized 2026 growth",
        f"about {round(counts['2025'] * 2, -2):,} disclosures": "doubling comparator",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
