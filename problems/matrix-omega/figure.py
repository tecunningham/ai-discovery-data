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
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "matrix-multiplication-omega.csv")
    years = [int(row["year"]) for row in rows]
    values = [float(row["omega"]) for row in rows]
    fig, ax = new_chart(
        "Matrix-multiplication exponent ω",
        "Best proved asymptotic upper bound; lower is better and every recorded step is human",
    )
    ax.plot(years + [NOW], values + [values[-1]], drawstyle="steps-post", color=HUMAN, linewidth=2)
    ax.scatter(years, values, color=HUMAN, s=45, edgecolor="white", linewidth=0.6, zorder=4)
    ax.axhline(2, color=VENDOR, linestyle=":", linewidth=1)
    ax.text(1970, 2.025, "conjectured limit = 2", fontsize=8, color="#555555")
    for target in ("Strassen", "Coppersmith–Winograd", "Alman et al."):
        row = next(row for row in rows if row["discoverer"] == target)
        ax.annotate(
            target,
            (int(row["year"]), float(row["omega"])),
            xytext=(5, 7),
            textcoords="offset points",
            fontsize=7.5,
            color=HUMAN,
        )
    right = 2030
    ax.set_xlim(1965, right)
    ax.set_ylim(1.96, 2.9)
    shade_era(ax, right)
    style(ax, "Best proved upper bound on ω")
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    # Counted at plot time rather than written into the caption, so re-vendoring
    # the chronology cannot leave the annotation asserting a stale count.
    recent = [value for year, value in zip(years, values) if year >= 2010]
    earlier = [value for year, value in zip(years, values) if year < 2010]
    ax.text(
        0.98,
        0.22,
        f"{len(recent)} human improvements since 2010, worth "
        f"{earlier[-1] - recent[-1]:.4f} together;\nno LLM-attributed step in the series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, "Source: matrix-multiplication-omega.csv; secondary chronology matching the existing source-log transcription.")
    save(
        fig,
        HERE / "discovery-matrix-omega.png",
        "Best proved upper bound on the matrix-multiplication exponent over time.",
        sorted({row["source_url"] for row in rows}),
        __file__,
    )


if __name__ == "__main__":
    main()
