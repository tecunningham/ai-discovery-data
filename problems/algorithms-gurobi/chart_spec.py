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
    rows = load(slug, "gurobi-milp-speedups.csv")
    cumulative, values = 1.0, []
    for row in rows:
        cumulative *= float(row["release_speedup"])
        values.append({"date": row["date"], "release": row["release"],
                       "cumulative": round(cumulative, 4),
                       "step": num(row["release_speedup"]),
                       "note": row["note"], "url": row["source_url"]})
    spec = record_steps(
        values, x="date", x_type="temporal", y="cumulative",
        y_title="Cumulative MILP speedup vs v9.5", href=True,
        tips=[("release", "nominal", "release"),
              ("date", "temporal", "announced"),
              ("step", "quantitative", "release speedup"),
              ("cumulative", "quantitative", "cumulative"),
              ("note", "nominal", "note")])
    return [("Gurobi vendor-reported MILP speedup", spec,
             "Click a point to open the vendor announcement.")]
