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

    quarterly = read_csv(HERE / "nvd-by-quarter.csv")
    q_counts = {row["quarter"]: int(row["nvd_published"]) for row in quarterly}
    prior_peak = max(count for quarter, count in q_counts.items()
                     if quarter < "2026")
    peak_2025 = max(count for quarter, count in q_counts.items()
                    if quarter.startswith("2025"))
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
        f"Q1's {q_counts['2026-Q1']:,} already topped every quarter before it":
            "2026-Q1 record quarter",
        f"Q2's {q_counts['2026-Q2']:,} is another "
        f"{round((q_counts['2026-Q2'] / q_counts['2026-Q1'] - 1) * 100)}% above Q1":
            "2026-Q2 over Q1",
        f"{round((q_counts['2026-Q2'] / peak_2025 - 1) * 100)}% above "
        "2025's largest quarter": "2026-Q2 over 2025 peak",
    }
    failures = missing(prose(HERE), claims)
    # "Topped every quarter before it" is checked, not assumed: a refetch that
    # revises history upward could quietly falsify the record claim.
    if q_counts["2026-Q1"] <= prior_peak:
        failures.append(
            f"README calls 2026-Q1 ({q_counts['2026-Q1']}) a record quarter, "
            f"but an earlier quarter reached {prior_peak}"
        )
    return report(failures)


if __name__ == "__main__":
    raise SystemExit(main())
