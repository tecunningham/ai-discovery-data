#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import year_fraction  # noqa: E402
from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "stockfish-ncm-elo.csv")
    first, last = rows[0], rows[-1]
    # The document and the figure both take the last row as the newest build,
    # so the check states the same rule rather than re-deriving a maximum.
    same_day = [float(row["elo_vs_sf15"]) for row in rows if row["date"] == last["date"]]
    span = float(last["elo_vs_sf15"]) - float(first["elo_vs_sf15"])
    years = year_fraction(last["date"]) - year_fraction(first["date"])
    claims = {
        f"{first['elo_vs_sf15']} ± {first['elo_err']} against Stockfish 15 on "
        f"{first['date']}".replace("-537.61", "−537.61"): "opening measurement",
        f"+{last['elo_vs_sf15']} ± {last['elo_err']} on {last['date']}":
            "closing measurement",
        f"about\n{round(span)} Elo of pure software progress".replace("\n", " "):
            "total span",
        f"averaging {round(span / years)} Elo a year": "annual average",
        f"{len(same_day)} builds share that final date": "tied-build count",
        f"span {min(same_day)} to {max(same_day)}": "tied-build spread",
        f"{len(rows):,} tested development builds": "build count",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
