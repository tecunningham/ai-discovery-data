#!/usr/bin/env python3
"""Draw discovery-math-landau.png from this folder's ledger of Landau's problems.

Run: python3 problems/math-landau/figure.py

All four rows are open, so the status bar is one open block and the events panel
records that no dated resolution exists. That is the chart's content rather than
a failure to draw.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import problem_list_chart  # noqa: E402


def main() -> None:
    problem_list_chart(
        HERE / "landau-problems.csv",
        HERE / "discovery-math-landau.png",
        __file__,
    )


if __name__ == "__main__":
    main()
