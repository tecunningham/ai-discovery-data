#!/usr/bin/env python3
"""Draw this folder's two figures from the FrontierMath open-problems ledgers.

Run: python3 problems/math-frontiermath-open/figure.py

discovery-math-frontiermath-open.png is two panels sharing the notability
lanes: a timeline placing each dated solution event by date, and a
denominator panel drawing the whole pool today as one stacked bar per tier —
open, solved by AI, solved by humans — so the six events on the left are
read against the 47 problems still standing on the right.
cumulative-math-frontiermath-open.png is the running count of solved
problems for the collection-wide cumulative index. Both read the mechanical
page ledger and the hand-transcribed event ledger beside this file.

This chart is a one-off shape rather than a lib/families call: no other series
places events on a curator-assigned significance scale, and the whole series
lives inside 2026, so the year-axis conventions of the shared ledger chart
would collapse it to a single bar. The open-bar colour is the cumulative
page's open-rows colour, so "what remains" reads the same across the
collection.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib import pyplot as plt  # noqa: E402

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    NOW,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.cumulative import OPEN_COLOUR, events_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

TIERS = ["Moderately interesting", "Solid result", "Major advance",
         "Breakthrough"]
LABELS = {
    "ramsey-hypergraphs": "hypergraph Ramsey\n(GPT-5.4 Pro)",
    "q2-absolute-galois": "Gal. group of Q$_2$\n(Claude Fable 5)",
    "superpermutations": "superpermutations\n(GPT-5.6 Sol)",
    "genus-2-jacobian-torsion": "genus-2 torsion\n(GPT-5.6 Sol)",
    "inverse-galois": "inverse Galois M$_{23}$\n(scored human)",
    "hadamard": "Hadamard 668\n(Claude)",
}
# Hand-placed offsets keep neighbouring labels off each other and off the
# lane above; (dx, dy) in points.
OFFSETS = {
    "ramsey-hypergraphs": (0, 12),
    "q2-absolute-galois": (0, 12),
    "superpermutations": (-48, 12),
    "genus-2-jacobian-torsion": (-6, -30),
    "inverse-galois": (0, 12),
    "hadamard": (-4, 12),
}
ANNOUNCED = "2026-02-26"


def main() -> None:
    problems = read_csv(HERE / "frontiermath-open-problems.csv")
    events = read_csv(HERE / "frontiermath-open-solutions.csv")
    dated = [row for row in events if row["date"]]
    undated = [row for row in events if not row["date"]]

    fig, (ax, pool_ax) = plt.subplots(
        1, 2, figsize=(8.4, 5.2), sharey=True,
        gridspec_kw={"width_ratios": [3.0, 1.0], "wspace": 0.05},
    )
    fig.suptitle("FrontierMath Open Problems: solution events",
                 x=0.09, y=0.98, ha="left", fontsize=14, fontweight="bold")
    ax.set_title("Dated solves by date and curator-assigned notability tier",
                 loc="left", fontsize=9.2, color="#444444", pad=12)
    pool_ax.set_title("The pool today", loc="left", fontsize=9.2,
                      color="#444444", pad=12)

    for lane in range(len(TIERS)):
        ax.axhline(lane, color="#d5d5d5", linewidth=0.7, zorder=1)
    by_slug = {row["slug"]: row for row in problems}
    for row in dated:
        tier = by_slug[row["slug"]]["notability"]
        x = year_fraction(row["date"])
        y = TIERS.index(tier)
        colour = AI if row["event"] == "solved_ai" else HUMAN
        ax.scatter([x], [y], s=64, color=colour, edgecolor="white",
                   linewidth=0.8, zorder=4)
        dx, dy = OFFSETS[row["slug"]]
        ax.annotate(
            LABELS[row["slug"]],
            (x, y),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.4,
            color=colour,
            ha="center",
            linespacing=1.25,
        )
    launch = year_fraction(ANNOUNCED)
    ax.axvline(launch, color="#777777", linestyle=":", linewidth=1.1, zorder=2)
    ax.text(launch + 0.008, 0.965, "benchmark announced",
            transform=ax.get_xaxis_transform(), fontsize=8, color="#555555",
            ha="left", va="top")

    left = year_fraction("2026-02-01")
    right = NOW + 0.028
    ax.set_xlim(left, right)
    ax.set_ylim(-0.75, 3.55)
    ax.set_yticks(range(len(TIERS)))
    ax.set_yticklabels(TIERS, fontsize=8.5)
    months = [f"2026-{month:02d}" for month in range(2, 9, 2)]
    ax.set_xticks([year_fraction(month) for month in months])
    ax.set_xticklabels(months, fontsize=8.5)
    shade_era(ax, right)
    style(ax, "", xlabel="Month")
    note = (f"{len(problems)} problem pages; "
            f"{len(dated) + len(undated)} recorded solves.\nNot drawn: "
            f"{len(undated)} undated AI solve on a problem\nwithdrawn from "
            "the pool.")
    ax.text(0.03, 0.03, note, transform=ax.transAxes, fontsize=8.2,
            color="#333333", va="bottom", linespacing=1.4)

    # The denominator panel: the whole pool as one stacked bar per tier, so
    # every event on the left is read against what still stands. Open rows
    # use the cumulative page's open colour; the solved slivers reuse the
    # event colours.
    for lane, tier in enumerate(TIERS):
        in_tier = [row for row in problems if row["notability"] == tier]
        open_count = sum(row["status"] == "unsolved" for row in in_tier)
        ai_count = sum(row["status"] == "solved_ai" for row in in_tier)
        human_count = sum(row["status"] == "solved_human" for row in in_tier)
        base = 0
        for count, colour in ((open_count, OPEN_COLOUR), (ai_count, AI),
                              (human_count, HUMAN)):
            if count:
                pool_ax.barh(lane, count, left=base, height=0.42,
                             color=colour, edgecolor="white", linewidth=0.6,
                             zorder=3)
            base += count
        solved = ai_count + human_count
        reading = (f"{open_count} of {base} open" if solved
                   else f"all {base} open")
        # Above the bar rather than beside it: the panel is too narrow for a
        # side label next to a 23-problem bar. Grey needs no legend — every
        # reading names it — and the solved slivers reuse the event colours
        # the timeline already labels.
        pool_ax.text(0.3, lane + 0.28, reading, fontsize=7.6,
                     color="#555555", va="bottom")
    pool_ax.set_xlim(0, 24.5)
    pool_ax.set_xticks([0, 10, 20])
    style(pool_ax, "", xlabel="Problems")
    pool_ax.grid(axis="y", visible=False)
    pool_ax.tick_params(labelleft=False)

    source_note(fig, "Source: epoch.ai problem pages, vendored as "
                     "frontiermath-open-problems.csv and "
                     "frontiermath-open-solutions.csv.")
    save(
        fig,
        HERE / "discovery-math-frontiermath-open.png",
        "FrontierMath Open Problems: dated solution events by notability "
        "tier, with the surviving pool per tier.",
        ["https://epoch.ai/frontiermath/open-problems"],
        __file__,
        adjust={"left": 0.175},
    )

    events_chart(
        HERE / "cumulative-math-frontiermath-open.png",
        title="FrontierMath Open Problems",
        ylabel="Problems marked solved",
        dates=sorted(row["date"] for row in dated),
        source_label="epoch.ai problem pages",
        source_url="https://epoch.ai/frontiermath/open-problems",
        built_by=__file__,
        subtitle="Cumulative dated solution events; one undated solve omitted",
    )


if __name__ == "__main__":
    main()
