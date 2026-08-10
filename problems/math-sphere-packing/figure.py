#!/usr/bin/env python3
"""Draw discovery-math-sphere-packing.png from this folder's record ladder.

Run: python3 problems/math-sphere-packing/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib.ticker import MaxNLocator  # noqa: E402

from lib.chart import (  # noqa: E402
    HUMAN,
    NOW,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "sphere-packing-lower-bound-records.csv")
    years = [int(row["year"]) for row in rows]
    steps = list(range(1, len(rows) + 1))
    fig, ax = new_chart(
        "Sphere-packing lower-bound ladder",
        "Cumulative improvements because the bound changes functional form and cannot share one numeric y-axis",
    )
    ax.plot(years + [NOW], steps + [steps[-1]], drawstyle="steps-post", color=HUMAN, linewidth=2)
    ax.scatter(years, steps, color=HUMAN, s=52, edgecolor="white", linewidth=0.7, zorder=4)
    for index, row in enumerate(rows):
        if row["year"] in {"1905", "1947", "1992", "2013", "2023", "2025"}:
            ax.annotate(
                row["finder"].split(" (")[0],
                (years[index], steps[index]),
                xytext=(-4, 8),
                textcoords="offset points",
                fontsize=7.5,
                color=HUMAN,
                ha="right",
            )
    right = 2032
    ax.set_xlim(1898, right)
    ax.set_ylim(0.4, len(rows) + 1.2)
    shade_era(ax, right)
    style(ax, "Cumulative improvements to the bound")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.text(
        0.98,
        0.12,
        "The two newest steps, 2023 and 2025,\nare human proofs; no AI step is in this ladder.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, "Source URLs are carried row-by-row in sphere-packing-lower-bound-records.csv.")
    save(
        fig,
        HERE / "discovery-math-sphere-packing.png",
        "Cumulative improvements in the asymptotic sphere-packing lower-bound ladder.",
        sorted({row["source_url"] for row in rows}),
        __file__,
    )


if __name__ == "__main__":
    main()
