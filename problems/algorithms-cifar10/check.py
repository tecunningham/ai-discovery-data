#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

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
                        "start falls through 'six further hlb-CIFAR10 releases'")

    # The yearly improvement factor divides the standing record at one year's
    # end by the standing record at the next; the CSV is in date order.
    last_of_year: dict[str, float] = {}
    for row in plotted:
        last_of_year[row["date"][:4]] = float(row["seconds"])
    factor = {year: last_of_year[str(int(year) - 1)] / last_of_year[year]
              for year in ("2023", "2024", "2025", "2026")}
    last_2023 = [row for row in plotted if row["date"].startswith("2023")][-1]
    airbench = next(row for row in plotted if "airbench" in row["holder"])
    proto = next(row for row in plotted if "proto-Muon" in row["holder"])
    muon = next(row for row in plotted if row["holder"].endswith("(Muon)"))
    claim = plotted[-1]

    claims = {
        f"**rows:** {len(rows)} rows; {len(plotted)} plotted from 2022 on; "
        f"{len(rows) - len(plotted)} pre-2022 V100 row excluded": "rows fact",
        f"**start:** {plotted[0]['seconds']} seconds at hlb-CIFAR10 v0.1.0 "
        f"on {plotted[0]['date']}": "start fact",
        f"**2023 close:** {last_2023['seconds']} seconds by "
        f"{last_2023['date']}": "2023-close fact",
        f"**2024 records:** {airbench['seconds']} seconds at airbench on "
        f"{airbench['date']}; {proto['seconds']} seconds with a proto-Muon "
        "optimizer, dated only to a bracket of April to November 2024; "
        f"{muon['seconds']} seconds with Muon on {muon['date']}":
            "2024-records fact",
        f"**ai-record:** {hiverge['seconds']} seconds by Hiverge on "
        f"{hiverge['date']}, a step of about {step}% against the "
        f"{displaced['seconds']}-second record it displaced": "AI-record fact",
        f"**claim:** {claim['seconds']} seconds by Fulcrum researchers "
        f"running the Fable model, reported {claim['date']}": "claim fact",
        f"**yearly-factor:** 2023: {factor['2023']:.1f} · 2024: "
        f"{factor['2024']:.1f} · 2025: {factor['2025']:.1f} · 2026 (through "
        f"{claim['date']}, claim included): {factor['2026']:.2f}":
            "yearly-factor fact",
        f"declining — yearly improvement factor {factor['2026']:.2f} in 2026 "
        f"(through {claim['date']}, claim included) against "
        f"{factor['2025']:.1f} in 2025 and {factor['2024']:.1f} in 2024":
            "verdict clause",
        f"to a claim of {claim['date']}": "coverage end",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
