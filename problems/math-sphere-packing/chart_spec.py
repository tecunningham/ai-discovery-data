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
    rows = load(slug, "sphere-packing-lower-bound-records.csv")
    values = [{"year": num(r["year"]), "step": i, "finder": r["finder"],
               "bound": r["bound_asymptotic"], "note": (r["note"] or "")[:200],
               "url": r["source_url"]}
              for i, r in enumerate(rows, 1)]
    spec = record_steps(
        values, x="year", x_type="quantitative", y="step",
        y_title="Cumulative improvements", x_title="Year", href=True,
        tips=[("year", "quantitative", "year"),
              ("finder", "nominal", "finder"),
              ("bound", "nominal", "bound"),
              ("note", "nominal", "note")])
    spec["layer"][0]["encoding"]["x"]["scale"] = {"zero": False}
    return [("Sphere-packing lower-bound ladder", spec,
             "Click a point for the survey it is documented in.")]
