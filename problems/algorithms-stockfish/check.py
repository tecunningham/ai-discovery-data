#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import year_fraction  # noqa: E402
from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "stockfish-ncm-elo.csv")
    first, last = rows[0], rows[-1]
    # The document and the figure both take the last row as the newest build,
    # so the check states the same rule rather than re-deriving a maximum.
    same_day = [float(row["elo_vs_sf15"]) for row in rows if row["date"] == last["date"]]
    span = float(last["elo_vs_sf15"]) - float(first["elo_vs_sf15"])
    years = year_fraction(last["date"]) - year_fraction(first["date"])
    # Every calendar-year figure in the document uses one convention: the last
    # tested build of the year against the last tested build of the year before.
    last_of_year: dict[str, float] = {}
    for row in rows:
        last_of_year[row["date"][:4]] = float(row["elo_vs_sf15"])
    gain = {year: last_of_year[year] - last_of_year[str(int(year) - 1)]
            for year in ("2020", "2021", "2022", "2023", "2024", "2025", "2026")}
    claims = {
        f"**span:** Stockfish 3 measures {first['elo_vs_sf15']} ± "
        f"{first['elo_err']} against Stockfish 15 on {first['date']}, and "
        f"the newest build measures +{last['elo_vs_sf15']} ± "
        f"{last['elo_err']} on {last['date']} — about {round(span)} Elo of "
        f"pure software progress, averaging {round(span / years)} Elo a "
        "year".replace("-537.61", "−537.61"): "span fact",
        f"**builds:** {len(rows):,} tested development builds": "builds fact",
        f"**final-day spread:** {len(same_day)} builds share that final date "
        f"and span {min(same_day)} to {max(same_day)}": "final-day fact",
        f"**nnue-era gains:** year-end to year-end, calendar 2020 gained "
        f"about {round(gain['2020'])} Elo and 2021 about "
        f"{round(gain['2021'])}": "NNUE-era fact",
        f"**recent gains:** the same year-end convention gives "
        f"{round(gain['2022'])} in 2022, {round(gain['2023'])} in 2023, "
        f"{round(gain['2024'])} in 2024, {round(gain['2025'])} in 2025, and "
        f"{round(gain['2026'])} through {last['date']}, which annualizes to "
        f"about {round(annualized(gain['2026'], last['date']))}":
            "recent-gains fact",
        f"no acceleration — {round(gain['2026'])} Elo through "
        f"{last['date']} (annualizing to about "
        f"{round(annualized(gain['2026'], last['date']))} Elo/year) against "
        f"{round(gain['2025'])} Elo in 2025 and a {round(span / years)} "
        "Elo/year mean over 2013–2026": "verdict clause",
        f"Coverage:** {first['date']} to {last['date']}, {len(rows):,} "
        "tested development builds": "coverage field",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
