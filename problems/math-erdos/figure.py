#!/usr/bin/env python3
"""Draw this folder's four figures.

Run: python3 problems/math-erdos/figure.py

discovery-math-erdos.png plots the monthly catalogue snapshots;
erdos-solution-years.png plots the imputed solution years from
erdos-solution-years.csv; erdos-surge-anatomy.png dissects the 2024–2026
surge; cumulative-math-erdos.png redraws the snapshots as open problems
remaining, for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import matplotlib.pyplot as plt  # noqa: E402

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
from lib.cumulative import remaining_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

# arXiv preprints sit between "published" and "wiki entry" in how settled they
# are, so they take a lighter shade of the human blue rather than a new hue.
PREPRINT = "#8fb3d9"


def solution_years() -> None:
    rows = read_csv(HERE / "erdos-solution-years.csv")
    dated = [row for row in rows if row["solution_year"]]
    undated = len(rows) - len(dated)
    first = min(int(row["solution_year"]) for row in dated)
    years = list(range(first, 2027))
    by_basis = {
        basis: [sum(int(row["solution_year"]) == year and row["basis"] == basis
                    for row in dated) for year in years]
        for basis in ("solving_citation", "review", "ai_wiki")}
    human = [a + b for a, b in zip(by_basis["solving_citation"],
                                   by_basis["review"])]
    fig, ax = new_chart(
        "Erdős problems: imputed solution years",
        "Publication year of the resolving reference on each solved problem's page,"
        " not the status-edit date",
    )
    ax.bar(years, human, width=0.85, color=HUMAN,
           label="solving reference in the literature")
    ax.bar(years, by_basis["ai_wiki"], width=0.85, bottom=human, color=AI,
           label="AI wiki full solution only")
    right = 2026 + 1.2
    ax.set_xlim(first - 1.5, right)
    tallest = max(h + a for h, a in zip(human, by_basis["ai_wiki"]))
    ax.set_ylim(0, tallest * 1.18)
    shade_era(ax, right, annual=True)
    style(ax, "Problems first resolved", "Imputed solution year")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.text(
        0.02,
        0.78,
        f"{len(dated)} of {len(rows)} solved problems dated;\n"
        f"{undated} state no dateable resolution",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#555555",
        ha="left",
        va="top",
    )
    source_note(fig, "Source: erdosproblems.com problem pages and the "
                     "AI-resolution wiki; years are imputed, see README.")
    save(
        fig,
        HERE / "erdos-solution-years.png",
        "Imputed solution years for the solved problems in the Erdős catalogue.",
        ["https://www.erdosproblems.com/"],
        __file__,
    )


def surge_anatomy() -> None:
    rows = read_csv(HERE / "erdos-solution-years.csv")
    dated = [row for row in rows if row["solution_year"]]
    history = read_csv(HERE / "erdos-database-history.csv")
    first_snapshot = int(history[0]["total_problems"])

    fig, (left, right) = plt.subplots(1, 2, figsize=(8.4, 4.9))
    fig.suptitle("Erdős problems: anatomy of the 2024–2026 surge",
                 x=0.09, y=0.98, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.09, 0.895,
             "What kind of record dates each solution, and where the solved "
             "problems sit in the catalogue's own ordering",
             fontsize=9.2, color="#444444")

    # Left: what dates each recent solution. "published" has a venue in the
    # page's bibliography, "preprint" is arXiv-only, "AI wiki" has no citable
    # record at all. The one "stated" row (1978) is outside this window.
    years = list(range(2015, 2027))
    kinds = [("published", HUMAN, "published paper"),
             ("preprint", PREPRINT, "arXiv preprint only"),
             ("ai_wiki", AI, "AI-wiki entry only")]
    bottom = [0] * len(years)
    for kind, colour, label in kinds:
        counts = [sum(row["solution_year"] == str(year)
                      and row["reference_kind"] == kind for row in dated)
                  for year in years]
        left.bar(years, counts, width=0.85, bottom=bottom, color=colour,
                 label=label)
        bottom = [b + c for b, c in zip(bottom, counts)]
    left.set_xlim(2014.3, 2026.7)
    left.set_ylim(0, max(bottom) * 1.15)
    shade_era(left, 2026.7, annual=True)
    style(left, "Problems first resolved", "Imputed solution year")
    left.legend(frameon=False, fontsize=8, loc="upper left")

    # Right: solution year against the problem's catalogue number, which is
    # the order the site assigned numbers. Points above the line were not yet
    # catalogued at the first snapshot; an old solution up there is literature
    # archaeology (added already solved), a recent solution below it is a
    # problem that sat in the catalogue as open and then fell.
    colour_of = {"published": HUMAN, "stated": HUMAN,
                 "preprint": PREPRINT, "ai_wiki": AI}
    for kind, colour in colour_of.items():
        xs = [int(row["solution_year"]) for row in dated
              if row["reference_kind"] == kind]
        ys = [int(row["problem"]) for row in dated
              if row["reference_kind"] == kind]
        right.scatter(xs, ys, s=9, color=colour, alpha=0.65, linewidths=0)
    right.axhline(first_snapshot, color="#555555", linewidth=0.9,
                  linestyle="--")
    right.text(1942, first_snapshot + 25,
               f"catalogued by {history[0]['month']} "
               f"(problems 1–{first_snapshot})",
               fontsize=7.5, color="#555555", va="bottom")
    right.set_xlim(1938, 2028)
    right.set_ylim(0, 1260)
    shade_era(right, 2028)
    style(right, "Problem number (order of cataloguing)",
          "Imputed solution year")

    source_note(fig, "Source: erdosproblems.com problem pages and the "
                     "AI-resolution wiki; one paper can resolve several "
                     "problems.")
    save(
        fig,
        HERE / "erdos-surge-anatomy.png",
        "Composition of recent Erdős-problem solutions and their position "
        "in the catalogue.",
        ["https://www.erdosproblems.com/"],
        __file__,
        adjust={"top": 0.82, "wspace": 0.28, "left": 0.08},
    )


def cumulative() -> None:
    rows = read_csv(HERE / "erdos-database-history.csv")
    first_total = int(rows[0]["total_problems"])
    last_total = int(rows[-1]["total_problems"])
    remaining_chart(
        HERE / "cumulative-math-erdos.png",
        title="Erdős problems: open problems remaining",
        subtitle="Catalogued minus marked solved at each site snapshot; "
                 "the catalogue itself keeps growing",
        ylabel="Problems open at snapshot",
        xs=[year_fraction(row["date"]) for row in rows],
        ys=[int(row["total_problems"]) - int(row["total_solved"]) for row in rows],
        source_label="teorth/erdosproblems statistics history",
        source_url="https://github.com/teorth/erdosproblems",
        built_by=__file__,
        note=f"catalogue grew from {first_total} to {last_total} problems "
             "across the window",
    )


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
    solution_years()
    surge_anatomy()
    cumulative()
