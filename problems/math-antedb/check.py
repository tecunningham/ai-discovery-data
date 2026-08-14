#!/usr/bin/env python3
"""Recompute this page's fact lines from the sweep and bounds CSVs."""

from __future__ import annotations

import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def sweep_events() -> dict[str, dict[int, int]]:
    """Slice-level changes per family and year, as figure.py counts them."""
    series: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    for row in read_csv(HERE / "antedb-sweep.csv"):
        series[(row["quantity"], row["point"])].append(
            (int(row["year"]), float(row["value_float"])))
    events: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for (quantity, _point), values in series.items():
        values.sort()
        previous = values[0][1]
        for year, value in values[1:]:
            if value != previous:
                events[quantity][year] += 1
                previous = value
    return events


def named_records(quantity: str, sigma: str) -> list[tuple[int, str, str]]:
    """A named slice's distinct records from the bounds CSV, in year order."""
    rows = sorted((row for row in read_csv(HERE / "antedb-bounds.csv")
                   if row["quantity"] == quantity and row["sigma"] == sigma),
                  key=lambda row: int(row["year"]))
    records: list[tuple[int, str, str]] = []
    for row in rows:
        if not records or row["value"] != records[-1][1]:
            records.append((int(row["year"]), row["value"],
                            row["attribution"]))
    return records


def main() -> int:
    events = sweep_events()
    slices = {quantity: len({(q, p) for (q, p) in (
        (row["quantity"], row["point"])
        for row in read_csv(HERE / "antedb-sweep.csv")) if q == quantity})
        for quantity in ("mu", "A", "beta")}
    totals = {quantity: sum(events[quantity].values()) for quantity in events}
    total = sum(totals.values())
    years = sorted(year for family in events.values() for year in family)
    by_year = defaultdict(int)
    for family in events.values():
        for year, count in family.items():
            by_year[year] += count
    mu_through = lambda through: sum(  # noqa: E731
        count for year, count in events["mu"].items() if year <= through)

    failures: list[str] = []
    lindelof = named_records("mu", "1/2")
    if (lindelof[0][:2] != (1920, "5/28")
            or "van der Corput" not in lindelof[0][2]
            or lindelof[-1][:2] != (2017, "13/84")
            or "Bourgain" not in lindelof[-1][2]):
        failures.append("the Lindelöf slice no longer runs van der Corput "
                        "5/28 (1920) to Bourgain 13/84 (2017)")
    a34 = named_records("A", "3/4")
    if ([record[0] for record in a34] != [1921, 1940, 2024]
            or a34[-1][1] != "20/9"
            or "Guth" not in a34[-1][2]):
        failures.append("the A(3/4) slice no longer runs Carlson 1921, "
                        "Ingham 1940, Guth–Maynard 20/9 2024")
    factor = float(Fraction("13/84") / Fraction("5/28"))
    if f"{factor:.3f}" != "0.867":
        failures.append("the Lindelöf factor no longer rounds to 0.867")

    claims = {
        f"**changes:** {total} slice-level record changes: {totals['mu']} "
        f"across the twenty $\\mu$ slices, {totals['A']} across the nineteen "
        f"$A$ slices, and {totals['beta']} across the nineteen $\\beta$ "
        "slices": "changes fact",
        f"**span:** first change {years[0]}, last change {years[-1]}; "
        f"{by_year[2025] + by_year[2026]} changes in 2025 or 2026":
            "span fact",
        f"**mu by period:** the cumulative $\\mu$ count runs "
        f"{mu_through(1980)} through 1980, {mu_through(1990)} through 1990 "
        f"and {mu_through(2000)} through 2000, with "
        f"{mu_through(2005) - mu_through(2000)} changes over 2001–2005, "
        "none from 2006 through 2010, and "
        f"{mu_through(2023)} through 2023": "mu-by-period fact",
        f"**lindelof slice:** $\\mu(1/2)$ fell from $5/28 \\approx 0.1786$ "
        "(van der Corput, 1920) to $13/84 \\approx 0.1548$ (Bourgain, 2017) "
        f"across {len(lindelof)} recorded values, a factor of {factor:.3f} "
        f"in {2017 - 1920} years": "lindelof fact",
        f"**a-slice:** $A(3/4)$ has {len(a34)} records in {2024 - 1921} "
        "years: Carlson in 1921, Ingham in 1940, then Guth and Maynard's "
        "$20/9$ in 2024": "a-slice fact",
        f"0 slice changes in 2025 or 2026 against {by_year[2024]} in 2024 "
        f"and a {total / (2024 - years[0] + 1):.1f}/year mean over "
        f"{years[0]}–2024": "verdict clause",
        f"{slices['mu'] + slices['A'] + slices['beta']} exponent slices":
            "metric slice count",
    }
    if by_year[2025] + by_year[2026] != 0:
        failures.append("changes now exist in 2025 or 2026; the span fact "
                        "and verdict clause both assume none")
    if mu_through(2010) != mu_through(2005):
        failures.append("mu changes now exist in 2006–2010; the mu-by-period "
                        "fact says none")
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
