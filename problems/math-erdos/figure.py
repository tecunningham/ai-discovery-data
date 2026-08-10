#!/usr/bin/env python3
"""Draw discovery-math-erdos.png from this folder's monthly catalogue snapshots.

Run: python3 problems/math-erdos/figure.py
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
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "erdos-database-history.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    solved = [int(row["total_solved"]) for row in rows]
    total = [int(row["total_problems"]) for row in rows]
    lean = [int(row["lean_formalized"]) for row in rows]
    fig, ax = new_chart(
        "Erdős problems: catalogue status over time",
        "Site snapshots, not historical solution dates; the comparable window is only eleven months",
    )
    ax.plot(xs, total, drawstyle="steps-post", color=NEUTRAL, linestyle="--", linewidth=1.7, label="catalogued")
    ax.plot(xs, solved, drawstyle="steps-post", color=HUMAN, linewidth=2, marker="o", markersize=4, label="marked solved")
    ax.plot(xs, lean, drawstyle="steps-post", color="#8a6fb8", linestyle=":", linewidth=1.7, label="Lean-formalized")
    right = max(xs) + 0.08
    ax.set_xlim(min(xs) - 0.04, right)
    ax.set_ylim(0, max(total) * 1.16)
    shade_era(ax, right)
    style(ax, "Problems", "Site snapshot")
    tick_idx = list(range(0, len(rows), 2))
    if tick_idx[-1] != len(rows) - 1:
        tick_idx.append(len(rows) - 1)
    ax.set_xticks([xs[i] for i in tick_idx])
    ax.set_xticklabels([rows[i]["month"] for i in tick_idx], rotation=30, ha="right")
    # The AI-standalone stock (~13) is two orders of magnitude below the
    # catalogue stocks, so plot it as a callout rather than a point on this axis.
    ax.text(
        0.98,
        0.18,
        "Separate stock (wiki freeze 2026-06-30):\n"
        "~13 full AI-standalone resolutions\n"
        f"vs {solved[-1]} statuses marked solved",
        transform=ax.transAxes,
        fontsize=8.5,
        color=AI,
        ha="right",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=AI, linewidth=0.8, alpha=0.92),
    )
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    source_note(fig, "Source: teorth/erdosproblems statistics and the AI-resolution wiki; stocks are not an AI-vs-human flow.")
    save(
        fig,
        HERE / "discovery-math-erdos.png",
        "Erdős problem catalogue stocks and a separately counted AI-resolution stock.",
        ["https://github.com/teorth/erdosproblems"],
        __file__,
    )


if __name__ == "__main__":
    main()
