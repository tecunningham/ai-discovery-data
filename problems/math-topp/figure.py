#!/usr/bin/env python3
"""Draw discovery-math-topp.png from this folder's ledger of TOPP entries.

Run: python3 problems/math-topp/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import problem_list_chart  # noqa: E402


def main() -> None:
    problem_list_chart(
        HERE / "topp-problems.csv",
        HERE / "discovery-math-topp.png",
        __file__,
    )


if __name__ == "__main__":
    main()
