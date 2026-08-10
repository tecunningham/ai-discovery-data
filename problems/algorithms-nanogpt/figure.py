#!/usr/bin/env python3
"""Draw discovery-algorithms-nanogpt.png from this folder's record table.

Run: python3 problems/algorithms-nanogpt/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    NEUTRAL,
    NOW,
    common_legend,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402
from matplotlib.ticker import NullFormatter, ScalarFormatter  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "nanogpt-records.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["minutes"]) for row in rows]
    fig, ax = new_chart(
        "modded-nanogpt training speedrun",
        "All 86 listed runs: minutes to the fixed target loss; lower is better",
    )
    ax.plot(xs + [NOW], ys + [ys[-1]], drawstyle="steps-post", color=NEUTRAL, linewidth=1.5)
    for x, y, row in zip(xs, ys, rows):
        colour = AI if row["agent"] == "ai" else HUMAN
        ax.scatter([x], [y], color=colour, s=48 if colour == AI else 20, edgecolor="white", linewidth=0.5, zorder=4)
        if row["ai_system"]:
            ax.annotate(row["ai_system"], (x, y), xytext=(3, 7), textcoords="offset points", fontsize=7, color=AI)
    right = NOW + 0.12
    ax.set_xlim(min(xs) - 0.08, right)
    ax.set_yscale("log")
    ax.set_yticks([1.5, 2, 3, 5, 10, 20, 45])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    shade_era(ax, right)
    style(ax, "Minutes to target loss (log scale)", "Date of run")
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    ax.text(0.02, 0.13, "45 → 1.27 minutes; 4 of 86 listed runs are AI-credited.", transform=ax.transAxes, fontsize=8.5)
    source_note(fig, "Source: KellerJordan/modded-nanogpt README, vendored as nanogpt-records.csv.")
    save(
        fig,
        HERE / "discovery-algorithms-nanogpt.png",
        "modded-nanogpt training-speed records with credited AI systems marked.",
        ["https://github.com/KellerJordan/modded-nanogpt"],
        __file__,
    )


if __name__ == "__main__":
    main()
