#!/usr/bin/env python3
"""Draw discovery-algorithms-enwik9.png from this folder's record table.

Run: python3 problems/algorithms-enwik9/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import compression_chart  # noqa: E402


def main() -> None:
    compression_chart(
        HERE / "enwik9-records.csv",
        "hutter_enwik9",
        HERE / "discovery-algorithms-enwik9.png",
        "Hutter Prize compression: enwik9",
        "Standing CPU-capped records on the 1 GB corpus; lower total size is better",
        __file__,
    )


if __name__ == "__main__":
    main()
