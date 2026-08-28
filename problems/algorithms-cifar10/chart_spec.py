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
    HUMAN,
    load,
    num,
    record_steps,
)


def charts(slug: str):
    values = [{"date": r["date"], "seconds": num(r["seconds"]),
               "holder": r["holder"], "agent": r["agent"], "note": r["note"]}
              for r in load(slug, "cifar-speedrun-records.csv")]
    spec = record_steps(
        values, x="date", x_type="temporal", y="seconds",
        y_title="Seconds to 94% (log scale)", log=True,
        color=("agent", {"human": HUMAN, "ai_assisted": AI_SOFT, "ai": AI}),
        tips=[("date", "temporal", "date"),
              ("seconds", "quantitative", "seconds"),
              ("holder", "nominal", "holder"),
              ("agent", "nominal", "agent"),
              ("note", "nominal", "note")])
    return [("CIFAR-10 speedrun record", spec, "")]
