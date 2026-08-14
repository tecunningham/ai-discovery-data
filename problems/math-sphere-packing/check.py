#!/usr/bin/env python3
"""Recompute this page's fact lines from the record ladder CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "sphere-packing-lower-bound-records.csv")
    years = sorted(int(row["year"]) for row in rows)
    by_year = Counter(years)
    early = sum(1905 <= year <= 2010 for year in years)
    late = sum(2011 <= year <= 2025 for year in years)
    recent = sum(2013 <= year <= 2025 for year in years)
    plateau = sum(1948 <= year <= 1992 for year in years)

    failures: list[str] = []
    if by_year[2026]:
        failures.append("a 2026 row now exists; the verdict clause says "
                        "0 steps dated 2026")

    claims = {
        f"**steps:** {len(rows)} recorded steps, {years[0]}–{years[-1]}":
            "steps fact",
        "**by-year:** " + " · ".join(f"{year}: {by_year[year]}"
                                     for year in sorted(by_year)):
            "by-year fact",
        f"**split:** {early} steps over 1905–2010 and {late} over "
        f"2011–2025; {recent} steps in the 13 years to 2025 against "
        f"{plateau} in the 45 years to 1992": "split fact",
        f"**ai-attributed:** 0 of {len(rows)} steps": "AI fact",
        f"accelerating — {late} steps over 2011–2025 "
        f"({late / 15 * 10:.1f}/decade) against {early} over 1905–2010 "
        f"({early / 106 * 10:.1f}/decade); {by_year[2026]} steps dated 2026":
            "verdict clause",
        f"Coverage:** {years[0]}–{years[-1]}, eight recorded steps":
            "coverage field",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
