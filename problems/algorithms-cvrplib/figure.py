#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of fixed-X frontier events.

Run: python3 problems/algorithms-cvrplib/figure.py

discovery-algorithms-cvrplib.png counts annual objective improvements and
optimality proofs; cumulative-algorithms-cvrplib.png is the same cohort as
instances remaining without an optimality proof, for the collection-wide
cumulative index.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib import chart  # noqa: E402
from lib.cumulative import remaining_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The X set was introduced as one designed cohort of exactly this many
# instances, which is what makes a fixed denominator honest here.
COHORT = 100


def cumulative() -> None:
    rows = read_csv(HERE / "cvrplib-x-frontier.csv")
    xs = [min(chart.year_fraction(row["recorded_date"]) for row in rows)]
    ys = [float(COHORT)]
    proved: set[str] = set()
    for row in sorted(rows, key=lambda row: row["recorded_date"]):
        if row["event_type"] != "optimality_proof" or row["instance"] in proved:
            continue
        proved.add(row["instance"])
        xs.append(chart.year_fraction(row["recorded_date"]))
        ys.append(float(COHORT - len(proved)))
    remaining_chart(
        HERE / "cumulative-algorithms-cvrplib.png",
        title="CVRPLIB X instances: unproven remaining",
        subtitle="The fixed 100-instance cohort minus instances with a posted "
                 "optimality proof",
        ylabel="Instances without optimality proof",
        xs=xs,
        ys=ys,
        source_label="CVRPLIB Updates",
        source_url="https://galgos.inf.puc-rio.br/cvrplib/index.php/en/updates/",
        built_by=__file__,
        note=f"{len(proved)} of {COHORT} instances proven optimal; "
             "objective improvements do not move this line",
    )


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
    cumulative()
