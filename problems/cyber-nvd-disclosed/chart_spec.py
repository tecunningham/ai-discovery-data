"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import periodic_series  # noqa: E402


charts = periodic_series(
    "nvd-by-quarter.csv", "quarter", "nvd_published", "CVEs published")
