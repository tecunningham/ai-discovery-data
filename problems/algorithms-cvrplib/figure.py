#!/usr/bin/env python3
"""Draw annual fixed-X objective improvements and optimality proofs."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib import chart  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "cvrplib-x-frontier.csv")
    objective = Counter(int(row["recorded_date"][:4]) for row in rows
                        if row["event_type"] == "objective_improvement")
    proofs = Counter(int(row["recorded_date"][:4]) for row in rows
                     if row["event_type"] == "optimality_proof")
    years = list(range(2015, 2027))
    fig, ax = chart.new_chart(
        "CVRPLIB X-instance record frontier",
        "Fixed 100-instance cohort; objective improvements and later proofs are distinct",
    )
    ax.bar(years, [objective[y] for y in years], width=0.76,
           color=chart.UNATTRIBUTED, zorder=3)
    ax.bar(years, [proofs[y] for y in years], width=0.76,
           bottom=[objective[y] for y in years], color=chart.NEUTRAL, zorder=3)
    right = 2027.2
    ax.set_xlim(2014.3, right)
    ax.set_ylim(0, max(objective.values()) * 1.18)
    chart.shade_era(ax, right, annual=True)
    chart.style(ax, "Recorded frontier events")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.legend(handles=[
        Patch(facecolor=chart.UNATTRIBUTED, label="better objective"),
        Patch(facecolor=chart.NEUTRAL, label="optimality proved"),
    ], frameon=False, fontsize=8, ncol=2)
    ax.text(2024, 4, "no X-cohort event", ha="center", fontsize=8, color="#555555")
    chart.source_note(fig, "Source: CVRPLIB Updates. Dates are public-ledger posting dates.")
    chart.save(
        fig,
        HERE / "discovery-algorithms-cvrplib.png",
        "CVRPLIB fixed-X record frontier. Annual public-ledger events, 2015–2026.",
        ["https://galgos.inf.puc-rio.br/cvrplib/index.php/en/updates/"],
        __file__,
    )


if __name__ == "__main__":
    main()
