#!/usr/bin/env python3
"""Draw discovery-matrix-omega.png from this folder's chronology of ω.

Run: python3 problems/matrix-omega/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    NOW,
    VENDOR,
    common_legend,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.cumulative import staircase_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

CREDIT_COLOURS = {"human": HUMAN, "ai": AI}


def cumulative() -> None:
    rows = read_csv(HERE / "matrix-multiplication-omega.csv")
    staircase_chart(
        HERE / "cumulative-matrix-omega.png",
        title="Matrix-multiplication exponent ω: standing record",
        subtitle="Best proved asymptotic upper bound; lower is better",
        ylabel="Best proved upper bound on ω",
        series=[("", [float(row["year"]) for row in rows],
                 [float(row["omega"]) for row in rows])],
        source_label="matrix-multiplication-omega.csv, a secondary chronology",
        source_url="https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm#Sub-cubic_algorithms",
        built_by=__file__,
        note="Conjectured limit is 2; the 2026 step is AI-credited.",
    )


def main() -> None:
    rows = read_csv(HERE / "matrix-multiplication-omega.csv")
    years = [int(row["year"]) for row in rows]
    values = [float(row["omega"]) for row in rows]
    credits = [row["credit"] for row in rows]
    fig, ax = new_chart(
        "Matrix-multiplication exponent ω",
        "Best proved asymptotic upper bound; lower is better",
    )
    ax.plot(years + [NOW], values + [values[-1]], drawstyle="steps-post", color=HUMAN, linewidth=2)
    for credit, colour in CREDIT_COLOURS.items():
        pts = [(y, v) for y, v, c in zip(years, values, credits) if c == credit]
        if pts:
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], color=colour,
                       s=45, edgecolor="white", linewidth=0.6, zorder=4)
    ax.axhline(2, color=VENDOR, linestyle=":", linewidth=1)
    ax.text(1970, 2.025, "conjectured limit = 2", fontsize=8, color="#555555")
    labels = {
        "Strassen": ("Strassen", (5, 7), "left"),
        "Coppersmith–Winograd": ("Coppersmith–Winograd", (5, 7), "left"),
        "Alman–Duan–Williams–Xu–Xu–Zhou": ("Alman et al.", (5, 7), "left"),
        "Dupont et al.": ("Dupont et al. (AI-credited)", (-2, -15), "right"),
    }
    for target, (label, offset, align) in labels.items():
        # Use the latest record when a discoverer appears more than once.
        row = next(row for row in reversed(rows) if row["discoverer"] == target)
        ax.annotate(
            label,
            (int(row["year"]), float(row["omega"])),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            fontsize=7.5,
            color=CREDIT_COLOURS[row["credit"]],
        )
    right = 2030
    ax.set_xlim(1965, right)
    ax.set_ylim(1.96, 2.9)
    shade_era(ax, right)
    style(ax, "Best proved upper bound on ω")
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    # Counted at plot time rather than written into the caption, so re-vendoring
    # the chronology cannot leave the annotation asserting a stale count.
    baseline = next(value for year, value in zip(years, values) if year == 2010)
    recent = [value for year, value in zip(years, values) if year > 2010]
    ai_years = [str(year) for year, credit in zip(years, credits) if credit == "ai"]
    ai_note = f"{len(ai_years)} AI-credited step{'s' if len(ai_years) != 1 else ''}"
    if ai_years:
        ai_note += f" ({', '.join(ai_years)})"
    ax.text(
        0.98,
        0.22,
        f"{len(recent)} further improvements after 2010, worth "
        f"{baseline - recent[-1]:.4f} together;\n{ai_note} in the series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, "Source: matrix-multiplication-omega.csv; secondary chronology, with the 2026 row from arXiv:2608.16884.")
    save(
        fig,
        HERE / "discovery-matrix-omega.png",
        "Best proved upper bound on the matrix-multiplication exponent over time.",
        sorted({row["source_url"] for row in rows}),
        __file__,
    )


if __name__ == "__main__":
    main()
    cumulative()
