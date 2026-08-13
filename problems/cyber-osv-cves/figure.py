#!/usr/bin/env python3
"""Draw the quarterly, severity, credits and cumulative OSV CVE charts.

Run: python3 problems/cyber-osv-cves/figure.py

discovery-cyber-osv-cves.png counts distinct CVEs first published per quarter,
the grain the fetch actually produces. severity-cyber-osv-cves.png cuts the
same CVEs by the ecosystem severity label, with the Unrated majority drawn as
its own row rather than hidden; its subtitle states the coverage from the CSV.
credits-cyber-osv-cves.png draws only the credited sliver, since stacking the
uncredited majority would flatten every band to invisibility; the note, with
its share computed from the CSV, says what is not drawn. cumulative-cyber-osv-cves.png redraws the quarterly counts as a
running total for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import AI, AI_SOFT, FUZZ, HUMAN, UNATTRIBUTED  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked, severity_heatmap  # noqa: E402
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://google.github.io/osv.dev/data/"
SOURCE_LABEL = "OSV full database export, deduplicated by CVE identifier"

# Mildest first, matching fetch.py; Unrated sits below Low because it is
# missing data, not a fifth severity rung.
SEVERITIES = ["Unrated", "Low", "Moderate", "High", "Critical"]


def main_chart() -> None:
    rows = read_csv(HERE / "osv-cves-by-quarter.csv")
    latest = next(row for row in rows if row["partial_quarter"] == "yes")
    periodic_stacked(
        HERE / "discovery-cyber-osv-cves.png",
        title="Open-source CVEs represented in OSV",
        subtitle="Quarterly distinct CVEs linked to an affected package, "
                 "deduplicated across advisories",
        ylabel="Distinct CVEs first published that quarter",
        periods=[row["quarter"] for row in rows],
        stacks=[
            ("distinct CVEs", UNATTRIBUTED,
             [int(row["distinct_cves"]) for row in rows]),
        ],
        source_label=SOURCE_LABEL,
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=f"partial quarter\nthrough {latest['data_through']}",
    )


def severity_chart() -> None:
    rows = read_csv(HERE / "osv-severity-by-year.csv")
    by_year = {
        row["year"]: {
            "Unrated": int(row["unrated"]),
            **{label: int(row[label.lower()]) for label in SEVERITIES[1:]},
        }
        for row in rows
    }
    rated = sum(count for counts in by_year.values()
                for label, count in counts.items() if label != "Unrated")
    total = sum(sum(counts.values()) for counts in by_year.values())
    severity_heatmap(
        HERE / "severity-cyber-osv-cves.png",
        "OSV CVEs by ecosystem severity label",
        f"Ecosystem severity labels cover {100 * rated / total:.0f}% of CVEs; "
        "the rest are Unrated",
        years=[row["year"] for row in rows],
        panels=[("All OSV-linked CVEs", by_year)],
        severities=SEVERITIES,
        source_label=SOURCE_LABEL,
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def credits_chart() -> None:
    rows = read_csv(HERE / "osv-credits-by-year.csv")
    uncredited = sum(int(row["uncredited"]) for row in rows)
    total = sum(int(row["distinct_cves"]) for row in rows)
    annual = read_csv(HERE / "osv-cves-by-year.csv")
    latest = next(row for row in annual if row["partial_year"] == "yes")
    periodic_stacked(
        HERE / "credits-cyber-osv-cves.png",
        title="OSV CVEs with finder credits",
        subtitle="Only the credited sliver is drawn; credits are an "
                 "ecosystem-dependent field most OSV sources never fill",
        ylabel="Credited CVEs that year",
        periods=[row["year"] for row in rows],
        stacks=[
            ("credited, conventional", HUMAN,
             [int(row["other_credited"]) for row in rows]),
            ("fuzzer", FUZZ, [int(row["fuzz"]) for row in rows]),
            ("AI-affiliated credit", AI_SOFT,
             [int(row["ai_affiliated"]) for row in rows]),
            ("explicit AI method", AI,
             [int(row["explicit_ai"]) for row in rows]),
        ],
        source_label="OSV full database export, credits unioned across "
                     "each CVE's records",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=f"partial year\nthrough {latest['data_through']}",
        note=f"{100 * uncredited / total:.0f}% of OSV-linked CVEs carry no "
             "credit at all and are not drawn",
    )


def cumulative() -> None:
    rows = read_csv(HERE / "osv-cves-by-quarter.csv")
    counts_chart(
        HERE / "cumulative-cyber-osv-cves.png",
        title="OSV open-source CVEs: cumulative",
        ylabel="Distinct CVEs to date",
        period_labels=[row["quarter"] for row in rows],
        counts=[int(row["distinct_cves"]) for row in rows],
        source_label=SOURCE_LABEL,
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    main_chart()
    severity_chart()
    credits_chart()
    cumulative()


if __name__ == "__main__":
    main()
