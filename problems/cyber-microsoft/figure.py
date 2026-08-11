#!/usr/bin/env python3
"""Draw discovery-cyber-microsoft.png from this folder's annual CVE counts.

Run: python3 problems/cyber-microsoft/figure.py

Stacked annual bars of Microsoft-issued CVEs split by what the acknowledgment
credit names, in the same bands and colours as the Firefox series so the two
vendors can be read side by side. The 2026 bar is a part year and is outlined.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    FUZZ,
    HUMAN,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.table import read_csv  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

# Affiliation-only credits are drawn in a lighter red than corroborated method
# credits: same family, visibly weaker evidence. Matches cyber-firefox.
AI_AFFILIATED = "#e09a8c"


def main() -> None:
    rows = read_csv(HERE / "msrc-cves.csv")
    years = [int(row["year"]) for row in rows]
    other = [int(row["other"]) for row in rows]
    fuzz = [int(row["fuzz"]) for row in rows]
    affiliated = [int(row["ai_affiliated"]) for row in rows]
    explicit = [int(row["explicit_ai"]) for row in rows]
    totals = [int(row["cves"]) for row in rows]

    fig, ax = new_chart(
        "Microsoft security-update CVEs",
        "CVEs issued by Microsoft's own CNA per year, split by what the "
        "acknowledgment credit names",
    )
    ax.bar(years, other, color=HUMAN, width=0.76, label="human or uncredited", zorder=3)
    bottoms = list(other)
    ax.bar(years, fuzz, bottom=bottoms, color=FUZZ, width=0.76, label="fuzzer", zorder=3)
    bottoms = [b + f for b, f in zip(bottoms, fuzz)]
    ax.bar(years, affiliated, bottom=bottoms, color=AI_AFFILIATED, width=0.76,
           label="AI-affiliated; method unstated", zorder=3)
    bottoms = [b + a for b, a in zip(bottoms, affiliated)]
    ax.bar(years, explicit, bottom=bottoms, color=AI, width=0.76,
           label="names an AI system or method", zorder=3)

    partial = [i for i, row in enumerate(rows) if row.get("partial_year") == "yes"]
    for index in partial:
        ax.bar(years[index], totals[index], width=0.76, facecolor="none",
               edgecolor="#444444", linewidth=1.3, zorder=4)
        ax.annotate("partial year", (years[index], totals[index]), xytext=(-4, 7),
                    textcoords="offset points", ha="right", fontsize=8, color="#555555")

    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(totals) * 1.28)
    shade_era(ax, right, annual=True)
    style(ax, "CVEs that year")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    handles = [
        Patch(facecolor=HUMAN, label="human or uncredited"),
        Patch(facecolor=FUZZ, label="fuzzer"),
        Patch(facecolor=AI_AFFILIATED, label="AI-affiliated; method unstated"),
        Patch(facecolor=AI, label="names an AI system or method"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8, ncol=2, loc="upper left")
    if partial:
        latest = rows[partial[-1]]
        ai_marked = int(latest["explicit_ai"]) + int(latest["ai_affiliated"])
        ax.text(
            0.02, 0.72,
            f"{latest['cves']} CVEs in partial {latest['year']} "
            f"through {latest['data_through']}\n"
            f"{ai_marked} carry any AI marker — "
            f"{100 * ai_marked / int(latest['cves']):.1f}% of the part year",
            transform=ax.transAxes, fontsize=9, color="#333333", va="top",
        )
    source_note(
        fig,
        "Source: MSRC Security Update Guide, counted in the vendored CSV. "
        "Credits are textual markers, not audited causation.",
    )
    save(
        fig,
        HERE / "discovery-cyber-microsoft.png",
        "Microsoft security-update CVEs per year split by acknowledgment credit, "
        "with the 2026 bar drawn as a partial year.",
        ["https://api.msrc.microsoft.com/cvrf/v3.0/updates"],
        __file__,
    )


if __name__ == "__main__":
    main()
