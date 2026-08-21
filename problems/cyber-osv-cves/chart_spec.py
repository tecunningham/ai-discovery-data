"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    AI,
    AI_SOFT,
    FUZZ,
    HUMAN,
    NEUTRAL,
    load,
    periodic_series,
    stacked_bars,
)


def charts(slug: str):
    charts = periodic_series(
        "osv-cves-by-quarter.csv", "quarter", "distinct_cves",
        "Distinct CVEs")(slug)
    severity = stacked_bars(
        load(slug, "osv-severity-by-year.csv"), "year",
        {"critical": "Critical", "high": "High", "moderate": "Moderate",
         "low": "Low", "unrated": "Unrated"},
        {"Critical": "#002435", "High": "#234f61", "Moderate": "#547d8f",
         "Low": "#87afc1", "Unrated": NEUTRAL},
        y_title="CVEs")
    charts.append(("Ecosystem severity labels by year", severity,
                   "Labels cover about a third of CVEs; Unrated is missing "
                   "data, not a rating."))
    credits = stacked_bars(
        load(slug, "osv-credits-by-year.csv"), "year",
        {"explicit_ai": "explicit AI", "ai_affiliated": "AI-affiliated",
         "fuzz": "fuzzer", "other_credited": "other credited"},
        {"explicit AI": AI, "AI-affiliated": AI_SOFT, "fuzzer": FUZZ,
         "other credited": HUMAN},
        y_title="Credited CVEs")
    charts.append(("Finder credits by year", credits,
                   "About 1% of CVEs carry any credit; the uncredited "
                   "majority is not drawn."))
    return charts


# Mirrors the grouping in problems/output-arxiv/figure.py; the folder check
# recomputes the prose from the same rule, so the three cannot drift apart
# without a red cell.
