#!/usr/bin/env python3
"""Draw this folder's two figures from its quarterly CVE counts.

Run: python3 problems/cyber-nvd-disclosed/figure.py

discovery-cyber-nvd-disclosed.png counts CVEs published per quarter;
cumulative-cyber-nvd-disclosed.png redraws them as a running total for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import HUMAN  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked  # noqa: E402
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://nvd.nist.gov/developers/vulnerabilities"


def main_chart() -> None:
    rows = read_csv(HERE / "nvd-by-quarter.csv")
    last = rows[-1]
    periodic_stacked(
        HERE / "discovery-cyber-nvd-disclosed.png",
        title="All software: vulnerabilities disclosed",
        subtitle="Quarterly CVEs published in the US National Vulnerability "
                 "Database",
        ylabel="CVEs published that quarter",
        periods=[row["quarter"] for row in rows],
        # One unlabelled band: nothing in this series is attributed to anyone,
        # so there is no split for a legend to name.
        stacks=[("", HUMAN, [int(row["nvd_published"]) for row in rows])],
        source_label="NVD API, counted by publication quarter",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=(
            f"partial quarter\nthrough {last['data_through']}"
            if last["partial_quarter"] == "yes" else ""
        ),
    )


def cumulative() -> None:
    rows = read_csv(HERE / "nvd-by-quarter.csv")
    counts_chart(
        HERE / "cumulative-cyber-nvd-disclosed.png",
        title="NVD-published CVEs: cumulative",
        ylabel="CVEs published to date",
        period_labels=[row["quarter"] for row in rows],
        counts=[int(row["nvd_published"]) for row in rows],
        source_label="NVD API, counted by publication quarter",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    main_chart()
    cumulative()


if __name__ == "__main__":
    main()
