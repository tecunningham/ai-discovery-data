#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

KINDS = ("better_incumbents", "new_optimal_solutions", "first_known_feasible",
         "optimal_status_only")


def main() -> int:
    rows = read_csv(HERE / "miplib-solution-releases.csv")
    total = lambda field: sum(int(row[field]) for row in rows)  # noqa: E731
    by_year: Counter[str] = Counter()
    releases_by_year: Counter[str] = Counter()
    incumbents_by_year: Counter[str] = Counter()
    for row in rows:
        year = row["release_date"][:4]
        by_year[year] += sum(int(row[kind]) for kind in KINDS)
        releases_by_year[year] += 1
        incumbents_by_year[year] += int(row["better_incumbents"])
    years = sorted(by_year)
    mean = sum(by_year[year] for year in years if year <= "2025") / len(
        [year for year in years if year <= "2025"])
    last = rows[-1]
    failures: list[str] = []
    if releases_by_year["2026"] != 1:
        failures.append(f"{releases_by_year['2026']} releases dated 2026; "
                        "the verdict clause counts a single 2026 release")

    claims = {
        f"**releases:** {len(rows)} releases with explicit solution counts, "
        f"{rows[0]['release_date']} through {last['release_date']}":
            "releases fact",
        f"**totals:** {total('better_incumbents')} better incumbents, "
        f"{total('new_optimal_solutions') + total('optimal_status_only')} "
        f"optimality updates and {total('first_known_feasible')} first "
        "feasible solutions": "totals fact",
        "**by-year (all update kinds):** " + " · ".join(
            f"{year}: {by_year[year]}" for year in years): "by-year fact",
        f"**2024:** {incumbents_by_year['2024']} better incumbents across "
        f"{releases_by_year['2024']} releases": "2024 fact",
        f"**2026:** the single 2026 release, solufile {last['solufile']} of "
        f"{last['release_date']}, reports {incumbents_by_year['2026']} "
        "better incumbents": "2026 fact",
        f"no acceleration — {by_year['2026']} announced updates in the "
        f"single 2026 release against {by_year['2025']} in 2025 and a "
        f"{mean:.1f}/year mean over 2019–2025": "verdict clause",
        f"{rows[0]['release_date']} through {last['release_date']}":
            "coverage dates",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
