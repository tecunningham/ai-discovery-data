#!/usr/bin/env python3
"""Draw discovery-cyber-curl.png from this folder's annual disclosure counts.

Run: python3 problems/cyber-curl/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import cyber_stacked  # noqa: E402


def main() -> None:
    cyber_stacked(
        HERE / "curl-vulnerabilities.csv",
        HERE / "discovery-cyber-curl.png",
        "curl vulnerability disclosures",
        "One fixed codebase; annual disclosures split by explicit finder credit",
        "curl vulnerability JSON, counted in the vendored CSV",
        "https://curl.se/docs/vuln.json",
        __file__,
    )


if __name__ == "__main__":
    main()
