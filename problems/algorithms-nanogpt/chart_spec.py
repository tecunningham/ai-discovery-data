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
    values = [{"date": r["date"], "minutes": num(r["minutes"]),
               "record": r["record"], "agent": r["agent"],
               "ai_system": r["ai_system"] or "—", "note": r["note"]}
              for r in load(slug, "nanogpt-records.csv")
              if num(r["minutes"]) is not None]
    spec = record_steps(
        values, x="date", x_type="temporal", y="minutes",
        y_title="Training minutes to target loss (log scale)", log=True,
        color=("agent", {"human": HUMAN, "ai_assisted": AI_SOFT, "ai": AI}),
        tips=[("record", "nominal", "record #"),
              ("date", "temporal", "date"),
              ("minutes", "quantitative", "minutes"),
              ("agent", "nominal", "agent"),
              ("ai_system", "nominal", "AI system"),
              ("note", "nominal", "note")])
    return [("modded-nanogpt speedrun records", spec, "")]
