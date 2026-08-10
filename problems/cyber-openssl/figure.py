#!/usr/bin/env python3
"""Draw discovery-cyber-openssl.png from this folder's annual disclosure counts.

Run: python3 problems/cyber-openssl/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import cyber_stacked  # noqa: E402


def main() -> None:
    cyber_stacked(
        HERE / "openssl-vulnerabilities.csv",
        HERE / "discovery-cyber-openssl.png",
        "OpenSSL vulnerability disclosures",
        "One critical library; annual disclosures split by explicit finder credit",
        "OpenSSL vulnerability index, counted in the vendored CSV",
        "https://openssl-library.org/news/vulnerabilities/",
        __file__,
    )


if __name__ == "__main__":
    main()
