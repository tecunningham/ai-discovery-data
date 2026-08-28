#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of Landau's problems.

Run: python3 problems/math-landau/figure.py

discovery-math-landau.png counts dated resolutions by year — all four rows are
open, so it records that no dated resolution exists, which is the chart's
content rather than a failure to draw; cumulative-math-landau.png is the same
ledger as rows remaining, for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import ledger_figures  # noqa: E402


def main() -> None:
    ledger_figures(
        "landau-problems.csv",
        __file__,
    )


if __name__ == "__main__":
    main()
