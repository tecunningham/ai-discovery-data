#!/usr/bin/env python3
"""Draw this folder's two figures from the deduplicated annual counts.

Run: python3 problems/cyber-osv-cves/figure.py

discovery-cyber-osv-cves.png counts distinct CVEs first published per year;
cumulative-cyber-osv-cves.png redraws them as a running total for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import UNATTRIBUTED  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import cyber_simple_bars  # noqa: E402
from lib.table import read_csv  # noqa: E402


def cumulative() -> None:
    rows = read_csv(HERE / "osv-cves-by-year.csv")
    counts_chart(
        HERE / "cumulative-cyber-osv-cves.png",
        title="OSV open-source CVEs: cumulative",
        ylabel="Distinct CVEs to date",
        period_labels=[row["year"] for row in rows],
        counts=[int(row["distinct_cves"]) for row in rows],
        source_label="OSV full database export, deduplicated by CVE identifier",
        source_url="https://google.github.io/osv.dev/data/",
        built_by=__file__,
    )


def main() -> None:
    cyber_simple_bars(
        HERE / "osv-cves-by-year.csv",
        "distinct_cves",
        HERE / "discovery-cyber-osv-cves.png",
        "Open-source CVEs represented in OSV",
        "Distinct active CVEs linked to an affected package, deduplicated across advisories",
        "Distinct CVEs first published that year",
        UNATTRIBUTED,
        "OSV full database export, deduplicated by CVE identifier",
        "https://google.github.io/osv.dev/data/",
        __file__,
    )
    cumulative()


if __name__ == "__main__":
    main()
