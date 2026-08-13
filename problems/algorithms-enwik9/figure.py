#!/usr/bin/env python3
"""Draw discovery-algorithms-enwik9.png and cumulative-algorithms-enwik9.png
from this folder's record table.

Run: python3 problems/algorithms-enwik9/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import year_fraction  # noqa: E402
from lib.cumulative import staircase_chart  # noqa: E402
from lib.families import compression_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402


def cumulative() -> None:
    rows = [
        row for row in read_csv(HERE / "enwik9-records.csv")
        if row["series"] == "hutter_enwik9" and row["award"] != "pending"
    ]
    staircase_chart(
        HERE / "cumulative-algorithms-enwik9.png",
        title="Hutter Prize enwik9: standing record",
        subtitle="Standing CPU-capped records on the 1 GB corpus; "
                 "lower total size is better",
        ylabel="Total size, MB (program + archive)",
        series=[("", [year_fraction(row["date"]) for row in rows],
                 [int(row["total_bytes"]) / 1e6 for row in rows])],
        source_label="prize.hutter1.net and mattmahoney.net/dc/text.html, "
                     "vendored as enwik9-records.csv",
        source_url="https://prize.hutter1.net/",
        built_by=__file__,
        note="Lower is better; pending entries excluded.",
    )


def main() -> None:
    compression_chart(
        HERE / "enwik9-records.csv",
        "hutter_enwik9",
        HERE / "discovery-algorithms-enwik9.png",
        "Hutter Prize compression: enwik9",
        "Standing CPU-capped records on the 1 GB corpus; lower total size is better",
        __file__,
    )


if __name__ == "__main__":
    main()
    cumulative()
