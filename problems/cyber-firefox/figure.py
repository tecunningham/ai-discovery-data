#!/usr/bin/env python3
"""Draw discovery-cyber-firefox.png from this folder's annual advisory counts.

Run: python3 problems/cyber-firefox/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import cyber_stacked  # noqa: E402


def main() -> None:
    cyber_stacked(
        HERE / "firefox-advisories.csv",
        HERE / "discovery-cyber-firefox.png",
        "Firefox vulnerability disclosures",
        "Security-advisory CVEs split by explicit AI, fuzzer, or other credit",
        "Mozilla foundation-security-advisories, counted in the vendored CSV",
        "https://github.com/mozilla/foundation-security-advisories",
        __file__,
    )


if __name__ == "__main__":
    main()
