#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of the prize problems.

Run: python3 problems/math-millennium/figure.py

discovery-math-millennium.png counts dated resolutions by year;
cumulative-math-millennium.png is the same ledger as rows remaining, for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.cumulative import ledger_remaining_chart  # noqa: E402
from lib.families import problem_list_chart  # noqa: E402


def main() -> None:
    problem_list_chart(
        HERE / "millennium-problems.csv",
        HERE / "discovery-math-millennium.png",
        __file__,
    )
    ledger_remaining_chart(
        HERE / "millennium-problems.csv",
        HERE / "cumulative-math-millennium.png",
        __file__,
    )


if __name__ == "__main__":
    main()
