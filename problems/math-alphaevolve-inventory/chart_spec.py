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
    DARKGREY,
    FUZZ,
    HUMAN,
    HUMAN_SOFT,
    NEUTRAL,
    load,
    num,
    scatter,
)


def charts(slug: str):
    values = [{"problem": r["problem"], "title": r["title"],
               "group": r["topic_group"], "status": r["status"],
               "citations": num(r["n_citations"]),
               "latest": num(r["latest_cited_year"]) or None,
               "earliest": num(r["earliest_cited_year"]) or None}
              for r in load(slug, "alphaevolve-inventory.csv")]
    values = [v for v in values if v["latest"] is not None]
    statuses = sorted({v["status"] for v in values})
    palette = {name: colour for name, colour
               in zip(statuses, [HUMAN, AI, FUZZ, NEUTRAL, DARKGREY,
                                 HUMAN_SOFT, AI_SOFT])}
    spec = scatter(values, x="latest", x_type="quantitative", y="citations",
                   y_type="quantitative",
                   y_title="Dated prior works cited",
                   x_title="Latest cited year",
                   color=("status", palette),
                   tips=[("problem", "nominal", "problem"),
                         ("title", "nominal", "title"),
                         ("group", "nominal", "group"),
                         ("status", "nominal", "status"),
                         ("citations", "quantitative", "cited works"),
                         ("earliest", "quantitative", "earliest cited")])
    return [("The 65 problems, by literature depth and recency", spec,
             "Each point is one problem from the AlphaEvolve paper's "
             "section 6.")]
