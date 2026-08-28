#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of Ben Green's 100 problems.

Run: python3 problems/math-green/figure.py

discovery-math-green.png counts dated resolutions by year;
cumulative-math-green.png is the same ledger as rows remaining, for the
collection-wide cumulative index. No row on this list has an AI-attributed
resolution, so unlike math-smale there is no ai_problem argument to pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import ledger_figures  # noqa: E402


def main() -> None:
    ledger_figures(
        "green-problems.csv",
        __file__,
    )


if __name__ == "__main__":
    main()
