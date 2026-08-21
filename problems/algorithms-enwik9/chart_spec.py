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
    values = [{"date": r["date"], "bytes": num(r["total_bytes"]),
               "series": r["series"], "program": r["program"],
               "author": r["author"], "note": r["note"]}
              for r in load(slug, "enwik9-records.csv")]
    series = sorted({v["series"] for v in values})
    palette = {name: colour for name, colour
               in zip(series, [HUMAN, DARKGREY, FUZZ, AI])}
    spec = record_steps(
        values, x="date", x_type="temporal", y="bytes",
        y_title="Decompressor + archive bytes",
        color=("series", palette),
        tips=[("date", "temporal", "date"),
              ("bytes", "quantitative", "bytes"),
              ("program", "nominal", "program"),
              ("author", "nominal", "author"),
              ("note", "nominal", "note")])
    return [("Hutter Prize enwik9 record", spec, "")]
