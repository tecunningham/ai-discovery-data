#!/usr/bin/env python3
"""Draw this folder's two figures from its quarterly record counts.

Run: python3 problems/cyber-oss-fuzz/figure.py

discovery-cyber-oss-fuzz.png counts records by publication quarter, the grain
the archive carries reliably from 2020 onward; cumulative-cyber-oss-fuzz.png
redraws the same quarters as a running total for the collection-wide cumulative
index. The annual ossfuzz-by-year.csv keeps the id-year counts the prose
quotes; fetch.py explains why the two groupings differ slightly.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import FUZZ  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import periodic_stacked  # noqa: E402
from lib.table import read_csv  # noqa: E402

SOURCE_URL = "https://osv.dev/list?q=ecosystem%3AOSS-Fuzz"


def cumulative() -> None:
    rows = read_csv(HERE / "ossfuzz-by-quarter.csv")
    counts_chart(
        HERE / "cumulative-cyber-oss-fuzz.png",
        title="OSS-Fuzz vulnerability records: cumulative",
        ylabel="Records published to date",
        period_labels=[row["quarter"] for row in rows],
        counts=[int(row["discoveries"]) for row in rows],
        source_label="OSV OSS-Fuzz archive, bucketed by publication quarter",
        source_url=SOURCE_URL,
        built_by=__file__,
    )


def main() -> None:
    rows = read_csv(HERE / "ossfuzz-by-quarter.csv")
    latest = rows[-1]
    partial = latest["partial_quarter"] == "yes"
    # The note counts what the bars show — this year's published records — not
    # the id-year figure the prose quotes; fetch.py explains the two clocks.
    year = latest["quarter"][:4]
    published = sum(int(row["discoveries"]) for row in rows
                    if row["quarter"].startswith(year))
    periodic_stacked(
        HERE / "discovery-cyber-oss-fuzz.png",
        title="OSS-Fuzz vulnerability discoveries",
        subtitle="Automated fuzzing baseline: quarterly records in the "
                 "OSS-Fuzz archive",
        ylabel="Vulnerabilities found that quarter",
        periods=[row["quarter"] for row in rows],
        stacks=[("fuzzer", FUZZ,
                 [int(row["discoveries"]) for row in rows])],
        source_label="OSV OSS-Fuzz archive, bucketed by publication quarter",
        source_url=SOURCE_URL,
        built_by=__file__,
        partial_last=(f"partial quarter\nthrough {latest['data_through']}"
                      if partial else ""),
        note=(f"{published} records published in {year} through "
              f"{latest['data_through']}" if partial else ""),
    )
    cumulative()


if __name__ == "__main__":
    main()
