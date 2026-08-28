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
    DARKGREY,
    FUZZ,
    HUMAN,
    load,
    num,
    record_steps,
)


def charts(slug: str):
    values = [{"date": r["date"], "digits": num(r["digits"]),
               "record": r["record"], "who": r["who"], "method": r["method"],
               "domain": r["domain"], "ai": r["ai_involved"],
               "url": r["source_url"]}
              for r in load(slug, "factoring-records.csv")]
    domains = sorted({v["domain"] for v in values})
    palette = {name: colour for name, colour
               in zip(domains, [HUMAN, DARKGREY, FUZZ, AI])}
    spec = record_steps(
        values, x="date", x_type="temporal", y="digits",
        y_title="Record size (decimal digits)", href=True,
        color=("domain", palette),
        tips=[("record", "nominal", "record"),
              ("date", "temporal", "date"),
              ("digits", "quantitative", "digits"),
              ("who", "nominal", "who"),
              ("method", "nominal", "method"),
              ("ai", "nominal", "AI involved")])
    return [("Factoring and discrete-log records", spec,
             "Click a point for its source.")]
