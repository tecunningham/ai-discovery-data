"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    load,
    num,
    record_steps,
)


def charts(slug: str):
    values = [{"year": num(r["year"]), "omega": num(r["omega"]),
               "discoverer": r["discoverer"], "credit": r["credit"],
               "note": (r["note"] or "")[:200], "url": r["source_url"]}
              for r in load(slug, "matrix-multiplication-omega.csv")]
    spec = record_steps(
        values, x="year", x_type="quantitative", y="omega",
        y_title="Best proved upper bound on ω", x_title="Year", href=True,
        tips=[("year", "quantitative", "year"),
              ("omega", "quantitative", "ω"),
              ("discoverer", "nominal", "discoverer"),
              ("credit", "nominal", "credit"),
              ("note", "nominal", "note")])
    spec["layer"][0]["encoding"]["x"]["scale"] = {"zero": False}
    spec["layer"][0]["encoding"]["y"]["scale"] = {"zero": False}
    return [("Matrix-multiplication exponent ω", spec, "")]
