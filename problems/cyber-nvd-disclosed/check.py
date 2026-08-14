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
    annual = read_csv(HERE / "nvd-by-year.csv")
    counts = {row["year"]: int(row["nvd_published"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    through = current["data_through"]
    pace = annualized(counts[current["year"]], through)

    def growth(earlier: str, later: str) -> int:
        return round((counts[later] / counts[earlier] - 1) * 100)

    from datetime import date
    day = date.fromisoformat(through).timetuple().tm_yday
    quarterly = read_csv(HERE / "nvd-by-quarter.csv")
    q_counts = {row["quarter"]: int(row["nvd_published"]) for row in quarterly}
    prior_peak = max(count for quarter, count in q_counts.items()
                     if quarter < "2026")
    peak_2025 = max(count for quarter, count in q_counts.items()
                    if quarter.startswith("2025"))
    by_year_line = " · ".join(
        f"{row['year']}: {int(row['nvd_published']):,}" for row in annual
        if row["partial_year"] == "no")

    claims = {
        f"Coverage:** 2016–2026, partial through {through}":
            "coverage field",
        f"{counts['2026']:,} CVEs through {through} annualize to about "
        f"{round(pace, -3):,.0f}, roughly {pace / counts['2025']:.1f} times "
        f"2025's {counts['2025']:,}, after +{growth('2023', '2024')}% growth "
        f"into 2024 and +{growth('2024', '2025')}% into 2025":
            "verdict clause",
        f"**by-year:** {by_year_line}": "by-year fact",
        f"**2026 (through {through}):** {counts['2026']:,} CVEs, day {day} "
        f"of the year; annualizes to about {round(pace, -3):,.0f}, roughly "
        f"{pace / counts['2025']:.1f} times 2025": "part-year fact",
        f"**growth:** +{growth('2023', '2024')}% into 2024 and "
        f"+{growth('2024', '2025')}% into 2025, against about "
        f"+{round((pace / counts['2025'] - 1) * 100)}% annualized for 2026":
            "growth fact",
        f"**2026 quarters:** Q1's {q_counts['2026-Q1']:,} topped every "
        f"quarter before it; Q2's {q_counts['2026-Q2']:,} is another "
        f"{round((q_counts['2026-Q2'] / q_counts['2026-Q1'] - 1) * 100)}% "
        f"above Q1 and "
        f"{round((q_counts['2026-Q2'] / peak_2025 - 1) * 100)}% above 2025's "
        "largest quarter": "quarters fact",
        f"**doubling arithmetic:** a 2026 double of 2025 would require "
        f"about {round(counts['2025'] * 2, -2):,} disclosures; the "
        f"annualized pace is about {round(pace, -3):,.0f}, or roughly "
        f"{pace / counts['2025']:.1f} times": "doubling fact",
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
