#!/usr/bin/env python3
"""Draw this folder's two figures from its monthly submission counts.

Run: python3 problems/output-arxiv/figure.py

output-arxiv-submissions.png plots submissions per month;
cumulative-output-arxiv.png redraws the series as cumulative submissions to
date, for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import AS_OF_DATE, year_fraction  # noqa: E402
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The month ChatGPT was released, which is the comparison the series is usually
# put to. Named here rather than in the text so the arithmetic below cannot
# drift from the label it produces.
CHATGPT = "2022-11"


def cumulative() -> None:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts_chart(
        HERE / "cumulative-output-arxiv.png",
        title="arXiv submissions: cumulative",
        ylabel="Submissions to date, millions",
        period_labels=[row["month"] for row in rows],
        counts=[int(row["submissions"]) / 1e6 for row in rows],
        source_label="arxiv.org/stats download, vendored as arxiv-monthly.csv",
        source_url="https://arxiv.org/stats/monthly_submissions",
        built_by=__file__,
    )


def main() -> None:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The last row is the month in progress at fetch time, so every comparison
    # uses the last complete month instead. That rule silently breaks when a
    # fetch lands just after a month boundary, before arXiv opens the new
    # month's row — so assert it rather than assume it.
    if rows[-1]["month"] != f"{AS_OF_DATE.year}-{AS_OF_DATE.month:02d}":
        raise SystemExit(
            f"the last row is {rows[-1]['month']}, not the AS_OF_DATE month "
            f"{AS_OF_DATE.year}-{AS_OF_DATE.month:02d}; the last-row-is-partial "
            "rule no longer holds")
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
    cumulative()


if __name__ == "__main__":
    main()
