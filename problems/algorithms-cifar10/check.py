#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "cifar-speedrun-records.csv")
    plotted = [row for row in rows if row["date"] >= "2022"]
    failures = []
    if len(rows) - len(plotted) != 1:
        failures.append(f"{len(rows) - len(plotted)} pre-2022 rows; the prose "
                        "accounts for exactly one, the V100 result")
    if len(plotted) != 12:
        failures.append(f"the plotted series has {len(plotted)} points; the "
                        "prose says 'only a dozen points'")

    hlb = [row for row in plotted if "hlb-CIFAR10" in row["holder"]]
    hiverge = next(row for row in plotted if "Hiverge" in row["holder"])
    displaced = plotted[plotted.index(hiverge) - 1]
    step = round(100 * (1 - float(hiverge["seconds"]) / float(displaced["seconds"])))
    if len(hlb) != 7:
        failures.append(f"{len(hlb)} hlb-CIFAR10 releases; the prose says the "
                        "start falls through 'six further releases'")

    # The yearly improvement factor divides the standing record at one year's
    # end by the standing record at the next; the CSV is in date order.
    last_of_year: dict[str, float] = {}
    for row in plotted:
        last_of_year[row["date"][:4]] = float(row["seconds"])
    factor = {year: last_of_year[str(int(year) - 1)] / last_of_year[year]
              for year in ("2023", "2024", "2025", "2026")}
    last_2023 = [row for row in plotted if row["date"].startswith("2023")][-1]
    airbench = next(row for row in plotted if "airbench" in row["holder"])
    muon = next(row for row in plotted if row["holder"].endswith("(Muon)"))

    claims = {
        f"{plotted[0]['seconds']} seconds at hlb-CIFAR10 v0.1.0 on "
        f"{plotted[0]['date']}": "series start",
        f"{last_2023['seconds']} seconds by {last_2023['date']}": "2023 close",
        f"{airbench['seconds']} seconds at airbench on {airbench['date']}":
            "airbench record",
        f"{muon['seconds']} seconds with Muon on {muon['date']}": "Muon record",
        f"reached {hiverge['seconds']} seconds": "Hiverge record",
        f"claim of {plotted[-1]['seconds']} seconds": "Fulcrum claim",
        f"ends with a claim of {plotted[-1]['date']}": "coverage end",
        f"a step of about {step}%": "AI step size",
        f"run {factor['2023']:.1f} in 2023 and {factor['2024']:.1f} in 2024":
            "human-era factors",
        f"then {factor['2025']:.1f} in 2025": "2025 factor",
        f"and {factor['2026']:.2f} through early July 2026": "2026 factor",
        f"falls from {factor['2023']:.1f} to a claimed {factor['2026']:.2f}":
            "verdict factors",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
