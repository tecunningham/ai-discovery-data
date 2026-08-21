#!/usr/bin/env python3
"""Draw the quarterly, batch, severity and cumulative OpenSSL disclosure charts.

Run: python3 problems/cyber-openssl/figure.py

The main chart counts CVEs by publication quarter, the ledger's native grain;
the batch chart shows the coordinated 2026 publication dates inside it. The
severity chart cuts the same CVE ledger by OpenSSL's own rating, as counts a
reader can take numbers from. It starts in 2015: the project's structured
metadata carries no severity before 2014, and an unrated record is missing data
rather than a low one. cumulative-cyber-openssl.png redraws the ledger as a
running total for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    FUZZ,
    HUMAN,
    NEUTRAL,
    new_chart,
    save,
    source_note,
    style,
)
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked, severity_heatmap  # noqa: E402
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://github.com/openssl/release-metadata/tree/main/secjson"
# OpenSSL scores Moderate where curl scores Medium, so the ladder is named here
# rather than taken from lib.credits.
OPENSSL_SEVERITIES = ["Low", "Moderate", "High", "Critical"]
RATED_FROM = 2015
AFFILIATED = FUZZ
UNKNOWN = NEUTRAL
SERIES = (
    ("conventional_or_fuzz", "conventional / fuzzing", HUMAN),
    ("unknown", "no reporter credit", UNKNOWN),
    ("ai_affiliated_unverified", "AI-affiliated; method unverified", AFFILIATED),
    ("corroborated_ai", "corroborated AI", AI),
)


def category(row: dict[str, str]) -> str:
    """The provenance class one CVE row is drawn in, batch and main alike."""
    if row["explicit_ai"] == "yes":
        return "corroborated_ai"
    if row["ai_affiliated"] == "yes":
        return "ai_affiliated_unverified"
    if row["reporter"]:
        return "conventional_or_fuzz"
    return "unknown"


def quarter_of(published: str) -> str:
    return f"{published[:4]}-Q{(int(published[5:7]) + 2) // 3}"


def main_chart() -> None:
    rows = read_csv(HERE / "openssl-cves.csv")
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        per_quarter[quarter_of(row["published"])][category(row)] += 1
    quarters = sorted(per_quarter)
    annual = read_csv(HERE / "openssl-by-year.csv")
    latest = annual[-1]
    current = [row for row in rows
               if row["published"][:4] == latest["year"]]
    periodic_stacked(
        HERE / "discovery-cyber-openssl.png",
        title="OpenSSL vulnerability disclosures",
        subtitle="Quarterly CVEs; corroborated AI method is separate from "
                 "affiliation-only credit",
        ylabel="Vulnerabilities disclosed that quarter",
        periods=quarters,
        stacks=[
            (label, colour,
             [per_quarter[quarter][key] for quarter in quarters])
            for key, label, colour in SERIES
        ],
        source_label="OpenSSL release-metadata. AI method requires CVE-level "
                     "evidence; affiliation alone is not method",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=f"partial quarter\nthrough {latest['data_through']}",
        note=f"{len(current)} disclosures in {latest['year']} through "
             f"{latest['data_through']};\n"
             f"{latest['corroborated_ai']} corroborated AI, "
             f"{latest['ai_affiliated_unverified']} affiliation only",
    )


def batch_chart() -> None:
    rows = [
        row
        for row in read_csv(HERE / "openssl-cves.csv")
        if row["published"].startswith("2026-")
    ]
    per_date: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        per_date[row["published"]][category(row)] += 1
    dates = sorted(per_date)
    x = list(range(len(dates)))
    totals = [sum(per_date[published].values()) for published in dates]
    fig, ax = new_chart(
        "OpenSSL's 2026 disclosures arrived in batches",
        "CVEs by coordinated publication date and finder provenance",
    )
    from matplotlib.patches import Patch

    bottoms = [0] * len(x)
    for key, _, colour in SERIES:
        heights = [per_date[published][key] for published in dates]
        ax.bar(x, heights, bottom=bottoms, width=0.66, color=colour, zorder=3)
        bottoms = [bottom + height for bottom, height in zip(bottoms, heights)]
    for position, total in zip(x, totals):
        ax.text(position, total + 0.35, str(total), ha="center", fontsize=8.5)
    ax.set_xticks(
        x,
        [
            date.fromisoformat(published).strftime("%b %-d")
            for published in dates
        ],
    )
    ax.set_xlim(-0.7, len(x) - 0.3)
    ax.set_ylim(0, max(totals) * 1.2)
    style(ax, "Vulnerabilities disclosed in batch", "2026 publication date")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(
        handles=[Patch(facecolor=colour, label=label)
                 for _, label, colour in SERIES],
        frameon=False,
        fontsize=7.8,
        ncol=2,
        loc="upper left",
    )
    source_note(
        fig,
        "Source: OpenSSL release-metadata. Dates are datePublic, not discovery dates.",
    )
    save(
        fig,
        HERE / "batches-cyber-openssl.png",
        "OpenSSL vulnerabilities published in each coordinated 2026 disclosure batch.",
        [SOURCE_URL],
        __file__,
    )


def severity_chart() -> None:
    rows = [row for row in read_csv(HERE / "openssl-cves.csv")
            if int(row["published"][:4]) >= RATED_FROM]
    unrated = [row for row in rows if row["severity"] not in OPENSSL_SEVERITIES]
    if unrated:
        raise SystemExit(
            f"{len(unrated)} CVEs from {RATED_FROM} on carry no severity rating "
            f"(first: {unrated[0]['cve']}); the chart's premise no longer holds"
        )

    def tally(subset) -> dict[str, dict[str, int]]:
        out: dict[str, Counter] = defaultdict(Counter)
        for row in subset:
            out[row["published"][:4]][row["severity"]] += 1
        return out

    years = sorted({row["published"][:4] for row in rows})
    panels = [
        ("All finders", tally(rows)),
        ("Conventional or fuzzing credits", tally(
            [r for r in rows
             if r["explicit_ai"] == "no" and r["ai_affiliated"] == "no"
             and r["reporter"]])),
        ("No reporter credit", tally(
            [r for r in rows
             if r["explicit_ai"] == "no" and r["ai_affiliated"] == "no"
             and not r["reporter"]])),
        ("AI-affiliated, method unverified", tally(
            [r for r in rows
             if r["explicit_ai"] == "no" and r["ai_affiliated"] == "yes"])),
        ("Corroborated AI method", tally(
            [r for r in rows if r["explicit_ai"] == "yes"])),
    ]

    severity_heatmap(
        HERE / "severity-cyber-openssl.png",
        "OpenSSL disclosures by severity",
        "CVE counts by OpenSSL's own rating and finder provenance, "
        f"from the first rated year ({RATED_FROM})",
        years=years,
        panels=panels,
        severities=OPENSSL_SEVERITIES,
        source_label="OpenSSL release-metadata, one row per CVE",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def cumulative() -> None:
    rows = read_csv(HERE / "openssl-cves.csv")
    per_quarter = Counter(quarter_of(row["published"]) for row in rows)
    quarters = sorted(per_quarter)
    counts_chart(
        HERE / "cumulative-cyber-openssl.png",
        title="OpenSSL vulnerabilities: cumulative disclosures",
        ylabel="Disclosures to date",
        period_labels=quarters,
        counts=[per_quarter[quarter] for quarter in quarters],
        source_label="OpenSSL release-metadata",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    main_chart()
    batch_chart()
    severity_chart()
    cumulative()


if __name__ == "__main__":
    main()
