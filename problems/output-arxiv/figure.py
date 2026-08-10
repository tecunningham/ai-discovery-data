#!/usr/bin/env python3
"""Draw output-arxiv-submissions.png from this folder's monthly counts.

Run: python3 problems/output-arxiv/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import year_fraction  # noqa: E402
from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The month ChatGPT was released, which is the comparison the series is usually
# put to. Named here rather than in the text so the arithmetic below cannot
# drift from the label it produces.
CHATGPT = "2022-11"


def main() -> None:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The last row is the month in progress at fetch time, so every comparison
    # uses the last complete month instead.
    last = rows[-2]["month"]
    span = (year_fraction(last) - year_fraction(CHATGPT))
    growth = counts[last] / counts[CHATGPT] - 1

    volume_series(
        HERE / "output-arxiv-submissions.png",
        xs=[year_fraction(row["month"]) for row in rows],
        ys=[int(row["submissions"]) for row in rows],
        title="arXiv submissions per month",
        subtitle="Every preprint submitted since 1991; volume, not discovery",
        ylabel="New submissions that month",
        reading=f"{counts[CHATGPT]:,} in {CHATGPT}, when ChatGPT was released\n"
                f"{counts[last]:,} in {last} — up {growth:.0%} in {span:.1f} years,\n"
                f"after decades of steadier growth",
        source_label="arxiv.org/stats download, vendored as arxiv-monthly.csv",
        source_url="https://arxiv.org/stats/monthly_submissions",
        built_by=__file__,
        partial_last="part month",
    )


if __name__ == "__main__":
    main()
