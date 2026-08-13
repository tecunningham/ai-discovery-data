#!/usr/bin/env python3
"""Draw the quarterly, impact, counting-units and cumulative Firefox charts.

Run: python3 problems/cyber-firefox/figure.py

The main chart counts distinct CVE IDs by announcement quarter, because one
vulnerability repeated across the Firefox, Firefox ESR and Thunderbird
advisories of a release is one discovery, and the quarterly grain shows where
inside a year a surge landed. The impact heatmap cuts the same per-CVE ledger
by Mozilla's own rating, one count grid per credit band. The advisory-CVE
mention count that the series used to plot stays as a second, smaller
sensitivity chart: it is an order of magnitude larger by 2026 and sharing an
axis with it would flatten the series the folder is actually about.
cumulative-cyber-firefox.png redraws the quarterly counts as a running total
for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    AI_SOFT,
    FUZZ,
    HUMAN,
    VENDOR,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked, severity_heatmap  # noqa: E402
from lib.table import read_csv  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

SOURCE_URL = "https://github.com/mozilla/foundation-security-advisories"

# Affiliation-only credits are drawn in a lighter red than corroborated method
# credits: same family, visibly weaker evidence.
AI_AFFILIATED = AI_SOFT


def undated_cves() -> int:
    """Ledger rows with no parseable announcement date.

    They carry a year but no quarter, so they are present in the annual counts
    and absent from every quarterly total; the charts that mix the two grains
    state the gap rather than letting it read as a miscount.
    """
    return sum(not row["date"] for row in read_csv(HERE / "firefox-cves.csv"))


def main_chart() -> None:
    rows = read_csv(HERE / "firefox-quarterly.csv")
    annual = read_csv(HERE / "firefox-advisories.csv")
    latest = next((row for row in annual if row["partial_year"] == "yes"), None)
    lines = []
    if latest:
        through = (f" through {latest['data_through']}"
                   if latest.get("data_through") else "")
        lines.append(
            f"{latest['unique_cves']} distinct CVEs in partial "
            f"{latest['year']}{through}\n{latest['unique_explicit_ai']} name "
            f"an AI system or method; {latest['unique_ai_affiliated']} name "
            "only an AI-security employer"
        )
    undated = undated_cves()
    if undated:
        lines.append(f"{undated} undated CVEs appear only in the annual counts")
    note = "\n".join(lines)
    last = rows[-1]
    periodic_stacked(
        HERE / "discovery-cyber-firefox.png",
        title="Firefox vulnerability disclosures",
        subtitle="Distinct CVEs per quarter, split by what the reporter "
                 "credit names",
        ylabel="Distinct CVEs that quarter",
        periods=[row["quarter"] for row in rows],
        stacks=[
            ("human or uncredited", HUMAN,
             [int(row["other"]) for row in rows]),
            ("fuzzer", FUZZ, [int(row["fuzz"]) for row in rows]),
            ("AI-affiliated; method unstated", AI_AFFILIATED,
             [int(row["ai_affiliated"]) for row in rows]),
            ("names an AI system or method", AI,
             [int(row["explicit_ai"]) for row in rows]),
        ],
        source_label="Mozilla foundation-security-advisories, counted in the "
                     "vendored CSV. Credits are textual markers, not audited "
                     "causation",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=(f"partial quarter\nthrough {last['data_through']}"
                      if last["partial_quarter"] == "yes" else ""),
        note=note,
    )


def impact_chart() -> None:
    rows = read_csv(HERE / "firefox-cves.csv")
    # Unrated is missing data, not a mild rating; its row appears only while
    # some CVE actually carries it, so an all-rated refetch drops the row
    # rather than drawing a line of zeros.
    severities = ["Unrated", "Low", "Moderate", "High", "Critical"]
    if not any(row["impact"] == "Unrated" for row in rows):
        severities.remove("Unrated")

    def tally(subset: list[dict[str, str]]) -> dict[str, dict[str, int]]:
        out: dict[str, Counter] = defaultdict(Counter)
        for row in subset:
            out[row["year"]][row["impact"]] += 1
        return out

    years = sorted({row["year"] for row in rows})
    panels = [
        ("All finders", tally(rows)),
        ("Explicit AI method", tally(
            [row for row in rows if row["band"] == "explicit_ai"])),
        ("AI-affiliated credit", tally(
            [row for row in rows if row["band"] == "ai_affiliated"])),
        ("Fuzzer credits", tally(
            [row for row in rows if row["band"] == "fuzz"])),
        ("Other credits", tally(
            [row for row in rows if row["band"] == "other"])),
    ]
    severity_heatmap(
        HERE / "impact-cyber-firefox.png",
        "Firefox CVEs by impact",
        "Distinct-CVE counts by Mozilla's advisory impact rating and "
        "reporter credit",
        years=years,
        panels=panels,
        severities=severities,
        source_label="Mozilla foundation-security-advisories, one row per "
                     "distinct CVE",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def sensitivity() -> None:
    """Draw the two counting units side by side.

    The gap between them is Mozilla's packaging, not discovery: it widens
    whenever more products ship the same fix, which is why the folder does not
    plot mentions as its headline. Kept annual: the mention columns live in
    the annual CSV, and the packaging ratio is a per-year fact.
    """
    rows = read_csv(HERE / "firefox-advisories.csv")
    years = [int(row["year"]) for row in rows]
    unique = [int(row["unique_cves"]) for row in rows]
    mentions = [int(row["total"]) for row in rows]
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
        [SOURCE_URL],
        __file__,
    )


def cumulative() -> None:
    rows = read_csv(HERE / "firefox-quarterly.csv")
    undated = undated_cves()
    counts_chart(
        HERE / "cumulative-cyber-firefox.png",
        title="Firefox vulnerabilities: cumulative distinct CVEs",
        ylabel="Distinct CVEs to date",
        period_labels=[row["quarter"] for row in rows],
        counts=[int(row["unique_cves"]) for row in rows],
        source_label="Mozilla foundation-security-advisories, "
                     "counted in the vendored CSV",
        source_url=SOURCE_URL,
        built_by=__file__,
        note=(f"{undated} undated CVEs are in the annual counts "
              "but not this line" if undated else ""),
    )


def main() -> None:
    main_chart()
    impact_chart()
    sensitivity()
    cumulative()


if __name__ == "__main__":
    main()
