#!/usr/bin/env python3
"""Draw discovery-algorithms-cifar10.png and cumulative-algorithms-cifar10.png
from this folder's record table.

Run: python3 problems/algorithms-cifar10/figure.py

The 2018 row is dropped: it was run on V100s, and a time on other hardware is
not a point on this curve.
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
from lib.cumulative import staircase_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402
from matplotlib.ticker import NullFormatter, ScalarFormatter  # noqa: E402


def cumulative() -> None:
    rows = [row for row in read_csv(HERE / "cifar-speedrun-records.csv") if row["date"] >= "2022"]
    staircase_chart(
        HERE / "cumulative-algorithms-cifar10.png",
        title="CIFAR-10 speedrun: standing record",
        subtitle="Seconds to 94% accuracy on one A100; lower is better",
        ylabel="Seconds to 94% accuracy",
        series=[("", [year_fraction(row["date"]) for row in rows],
                 [float(row["seconds"]) for row in rows])],
        ylog=True,
        source_label="dates assembled from releases and announcements in "
                     "cifar-speedrun-records.csv; no official ledger exists",
        source_url="https://github.com/KellerJordan/cifar10-airbench",
        built_by=__file__,
        note="Lower is better.",
    )


def main() -> None:
    rows = [row for row in read_csv(HERE / "cifar-speedrun-records.csv") if row["date"] >= "2022"]
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["seconds"]) for row in rows]
    fig, ax = new_chart(
        "CIFAR-10 speedrun",
        "Seconds to 94% accuracy on one A100; lower is better",
    )
    ax.plot(xs + [NOW], ys + [ys[-1]], drawstyle="steps-post", color=NEUTRAL, linewidth=1.5)
    for x, y, row in zip(xs, ys, rows):
        colour = AI if row["agent"] == "ai" else HUMAN
        uncertain = row["date_precision"] == "undated" or row["acknowledged"] == "no"
        ax.scatter(
            [x],
            [y],
            s=55,
            facecolor="none" if uncertain else colour,
            edgecolor=colour,
            linewidth=1.5 if uncertain else 0.7,
            zorder=4,
        )
        if row["agent"] == "ai":
            label = (
                "Hiverge"
                if row["acknowledged"] == "yes"
                else "Fulcrum/Fable\nunacknowledged"
            )
            offset = (-5, 8) if row["acknowledged"] == "yes" else (-7, 11)
            ax.annotate(
                label,
                (x, y),
                xytext=offset,
                textcoords="offset points",
                ha="right",
                fontsize=7.5,
                color=AI,
            )
    right = NOW + 0.15
    ax.set_xlim(min(xs) - 0.08, right)
    ax.set_yscale("log")
    ax.set_yticks([2, 3, 5, 10, 20])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    shade_era(ax, right)
    style(ax, "Seconds to 94% accuracy (log scale)", "Record date")
    ax.legend(handles=common_legend(pending=True), frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.14,
        "The open red 1.828 s point is unacknowledged\nand carries specification-gaming caveats.",
        transform=ax.transAxes,
        fontsize=8.3,
    )
    source_note(fig, "Source: dates assembled from releases and announcements in cifar-speedrun-records.csv; no official ledger exists.")
    save(
        fig,
        HERE / "discovery-algorithms-cifar10.png",
        "CIFAR-10 speedrun records on one A100 with AI and uncertain records marked.",
        ["https://github.com/KellerJordan/cifar10-airbench"],
        __file__,
    )


if __name__ == "__main__":
    main()
    cumulative()
