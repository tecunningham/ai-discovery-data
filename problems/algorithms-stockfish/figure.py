#!/usr/bin/env python3
"""Draw discovery-algorithms-stockfish.png from this folder's build tests.

Run: python3 problems/algorithms-stockfish/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    common_legend,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402

# The date of the commit the red marker records; see the README's LLM section.
# Pinned here so a refetch that appends newer builds cannot silently drag the
# marker to whatever the new last row happens to be.
LLM_COMMIT_DATE = "2026-07-26"


def main() -> None:
    rows = read_csv(HERE / "stockfish-ncm-elo.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["elo_vs_sf15"]) for row in rows]
    # Eight builds share the commit's date, spanning about three Elo, so "the
    # build to mark" is a choice rather than a lookup. The file keeps upstream's
    # test order, and the last row on that date is the last build tested; taking
    # the maximum instead would report whichever run got the luckiest 20,000
    # games.
    latest = [row for row in rows if row["date"] == LLM_COMMIT_DATE][-1]
    latest_elo = float(latest["elo_vs_sf15"])
    fig, ax = new_chart(
        "Stockfish development builds on fixed hardware",
        "20,000 games per build against Stockfish 15; releases are marked",
    )
    ax.plot(xs, ys, color="#9fb3cc", linewidth=1, zorder=2)
    releases = [(x, y, row["release"]) for x, y, row in zip(xs, ys, rows) if row["release"]]
    ax.scatter([row[0] for row in releases], [row[1] for row in releases], color=HUMAN, s=35, edgecolor="white", linewidth=0.5, zorder=4)
    llm_x = year_fraction(latest["date"])
    ax.scatter([llm_x], [latest_elo], s=70, facecolor="none", edgecolor=AI, linewidth=1.6, zorder=5)
    ax.annotate(
        "first LLM-credited master commit:\n0.6% speed patch, not an Elo record",
        (llm_x, latest_elo),
        xytext=(-8, -35),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=AI,
    )
    right = 2027
    ax.set_xlim(2013, right)
    shade_era(ax, right)
    style(ax, "Elo relative to Stockfish 15")
    ax.legend(handles=common_legend(pending=True), frameon=False, fontsize=8)
    source_note(fig, "Source: nextchessmove.com fixed-machine development-build tests, vendored as stockfish-ncm-elo.csv.")
    save(
        fig,
        HERE / "discovery-algorithms-stockfish.png",
        "Stockfish fixed-hardware Elo progression with the first LLM-credited commit marked.",
        ["https://nextchessmove.com/dev-builds"],
        __file__,
    )


if __name__ == "__main__":
    main()
