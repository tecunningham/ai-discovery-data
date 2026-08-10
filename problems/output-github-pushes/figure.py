#!/usr/bin/env python3
"""Draw output-github-pushes.png from this folder's quarterly totals.

Run: python3 problems/output-github-pushes/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The quarter ChatGPT was released, which is the comparison the series is
# usually put to. Named here rather than in the text so the arithmetic below
# cannot drift from the label it produces.
CHATGPT = "2022-Q4"
# The bend is recent enough that a start-to-end ratio understates it, so the
# annotation also reports the run over the last few quarters on their own.
WINDOW = 5


def quarter_fraction(quarter: str) -> float:
    # lib.chart.year_fraction parses hyphenated dates; this series is labelled
    # by quarter, which it does not accept.
    year, index = quarter.split("-Q")
    return int(year) + (int(index) - 0.5) / 4


def main() -> None:
    rows = read_csv(HERE / "github-innovationgraph-global.csv")
    pushes = {row["quarter"]: int(row["git_pushes"]) / 1e6 for row in rows}
    last = rows[-1]["quarter"]
    earlier = rows[-1 - WINDOW]["quarter"]
    growth = pushes[last] / pushes[CHATGPT] - 1
    ratio = pushes[last] / pushes[earlier]

    volume_series(
        HERE / "output-github-pushes.png",
        xs=[quarter_fraction(row["quarter"]) for row in rows],
        ys=[pushes[row["quarter"]] for row in rows],
        title="Git pushes to GitHub per quarter",
        subtitle="Uploads of commits counted by the platform; volume, not discovery",
        ylabel="Million pushes that quarter",
        reading=f"{pushes[CHATGPT]:.0f}M pushes in {CHATGPT}, when ChatGPT was released\n"
                f"{pushes[last]:.0f}M in {last} — up {growth:.0%}\n"
                f"{ratio:.1f}x in the {WINDOW} quarters from {earlier} alone",
        source_label="github/innovationgraph, summed over economies here",
        source_url="https://github.com/github/innovationgraph",
        built_by=__file__,
        markers=True,
    )


if __name__ == "__main__":
    main()
