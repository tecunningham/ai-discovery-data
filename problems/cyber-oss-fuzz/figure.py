#!/usr/bin/env python3
"""Draw this folder's two figures from its annual record counts.

Run: python3 problems/cyber-oss-fuzz/figure.py

discovery-cyber-oss-fuzz.png counts records published per year;
cumulative-cyber-oss-fuzz.png redraws them as a running total for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import FUZZ  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import cyber_simple_bars  # noqa: E402
from lib.table import read_csv  # noqa: E402


def cumulative() -> None:
    rows = read_csv(HERE / "ossfuzz-discoveries.csv")
    counts_chart(
        HERE / "cumulative-cyber-oss-fuzz.png",
        title="OSS-Fuzz vulnerability records: cumulative",
        ylabel="Records published to date",
        period_labels=[row["year"] for row in rows],
        counts=[int(row["discoveries"]) for row in rows],
        source_label="OSV OSS-Fuzz archive, counted by record id",
        source_url="https://osv.dev/list?q=ecosystem%3AOSS-Fuzz",
        built_by=__file__,
    )


def main() -> None:
    cyber_simple_bars(
        HERE / "ossfuzz-discoveries.csv",
        "discoveries",
        HERE / "discovery-cyber-oss-fuzz.png",
        "OSS-Fuzz vulnerability discoveries",
        "Automated fuzzing baseline: annual records in the OSS-Fuzz archive",
        "Vulnerabilities found that year",
        FUZZ,
        "OSV OSS-Fuzz archive, counted by record id",
        "https://osv.dev/list?q=ecosystem%3AOSS-Fuzz",
        __file__,
    )
    cumulative()


if __name__ == "__main__":
    main()
