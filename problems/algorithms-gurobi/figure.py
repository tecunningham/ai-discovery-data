#!/usr/bin/env python3
"""Draw discovery-algorithms-gurobi.png from this folder's release speedups.

Run: python3 problems/algorithms-gurobi/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    NOW,
    VENDOR,
    common_legend,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "gurobi-milp-speedups.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    factors = []
    cumulative = 1.0
    for row in rows:
        cumulative *= float(row["release_speedup"])
        factors.append(cumulative)
    fig, ax = new_chart(
        "Gurobi mixed-integer programming speed",
        "Cumulative vendor-reported speedup over v9.5; fixed-machine release comparisons",
    )
    ax.plot([2022.0] + xs + [NOW], [1.0] + factors + [factors[-1]], drawstyle="steps-post", color=VENDOR, linewidth=2)
    ax.scatter(xs, factors, color=VENDOR, s=55, edgecolor="white", linewidth=0.7, zorder=4)
    for x, y, row in zip(xs, factors, rows):
        ax.annotate(row["release"], (x, y), xytext=(4, -12), textcoords="offset points", fontsize=8, color=VENDOR)
    right = NOW + 0.3
    ax.set_xlim(2022, right)
    ax.set_ylim(0.95, max(factors) * 1.2)
    shade_era(ax, right)
    style(ax, "Cumulative speedup since v9.5")
    ax.legend(handles=common_legend(vendor=True), frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.9,
        f"×{factors[-1]:.2f} across four releases.\nNo AI credit in the release notes.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: Gurobi release announcements; vendor-run figures, transcribed with URLs in gurobi-milp-speedups.csv.")
    save(
        fig,
        HERE / "discovery-algorithms-gurobi.png",
        "Cumulative Gurobi vendor-reported MILP speedup across releases 10 through 13.",
        [row["source_url"] for row in rows],
        __file__,
    )


if __name__ == "__main__":
    main()
