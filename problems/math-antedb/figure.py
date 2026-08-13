#!/usr/bin/env python3
"""Draw this folder's three ANTEDB figures from the sweep of exponent slices.

Run: python3 problems/math-antedb/figure.py

discovery-math-antedb.png counts slice-level record changes per family;
antedb-small-multiples.png plots each slice's raw values;
cumulative-math-antedb.png pools the three families into one line, for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    HUMAN,
    NOW,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.cumulative import events_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

SWEEP = HERE / "antedb-sweep.csv"


def cumulative() -> None:
    # The same event definition as cumulative_changes() — a year in which a
    # slice's best derivable value moves — pooled across all three families
    # into one line for the collection-wide cumulative index.
    series: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    for row in read_csv(SWEEP):
        series[(row["quantity"], row["point"])].append(
            (int(row["year"]), float(row["value_float"])))
    by_year: dict[int, int] = defaultdict(int)
    for values in series.values():
        values.sort()
        previous = values[0][1]
        for year, value in values[1:]:
            if value != previous:
                by_year[year] += 1
                previous = value
    years = sorted(by_year)
    events_chart(
        HERE / "cumulative-math-antedb.png",
        title="ANTEDB exponent records: cumulative changes",
        ylabel="Slice-level record changes to date",
        dates=[str(year) for year in years],
        weights=[float(by_year[year]) for year in years],
        source_label="ANTEDB extraction",
        source_url="https://github.com/teorth/expdb",
        built_by=__file__,
    )


def cumulative_changes() -> None:
    rows = read_csv(SWEEP)
    series: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        series[(row["quantity"], row["point"])].append((int(row["year"]), float(row["value_float"])))
    events: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for (quantity, _point), values in series.items():
        values.sort()
        previous = values[0][1]
        for year, value in values[1:]:
            if value != previous:
                events[quantity][year] += 1
                previous = value
    fig, ax = new_chart(
        "ANTEDB analytic-number-theory exponents",
        "Cumulative slice-level record changes across 58 parameter points; one theorem can move many slices",
    )
    labels = {"mu": r"$\mu$: 20 slices", "A": r"$A$: 19 slices", "beta": r"$\beta$: 19 slices"}
    line_styles = {"mu": "-", "A": "--", "beta": ":"}
    for quantity in ("mu", "A", "beta"):
        cumulative = 0
        xs = [min(events[quantity])]
        ys = [0]
        for year, count in sorted(events[quantity].items()):
            cumulative += count
            xs.append(year)
            ys.append(cumulative)
        xs.append(NOW)
        ys.append(cumulative)
        ax.plot(
            xs,
            ys,
            drawstyle="steps-post",
            color=HUMAN,
            linestyle=line_styles[quantity],
            linewidth=2,
            label=labels[quantity],
        )
    right = 2030
    ax.set_xlim(1915, right)
    shade_era(ax, right)
    style(ax, "Cumulative slice-level improvements")
    ax.legend(frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.88,
        "All plotted changes are derived from human literature.\nNo LLM-attributed step appears in the vendored series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: ANTEDB extraction. Counts are parameter-slice changes, not independent papers or discoveries.")
    save(
        fig,
        HERE / "discovery-math-antedb.png",
        "ANTEDB cumulative record changes across 58 exponent slices, grouped by family.",
        ["https://github.com/teorth/expdb"],
        __file__,
    )


def small_multiples() -> None:
    """One raw time series per panel, for every slice of all three families.

    The four-panel version of this was too dense to read. Small multiples keep
    each series raw, with real values on its own axis, and make the panels
    comparable by giving every one the same framing: y runs from 0 to a little
    above that slice's earliest value, so the fraction of the panel the line
    descends is the fraction of the bound that has been removed. A line hugging
    the top means a century bought almost nothing; a line reaching the floor
    means the bound was eliminated.
    """
    rows: dict[tuple[str, float], list[tuple[int, float]]] = defaultdict(list)
    label_of: dict[tuple[str, float], str] = {}
    for row in read_csv(SWEEP):
        key = (row["quantity"], float(row["point_float"]))
        rows[key].append((int(row["year"]), float(row["value_float"])))
        label_of[key] = row["point"]
    for key in rows:
        rows[key].sort()

    # Ten slices per family, evenly spread over the grid, so each row of the
    # figure reads left to right as the parameter increases.
    families = [
        ("mu", r"\mu", "#2f6cc1"),
        ("A", "A", "#e0a020"),
        ("beta", r"\beta", "#2f8f5b"),
    ]
    # Ten slices per family, hand-picked rather than sampled uniformly, so that
    # the points with standard names and standard conjectures attached are all
    # present: mu(1/2) is the Lindelof exponent, A(3/4) is the slice Ingham
    # bounded in 1940 and Guth-Maynard improved in 2024, and beta near 0.325 is
    # the dead zone. Uniform sampling dropped all three.
    wanted = {
        "mu": [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.975],
        "A": [0.525, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975],
        "beta": [0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.325, 0.4, 0.475],
    }
    chosen: dict[str, list] = {}
    for quantity, _, _ in families:
        points = sorted(k[1] for k in rows if k[0] == quantity)
        if not points:
            chosen[quantity] = []
            continue
        picked = []
        for target in wanted[quantity]:
            nearest = min(points, key=lambda p: abs(p - target))
            if nearest not in picked:
                picked.append(nearest)
        chosen[quantity] = picked

    ncols, nrows = 5, 6
    fig, axes = plt.subplots(nrows, ncols, figsize=(15.0, 15.4))

    panel = 0
    for quantity, symbol, colour in families:
        for point in chosen[quantity]:
            ax = axes[panel // ncols][panel % ncols]
            panel += 1
            series = rows[(quantity, point)]
            xs = [r[0] for r in series] + [2026]
            ys = [r[1] for r in series] + [series[-1][1]]
            first, last = series[0][1], series[-1][1]

            ax.fill_between(xs, 0, ys, step="post", color=colour, alpha=0.13, zorder=1)
            ax.plot(xs, ys, drawstyle="steps-post", lw=1.9, color=colour, zorder=3)
            ax.scatter([r[0] for r in series], [r[1] for r in series], s=13,
                       color=colour, zorder=4, edgecolor="white", linewidth=0.4)

            ax.set_ylim(0, first * 1.14)
            ax.set_xlim(1913, 2030)
            ax.set_xticks([1920, 1960, 2000])
            ax.set_yticks([0, first])
            ax.set_yticklabels(["0", f"{first:.4g}"], fontsize=8)
            ax.tick_params(axis="x", labelsize=8)
            # Both raw values go in the title, where nothing can overlap them.
            ax.set_title(
                f"${symbol}({label_of[(quantity, point)]})$   "
                f"{first:.4g} → {last:.4g}",
                fontsize=9.8, loc="left", pad=5,
            )
            # "last moved" rather than a span between records: every series is
            # observed to the present, so the gap between the first and last
            # record is not the observation window.
            ax.text(0.97, 0.06,
                    f"×{last / first:.2f}\nlast moved {series[-1][0]}\n"
                    f"{len(series)} record" + ("s" if len(series) != 1 else ""),
                    transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=8, color="#555", linespacing=1.35)
            if quantity == "A":
                # The density hypothesis is a real threshold, so mark it where
                # it falls inside the panel.
                if 2 < first * 1.14:
                    ax.axhline(2, color="#666", ls="--", lw=1.0, zorder=2)
            ax.grid(axis="y", alpha=0.18)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)

    for blank in range(panel, nrows * ncols):
        axes[blank // ncols][blank % ncols].axis("off")

    fig.suptitle(
        "Best known value of each exponent over time, one panel per slice\n"
        "Every panel spans 0 to its own starting value, so how far the line drops "
        "is the fraction of the bound removed. Dashed line on the $A$ panels is the "
        "density hypothesis.",
        fontsize=12.5, x=0.008, ha="left", y=0.995,
    )
    # tight_layout picks the margins this panel grid needs; save() then
    # reapplies exactly those, so the shared helper adds its renderer guard and
    # PNG provenance without changing the layout.
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    pars = fig.subplotpars
    save(
        fig,
        HERE / "antedb-small-multiples.png",
        "Best known value of each ANTEDB exponent slice over time, one panel "
        "per slice.",
        ["https://github.com/teorth/expdb"],
        __file__,
        adjust={"left": pars.left, "right": pars.right, "top": pars.top,
                "bottom": pars.bottom, "wspace": pars.wspace,
                "hspace": pars.hspace},
    )


def main() -> None:
    cumulative_changes()
    small_multiples()
    cumulative()


if __name__ == "__main__":
    main()
