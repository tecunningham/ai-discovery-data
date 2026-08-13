#!/usr/bin/env python3
"""Draw this folder's two figures from its annual CVE counts.

Run: python3 problems/cyber-nvd-disclosed/figure.py

discovery-cyber-nvd-disclosed.png counts CVEs published per year;
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
from lib.families import cyber_simple_bars  # noqa: E402
from lib.table import read_csv  # noqa: E402


def cumulative() -> None:
    rows = read_csv(HERE / "nvd-by-year.csv")
    counts_chart(
        HERE / "cumulative-cyber-nvd-disclosed.png",
        title="NVD-published CVEs: cumulative",
        ylabel="CVEs published to date",
        period_labels=[row["year"] for row in rows],
        counts=[int(row["nvd_published"]) for row in rows],
        source_label="NVD API, counted by publication year",
        source_url="https://nvd.nist.gov/developers/vulnerabilities",
        built_by=__file__,
    )


def main() -> None:
    cyber_simple_bars(
        HERE / "nvd-by-year.csv",
        "nvd_published",
        HERE / "discovery-cyber-nvd-disclosed.png",
        "All software: vulnerabilities disclosed",
        "Every CVE published in the US National Vulnerability Database",
        "CVEs disclosed that year",
        HUMAN,
        "NVD API, counted by publication year",
        "https://nvd.nist.gov/developers/vulnerabilities",
        __file__,
    )
    cumulative()


if __name__ == "__main__":
    main()
