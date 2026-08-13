#!/usr/bin/env python3
"""Draw discovery-math-sums-autoconvolution.png and
cumulative-math-sums-autoconvolution.png from this folder's two ladders.

Run: python3 problems/math-sums-autoconvolution/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.cumulative import staircase_chart  # noqa: E402
from lib.families import alphaevolve_value_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402


def cumulative() -> None:
    rows = [
        row for row in read_csv(HERE / "sums-autoconvolution-records.csv")
        if row["problem"] in ("6.44", "6.3") and row["value"]
        and row["is_record"] == "yes"
    ]
    series = []
    for problem in ("6.44", "6.3"):
        local = sorted((row for row in rows if row["problem"] == problem),
                       key=lambda row: (int(row["year"]), int(row["step"])))
        series.append((local[0]["quantity"],
                       [float(row["year"]) for row in local],
                       [float(row["value"]) for row in local]))
    staircase_chart(
        HERE / "cumulative-math-sums-autoconvolution.png",
        title="Sums-and-differences and autoconvolution constants: "
              "standing records",
        subtitle="Two related standing lower-bound ladders; higher is better",
        ylabel="Best known lower bound",
        series=series,
        source_label="sums-autoconvolution-records.csv, transcribed from the "
                     "paper and cited follow-ons",
        source_url=sorted({row["ref"] for row in rows if row["ref"]})[0],
        built_by=__file__,
        note="Higher is better for both ladders.",
    )


def main() -> None:
    alphaevolve_value_chart(
        HERE / "sums-autoconvolution-records.csv",
        ["6.44", "6.3"],
        HERE / "discovery-math-sums-autoconvolution.png",
        "Sums-and-differences and autoconvolution",
        "Two related standing lower-bound ladders; colour marks who set each step",
        "Best known lower bound",
        {("6.44", "4"): "AlphaEvolve", ("6.44", "6"): "human retakes record", ("6.3", "3"): "AlphaEvolve"},
        __file__,
    )


if __name__ == "__main__":
    main()
    cumulative()
