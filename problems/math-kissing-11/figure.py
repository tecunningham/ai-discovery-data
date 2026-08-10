#!/usr/bin/env python3
"""Draw discovery-math-kissing-11.png from this folder's record ladder.

Run: python3 problems/math-kissing-11/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import alphaevolve_value_chart  # noqa: E402


def main() -> None:
    alphaevolve_value_chart(
        HERE / "kissing-11-records.csv",
        ["6.8"],
        HERE / "discovery-math-kissing-11.png",
        "Kissing number in dimension 11",
        "Standing lower bound: human records, AlphaEvolve, then collective AI agents",
        "Best known lower bound K(11)",
        {("6.8", "3"): "AlphaEvolve", ("6.8", "4"): "collective agents"},
        __file__,
    )


if __name__ == "__main__":
    main()
