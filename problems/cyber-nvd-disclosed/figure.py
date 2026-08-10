#!/usr/bin/env python3
"""Draw discovery-cyber-nvd-disclosed.png from this folder's annual CVE counts.

Run: python3 problems/cyber-nvd-disclosed/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import HUMAN  # noqa: E402
from lib.families import cyber_simple_bars  # noqa: E402


def main() -> None:
    cyber_simple_bars(
        HERE / "nvd-by-year.csv",
        "nvd_published",
        HERE / "discovery-cyber-nvd-disclosed.png",
        "All software: vulnerabilities disclosed",
        "Every CVE published in the US National Vulnerability Database",
        "CVEs disclosed that year",
        HUMAN,
        "NVD API, counted by publication year",
        "https://nvd.nist.gov/developers/vulnerabilities",
        __file__,
    )


if __name__ == "__main__":
    main()
