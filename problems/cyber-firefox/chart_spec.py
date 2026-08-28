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
    load,
    periodic_split_series,
    scatter,
)


def charts(slug: str):
    charts = periodic_split_series(
        "firefox-by-quarter.csv", "quarter",
        {"explicit_ai": "explicit AI", "ai_affiliated": "AI-affiliated",
         "fuzz": "fuzzer", "other": "other"},
        {"explicit AI": AI, "AI-affiliated": AI_SOFT, "fuzzer": FUZZ,
         "other": HUMAN}, "Distinct CVEs")(slug)
    per_cve = [{"date": r["date"], "impact": r["impact"], "cve": r["cve"],
                "band": r["band"],
                "reporters": (r["reporters"] or "—")[:160]}
               for r in load(slug, "firefox-cves.csv") if r["date"]]
    impact_order = ["Critical", "High", "Moderate", "Low", "Unrated"]
    spec = scatter(per_cve, x="date", x_type="temporal", y="impact",
                   y_type="nominal", y_title=None, y_sort=impact_order,
                   x_title="Announced",
                   tips=[("cve", "nominal", "CVE"),
                         ("date", "temporal", "announced"),
                         ("impact", "nominal", "impact"),
                         ("band", "nominal", "credit band"),
                         ("reporters", "nominal", "reporters")],
                   color=("band", {"explicit_ai": AI, "ai_affiliated": AI_SOFT,
                                   "fuzz": FUZZ, "other": HUMAN}),
                   height=260)
    charts.append(("Every distinct CVE, by impact", spec,
                   "Mozilla's advisory impact rating; colour is the credit "
                   "band. The few undated CVEs are absent."))
    return charts
