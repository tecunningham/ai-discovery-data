#!/usr/bin/env python3
"""Draw discovery-cyber-firefox.png from this folder's annual advisory counts.

Run: python3 problems/cyber-firefox/figure.py

The main chart counts distinct CVE IDs, because one vulnerability repeated across
the Firefox, Firefox ESR and Thunderbird advisories of a release is one
discovery. The advisory-CVE mention count that the series used to plot becomes a
second, smaller sensitivity chart: it is an order of magnitude larger by 2026 and
sharing an axis with it would flatten the series the folder is actually about.
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
    VENDOR,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.table import read_csv  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

# Affiliation-only credits are drawn in a lighter red than corroborated method
# credits: same family, visibly weaker evidence.
AI_AFFILIATED = "#e09a8c"


def main() -> None:
    rows = read_csv(HERE / "firefox-advisories.csv")
    years = [int(row["year"]) for row in rows]
    other = [int(row["unique_other"]) for row in rows]
    fuzz = [int(row["unique_fuzz"]) for row in rows]
    affiliated = [int(row["unique_ai_affiliated"]) for row in rows]
    explicit = [int(row["unique_explicit_ai"]) for row in rows]
    unique = [int(row["unique_cves"]) for row in rows]
    mentions = [int(row["total"]) for row in rows]

    fig, ax = new_chart(
        "Firefox vulnerability disclosures",
        "Distinct CVEs per year, split by what the reporter credit names",
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
        ax.bar(years[index], unique[index], width=0.76, facecolor="none",
               edgecolor="#444444", linewidth=1.3, zorder=4)
        ax.annotate("partial year", (years[index], unique[index]), xytext=(-4, 7),
                    textcoords="offset points", ha="right", fontsize=8, color="#555555")

    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(unique) * 1.3)
    shade_era(ax, right, annual=True)
    style(ax, "Distinct CVEs that year")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    handles = [
        Patch(facecolor=HUMAN, label="human or uncredited"),
        Patch(facecolor=FUZZ, label="fuzzer"),
        Patch(facecolor=AI_AFFILIATED, label="AI-affiliated; method unstated"),
        Patch(facecolor=AI, label="names an AI system or method"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8, ncol=2)
    if partial:
        latest = rows[partial[-1]]
        through = (f" through {latest['data_through']}"
                   if latest.get("data_through") else "")
        ax.text(
            0.02, 0.78,
            f"{latest['unique_cves']} distinct CVEs in partial {latest['year']}"
            f"{through}\n{latest['unique_explicit_ai']} name an AI system or method; "
            f"{latest['unique_ai_affiliated']} name only an AI-security employer",
            transform=ax.transAxes, fontsize=9, color="#333333", va="top",
        )
    source_note(
        fig,
        "Source: Mozilla foundation-security-advisories, counted in the vendored CSV. "
        "Credits are textual markers, not audited causation.",
    )
    save(
        fig,
        HERE / "discovery-cyber-firefox.png",
        "Firefox vulnerability disclosures. Distinct CVEs per year split by reporter "
        "credit, with the 2026 bar drawn as a partial year.",
        ["https://github.com/mozilla/foundation-security-advisories"],
        __file__,
    )
    sensitivity(rows, years, unique, mentions)


def sensitivity(rows, years, unique, mentions) -> None:
    """Draw the two counting units side by side.

    The gap between them is Mozilla's packaging, not discovery: it widens
    whenever more products ship the same fix, which is why the folder does not
    plot mentions as its headline.
    """
    fig, ax = new_chart(
        "Firefox: two ways of counting the same year",
        "Advisory–CVE mentions against distinct CVE IDs",
    )
    ax.plot(years, mentions, color=VENDOR, linewidth=1.6, linestyle=(0, (4, 3)),
            marker="o", markersize=3.5, label="advisory–CVE mentions", zorder=4)
    ax.plot(years, unique, color=HUMAN, linewidth=1.8, marker="o", markersize=3.5,
            label="distinct CVE IDs", zorder=5)
    ratio = [m / u for m, u in zip(mentions, unique)]
    ax.text(0.03, 0.80,
            f"{ratio[0]:.1f} mentions per distinct CVE in {years[0]}\n"
            f"{ratio[-1]:.1f} in {years[-1]}",
            transform=ax.transAxes, fontsize=9, color="#333333", va="top")
    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(mentions) * 1.18)
    shade_era(ax, right, annual=True)
    style(ax, "Count that year")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.legend(frameon=False, fontsize=8)
    source_note(
        fig,
        "Source: Mozilla foundation-security-advisories. The gap is advisory "
        "packaging across Firefox, ESR and Thunderbird, not extra discoveries.",
    )
    save(
        fig,
        HERE / "counting-units-cyber-firefox.png",
        "Advisory–CVE mentions per year against distinct CVE IDs per year for Firefox.",
        ["https://github.com/mozilla/foundation-security-advisories"],
        __file__,
    )


if __name__ == "__main__":
    main()
