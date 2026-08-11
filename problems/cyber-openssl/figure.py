#!/usr/bin/env python3
"""Draw annual and publication-batch OpenSSL disclosure charts.

Run: python3 problems/cyber-openssl/figure.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from matplotlib.patches import Patch
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
    shade_era,
    source_note,
    style,
)
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://github.com/openssl/release-metadata/tree/main/secjson"
AFFILIATED = FUZZ
UNKNOWN = NEUTRAL
SERIES = (
    ("conventional_or_fuzz", "conventional / fuzzing", HUMAN),
    ("unknown", "no reporter credit", UNKNOWN),
    ("ai_affiliated_unverified", "AI-affiliated; method unverified", AFFILIATED),
    ("corroborated_ai", "corroborated AI", AI),
)


def _stacked(ax, x, values, width: float) -> None:
    bottoms = [0] * len(x)
    for key, _, colour in SERIES:
        heights = values[key]
        ax.bar(x, heights, bottom=bottoms, width=width, color=colour, zorder=3)
        bottoms = [bottom + height for bottom, height in zip(bottoms, heights)]


def _legend(ax) -> None:
    ax.legend(
        handles=[Patch(facecolor=colour, label=label) for _, label, colour in SERIES],
        frameon=False,
        fontsize=7.8,
        ncol=2,
        loc="upper left",
    )


def annual_chart() -> None:
    rows = read_csv(HERE / "openssl-vulnerabilities.csv")
    years = [int(row["year"]) for row in rows]
    totals = [int(row["total"]) for row in rows]
    values = {
        key: [int(row[key]) for row in rows]
        for key, _, _ in SERIES
    }
    fig, ax = new_chart(
        "OpenSSL vulnerability disclosures",
        "Annual CVEs; corroborated AI method is separate from affiliation-only credit",
    )
    _stacked(ax, years, values, 0.76)
    partial = [index for index, row in enumerate(rows) if row["partial_year"] == "yes"]
    for index in partial:
        ax.bar(
            years[index],
            totals[index],
            width=0.76,
            facecolor="none",
            edgecolor="#444444",
            linewidth=1.3,
            zorder=4,
        )
        ax.annotate(
            "partial year",
            (years[index], totals[index]),
            xytext=(-4, 7),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color="#555555",
        )
    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(totals) * 1.24)
    shade_era(ax, right, annual=True)
    style(ax, "Vulnerabilities disclosed that year")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    _legend(ax)
    if partial:
        latest = rows[partial[-1]]
        ax.text(
            0.02,
            0.76,
            f"{latest['total']} disclosures through {latest['data_through']}\n"
            f"{latest['corroborated_ai']} corroborated AI; "
            f"{latest['ai_affiliated_unverified']} affiliation only",
            transform=ax.transAxes,
            fontsize=8.8,
            color="#333333",
            va="top",
        )
    source_note(
        fig,
        "Source: OpenSSL release-metadata. AI method requires CVE-level evidence; "
        "affiliation alone is not method.",
    )
    save(
        fig,
        HERE / "discovery-cyber-openssl.png",
        "OpenSSL vulnerability disclosures by year and provenance class. "
        "The latest year is partial.",
        [SOURCE_URL],
        __file__,
    )


def batch_chart() -> None:
    rows = [
        row
        for row in read_csv(HERE / "openssl-cves.csv")
        if row["published"].startswith("2026-")
    ]
    per_date: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        if row["explicit_ai"] == "yes":
            category = "corroborated_ai"
        elif row["ai_affiliated"] == "yes":
            category = "ai_affiliated_unverified"
        elif row["reporter"]:
            category = "conventional_or_fuzz"
        else:
            category = "unknown"
        per_date[row["published"]][category] += 1
    dates = sorted(per_date)
    x = list(range(len(dates)))
    values = {
        key: [per_date[published][key] for published in dates]
        for key, _, _ in SERIES
    }
    totals = [sum(per_date[published].values()) for published in dates]
    fig, ax = new_chart(
        "OpenSSL's 2026 disclosures arrived in batches",
        "CVEs by coordinated publication date and finder provenance",
    )
    _stacked(ax, x, values, 0.66)
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
    _legend(ax)
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


def main() -> None:
    annual_chart()
    batch_chart()


if __name__ == "__main__":
    main()
