#!/usr/bin/env python3
"""Draw discovery-math-sums-autoconvolution.png from this folder's two ladders.

Run: python3 problems/math-sums-autoconvolution/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import alphaevolve_value_chart  # noqa: E402


def main() -> None:
    alphaevolve_value_chart(
        HERE / "sums-autoconvolution-records.csv",
        ["6.44", "6.3"],
        HERE / "discovery-math-sums-autoconvolution.png",
        "Sums-and-differences and autoconvolution",
        "Two related standing lower-bound ladders; colour marks who set each step",
        "Best known lower bound",
        {("6.44", "4"): "AlphaEvolve", ("6.44", "6"): "human retakes record", ("6.3", "3"): "AlphaEvolve"},
        __file__,
    )


if __name__ == "__main__":
    main()
