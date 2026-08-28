"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import build_record_ladder  # noqa: E402


charts = build_record_ladder(
    "alphaevolve-records.csv", "problem",
    "Record steps across the five groups",
    keep={"6.5", "6.7", "6.48", "6.49", "6.50"})
