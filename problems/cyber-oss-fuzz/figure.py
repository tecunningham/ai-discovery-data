#!/usr/bin/env python3
"""Draw discovery-cyber-oss-fuzz.png from this folder's annual record counts.

Run: python3 problems/cyber-oss-fuzz/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import FUZZ  # noqa: E402
from lib.families import cyber_simple_bars  # noqa: E402


def main() -> None:
    cyber_simple_bars(
        HERE / "ossfuzz-discoveries.csv",
        "discoveries",
        HERE / "discovery-cyber-oss-fuzz.png",
        "OSS-Fuzz vulnerability discoveries",
        "Automated fuzzing baseline: annual records in the OSS-Fuzz archive",
        "Vulnerabilities found that year",
        FUZZ,
        "OSV OSS-Fuzz archive, counted by record id",
        "https://osv.dev/list?q=ecosystem%3AOSS-Fuzz",
        __file__,
    )


if __name__ == "__main__":
    main()
