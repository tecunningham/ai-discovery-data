#!/usr/bin/env python3
"""Draw the quarterly, severity and cumulative curl disclosure charts.

Run: python3 problems/cyber-curl/figure.py

The main chart counts disclosures by publication quarter, the finest grain the
vendored tables carry; its corner note and part-quarter marker come from the
annual table, which knows the snapshot date. The severity chart cuts the same
rows by curl's own severity rating, as counts a reader can take numbers from —
the folder's check on whether a rising count is a rising amount of harm.
cumulative-cyber-curl.png redraws the quarterly totals as a running total for
the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import AI, HUMAN  # noqa: E402
from lib.credits import SEVERITIES  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked, severity_heatmap  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The severity story is a long-run one, but curl disclosed one or two issues in
# some early years, and a decade of near-empty columns would squeeze the years
# where the drift actually happens.
FROM_YEAR = 2010

SOURCE_LABEL = "curl vulnerability JSON, counted in the vendored CSV"
SOURCE_URL = "https://curl.se/docs/vuln.json"


def counts(row: dict[str, str], prefix: str = "") -> dict[str, int]:
    return {severity: int(row[f"{prefix}sev_{severity.lower()}"])
            for severity in SEVERITIES}


def cumulative() -> None:
    rows = read_csv(HERE / "curl-by-quarter.csv")
    counts_chart(
        HERE / "cumulative-cyber-curl.png",
        title="curl vulnerabilities: cumulative disclosures",
        ylabel="Disclosures to date",
        period_labels=[row["quarter"] for row in rows],
        counts=[int(row["total"]) for row in rows],
        source_label=SOURCE_LABEL,
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    quarterly = read_csv(HERE / "curl-by-quarter.csv")
    annual = read_csv(HERE / "curl-by-year.csv")
    latest = annual[-1]
    periodic_stacked(
        HERE / "discovery-cyber-curl.png",
        title="curl vulnerability disclosures",
        subtitle="One fixed codebase; quarterly disclosures split by explicit "
                 "finder credit",
        ylabel="Vulnerabilities disclosed that quarter",
        periods=[row["quarter"] for row in quarterly],
        stacks=[
            ("human or uncredited", HUMAN,
             [int(row["other_attributed"]) for row in quarterly]),
            ("AI-credited", AI,
             [int(row["ai_attributed"]) for row in quarterly]),
        ],
        source_label=f"{SOURCE_LABEL}. Finder credits are textual markers, "
                     "not audited causation",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=f"partial quarter\nthrough {latest['data_through']}",
        note=f"{latest['total']} disclosures in partial {latest['year']} "
             f"through {latest['data_through']}\n"
             f"{latest['ai_attributed']} explicitly AI-credited",
    )
    cumulative()

    rows = [row for row in annual if int(row["year"]) >= FROM_YEAR]
    severity_heatmap(
        HERE / "severity-cyber-curl.png",
        "curl disclosures by severity",
        "Disclosure counts by curl's own rating and finder credit, "
        f"from {FROM_YEAR}",
        years=[row["year"] for row in rows],
        panels=[
            ("All finders",
             {row["year"]: counts(row) for row in rows}),
            ("AI-marked credits",
             {row["year"]: counts(row, "ai_") for row in rows}),
            ("Other credits",
             {row["year"]: counts(row, "other_") for row in rows}),
        ],
        severities=SEVERITIES,
        source_label=SOURCE_LABEL,
        source_url=SOURCE_URL,
        built_by=__file__,
    )


if __name__ == "__main__":
    main()
