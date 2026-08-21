#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of the top-10 Erdős problems.

Run: python3 problems/math-erdos-top10/figure.py

discovery-math-erdos-top10.png counts dated resolutions by year;
cumulative-math-erdos-top10.png is the same ledger as rows remaining, for the
collection-wide cumulative index. ai_problem marks the unit-distance row, the
one resolution on this list attributed to an AI system, and ai_caption states
its verification standing — a human-verified account rather than the formal
kernel checks the default caption describes.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import ledger_figures  # noqa: E402


def main() -> None:
    ledger_figures(
        "erdos-top10-problems.csv",
        __file__,
        ai_problem="90",
        ai_caption="AI disproof; human-verified account",
    )


if __name__ == "__main__":
    main()
