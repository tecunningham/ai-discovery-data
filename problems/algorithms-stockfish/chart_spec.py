"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    HUMAN,
    load,
    num,
    plain_lines,
)


def charts(slug: str):
    values = [{"x": r["date"], "series": "Elo vs Stockfish 15",
               "value": num(r["elo_vs_sf15"])}
              for r in load(slug, "stockfish-ncm-elo.csv")]
    spec = plain_lines(values, x="x", x_type="temporal",
                       y_title="Elo versus Stockfish 15",
                       series_colors={"Elo vs Stockfish 15": HUMAN})
    return [("Stockfish strength by build date", spec,
             "One point per tested development build.")]
