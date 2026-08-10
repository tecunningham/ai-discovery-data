#!/usr/bin/env python3
"""Draw output-stackoverflow-questions.png from this folder's monthly counts.

Run: python3 problems/output-stackoverflow/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import year_fraction  # noqa: E402
from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The month ChatGPT was released, which is where the fall begins and the level
# the collapse is measured against. Named here rather than in the text so the
# arithmetic below cannot drift from the label it produces.
CHATGPT = "2022-11"


def main() -> None:
    rows = read_csv(HERE / "stackoverflow-questions-monthly.csv")
    counts = {row["month"]: int(row["questions"]) for row in rows}
    last = rows[-1]["month"]
    fall = 1 - counts[last] / counts[CHATGPT]

    volume_series(
        HERE / "output-stackoverflow-questions.png",
        xs=[year_fraction(row["month"]) for row in rows],
        ys=[counts[row["month"]] / 1000 for row in rows],
        title="Stack Overflow questions per month",
        subtitle="Questions asked of other people; demand for human time, not discovery",
        ylabel="Thousand questions that month",
        # Only the first line can run long: the 2020 peak reaches into the
        # block's second and third lines, so those stay short of it.
        reading=f"{counts[CHATGPT]:,} questions in {CHATGPT}, when ChatGPT was released\n"
                f"{counts[last]:,} in {last},\n"
                f"a {fall:.0%} collapse",
        source_label="Stack Exchange API, surviving questions by creation date",
        source_url="https://api.stackexchange.com/docs",
        built_by=__file__,
        rules=((2022 + 10.5 / 12, "ChatGPT released,\nNov 2022"),),
    )


if __name__ == "__main__":
    main()
