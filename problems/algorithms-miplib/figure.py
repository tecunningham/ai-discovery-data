#!/usr/bin/env python3
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
    rows = read_csv(HERE / "miplib-solution-releases.csv")
    better, optima, first = Counter(), Counter(), Counter()
    for row in rows:
        year = int(row["release_date"][:4])
        better[year] += int(row["better_incumbents"])
        optima[year] += int(row["new_optimal_solutions"]) + int(row["optimal_status_only"])
        first[year] += int(row["first_known_feasible"])
    years = list(range(2019, 2027))
    fig, ax = chart.new_chart(
        "MIPLIB 2017 solution frontier",
        "Public solufile releases; better incumbents, first feasible solutions and optimality updates",
    )
    a = [better[y] for y in years]
    b = [first[y] for y in years]
    c = [optima[y] for y in years]
    ax.bar(years, a, width=0.76, color=chart.UNATTRIBUTED, zorder=3)
    ax.bar(years, b, width=0.76, bottom=a, color="#7694a0", zorder=3)
    ax.bar(years, c, width=0.76, bottom=[x + y for x, y in zip(a, b)],
           color=chart.NEUTRAL, zorder=3)
    right = 2027.0
    ax.set_xlim(2018.3, right)
    ax.set_ylim(0, max(x + y + z for x, y, z in zip(a, b, c)) * 1.18)
    chart.shade_era(ax, right, annual=True)
    chart.style(ax, "Solution-frontier updates")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.legend(handles=[
        Patch(facecolor=chart.UNATTRIBUTED, label="better incumbent"),
        Patch(facecolor="#7694a0", label="first feasible"),
        Patch(facecolor=chart.NEUTRAL, label="optimality update"),
    ], frameon=False, fontsize=8, ncol=3, loc="upper left")
    chart.source_note(fig, "Source: MIPLIB 2017 News Log. Categories follow the log's wording.")
    chart.save(fig, HERE / "discovery-algorithms-miplib.png",
               "MIPLIB 2017 solution frontier. Annual release-log counts, 2019–2026.",
               ["https://miplib.zib.de/news.html"], __file__)


if __name__ == "__main__":
    main()
