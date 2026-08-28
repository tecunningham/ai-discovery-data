#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of Thurston's questions.

Run: python3 problems/math-thurston/figure.py

discovery-math-thurston.png counts dated resolutions by year;
cumulative-math-thurston.png is the same ledger as rows remaining, for the
collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import ledger_figures  # noqa: E402


def main() -> None:
    ledger_figures(
        "thurston-questions.csv",
        __file__,
    )


if __name__ == "__main__":
    main()
