#!/usr/bin/env python3
"""Draw discovery-cyber-osv-cves.png from the deduplicated annual counts.

Run: python3 problems/cyber-osv-cves/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import UNATTRIBUTED  # noqa: E402
from lib.families import cyber_simple_bars  # noqa: E402


def main() -> None:
    cyber_simple_bars(
        HERE / "osv-cves-by-year.csv",
        "distinct_cves",
        HERE / "discovery-cyber-osv-cves.png",
        "Open-source CVEs represented in OSV",
        "Distinct active CVEs linked to an affected package, deduplicated across advisories",
        "Distinct CVEs first published that year",
        UNATTRIBUTED,
        "OSV full database export, deduplicated by CVE identifier",
        "https://google.github.io/osv.dev/data/",
        __file__,
    )


if __name__ == "__main__":
    main()
