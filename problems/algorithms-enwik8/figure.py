#!/usr/bin/env python3
"""Draw discovery-algorithms-enwik8.png from this folder's record table.

Run: python3 problems/algorithms-enwik8/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import compression_chart  # noqa: E402


def main() -> None:
    compression_chart(
        HERE / "enwik8-records.csv",
        "hutter_enwik8",
        HERE / "discovery-algorithms-enwik8.png",
        "Hutter Prize compression: enwik8",
        "The retired 100 MB series provides a pre-agent record-cadence baseline",
        __file__,
    )


if __name__ == "__main__":
    main()
