#!/usr/bin/env python3
"""Draw discovery-cyber-microsoft.png from this folder's monthly CVE counts.

Run: python3 problems/cyber-microsoft/figure.py

Stacked monthly bars of Microsoft-issued CVEs split by what the acknowledgment
credit names, in the same bands and colours as the Firefox series so the two
vendors can be read side by side. A month is this series' native grain —
Microsoft ships one coordinated release per Patch Tuesday — so the record June
and July 2026 releases stand as their own bars instead of dissolving into an
annual one. The 2026 part year ends on a complete month, so no bar is drawn
partial; the on-chart note states where the data stops.
cumulative-cyber-microsoft.png redraws the same counts as a running total for
the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import AI, AI_SOFT, FUZZ, HUMAN  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked  # noqa: E402
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://api.msrc.microsoft.com/cvrf/v3.0/updates"

# Affiliation-only credits are drawn in a lighter red than corroborated method
# credits: same family, visibly weaker evidence. Matches cyber-firefox.
AI_AFFILIATED = AI_SOFT


def cumulative() -> None:
    rows = read_csv(HERE / "msrc-monthly.csv")
    counts_chart(
        HERE / "cumulative-cyber-microsoft.png",
        title="Microsoft security-update CVEs: cumulative",
        ylabel="CVEs to date",
        period_labels=[row["month"] for row in rows],
        counts=[int(row["cves"]) for row in rows],
        source_label="MSRC Security Update Guide, counted in the vendored CSV",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    monthly = read_csv(HERE / "msrc-monthly.csv")
    annual = read_csv(HERE / "msrc-cves.csv")
    latest = next(row for row in annual if row["partial_year"] == "yes")
    ai_marked = int(latest["explicit_ai"]) + int(latest["ai_affiliated"])
    periodic_stacked(
        HERE / "discovery-cyber-microsoft.png",
        title="Microsoft security-update CVEs",
        subtitle="CVEs issued by Microsoft's own CNA per month, split by what "
                 "the acknowledgment credit names",
        ylabel="CVEs that month",
        periods=[row["month"] for row in monthly],
        stacks=[
            ("human or uncredited", HUMAN,
             [int(row["other"]) for row in monthly]),
            ("fuzzer", FUZZ,
             [int(row["fuzz"]) for row in monthly]),
            ("AI-affiliated; method unstated", AI_AFFILIATED,
             [int(row["ai_affiliated"]) for row in monthly]),
            ("names an AI system or method", AI,
             [int(row["explicit_ai"]) for row in monthly]),
        ],
        source_label="MSRC Security Update Guide, counted in the vendored CSV. "
                     "Credits are textual markers, not audited causation",
        source_url=SOURCE_URL,
        built_by=__file__,
        note=f"{latest['cves']} CVEs in partial {latest['year']} "
             f"through {latest['data_through']}, a complete final month;\n"
             f"{ai_marked} carry any AI marker — "
             f"{100 * ai_marked / int(latest['cves']):.1f}% of the part year",
    )
    cumulative()


if __name__ == "__main__":
    main()
