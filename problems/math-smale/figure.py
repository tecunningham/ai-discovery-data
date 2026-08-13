#!/usr/bin/env python3
"""Draw this folder's two figures from its ledger of Smale's problems.

Run: python3 problems/math-smale/figure.py

discovery-math-smale.png counts dated resolutions by year;
cumulative-math-smale.png is the same ledger as rows remaining, for the
collection-wide cumulative index. ai_problem names the one row on any prestige
list with an AI-attributed fall, so the attribution is a hand-set argument here
rather than a column in the CSV.
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
        HERE / "smale-problems.csv",
        HERE / "discovery-math-smale.png",
        __file__,
        ai_problem="16",
    )
    ledger_remaining_chart(
        HERE / "smale-problems.csv",
        HERE / "cumulative-math-smale.png",
        __file__,
    )


if __name__ == "__main__":
    main()
