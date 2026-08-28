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
    FUZZ,
    HUMAN,
    NEUTRAL,
    _fill_periods,
    _period_axis,
    load,
    scatter,
    stacked_bars,
)


def charts(slug: str):
    from collections import Counter, defaultdict

    columns = {"corroborated_ai": "corroborated AI",
               "ai_affiliated_unverified": "AI-affiliated, unverified",
               "conventional_or_fuzz": "conventional or fuzzing",
               "unknown": "unknown"}
    # The folder's PNG draws the affiliated band in the fuzzer amber (its chart
    # has no separate fuzz band), so the interactive page matches that choice.
    colors = {"corroborated AI": AI, "AI-affiliated, unverified": FUZZ,
              "conventional or fuzzing": HUMAN, "unknown": NEUTRAL}
    # The same quarter × provenance aggregation the folder's figure.py draws,
    # from the same per-CVE ledger, so the two views cannot disagree.
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for r in load(slug, "openssl-cves.csv"):
        quarter = f'{r["published"][:4]}-Q{(int(r["published"][5:7]) + 2) // 3}'
        if r["explicit_ai"] == "yes":
            per_quarter[quarter]["corroborated_ai"] += 1
        elif r["ai_affiliated"] == "yes":
            per_quarter[quarter]["ai_affiliated_unverified"] += 1
        elif r["reporter"]:
            per_quarter[quarter]["conventional_or_fuzz"] += 1
        else:
            per_quarter[quarter]["unknown"] += 1
    rows = _fill_periods(
        [{"quarter": quarter, **{key: str(per_quarter[quarter][key])
                                 for key in columns}}
         for quarter in sorted(per_quarter)], "quarter")
    spec = stacked_bars(rows, "quarter", columns, colors,
                        x_title="Quarter", y_title="CVEs disclosed")
    spec["encoding"]["x"]["axis"] = _period_axis("quarter")
    charts = [("Disclosures per quarter by finder provenance", spec,
               "The final bar is a partial quarter.")]
    per_cve = [{"date": r["published"], "severity": r["severity"],
                "cve": r["cve"], "reporter": (r["reporter"] or "—")[:160],
                "url": r["source_url"]}
               for r in load(slug, "openssl-cves.csv")]
    severity_order = ["Critical", "High", "Moderate", "Low", "Unknown"]
    spec = scatter(per_cve, x="date", x_type="temporal", y="severity",
                   y_type="nominal", y_title=None, y_sort=severity_order,
                   x_title="Published", href=True,
                   tips=[("cve", "nominal", "CVE"),
                         ("date", "temporal", "published"),
                         ("severity", "nominal", "severity"),
                         ("reporter", "nominal", "reporter")],
                   height=240)
    charts.append(("Every disclosure, by severity", spec,
                   "Click a point to open the OpenSSL metadata record."))
    return charts
