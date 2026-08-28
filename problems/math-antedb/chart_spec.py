"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    DARKGREY,
    FUZZ,
    HUMAN,
    load,
    num,
    record_steps,
)


def charts(slug: str):
    rows = load(slug, "antedb-sweep.csv")
    rows.sort(key=lambda r: (r["quantity"], int(r["year"])))
    counts: dict[str, int] = {}
    values = []
    for row in rows:
        counts[row["quantity"]] = counts.get(row["quantity"], 0) + 1
        values.append({"year": num(row["year"]), "family": row["quantity"],
                       "changes": counts[row["quantity"]],
                       "slice": f'{row["parameter"]}={row["point"]}',
                       "value": row["value"]})
    spec = record_steps(
        values, x="year", x_type="quantitative", y="changes",
        y_title="Cumulative slice-level record changes", x_title="Year",
        color=("family", {"mu": HUMAN, "A": FUZZ, "beta": DARKGREY}),
        tips=[("family", "nominal", "family"),
              ("year", "quantitative", "year"),
              ("slice", "nominal", "slice"),
              ("value", "nominal", "new value")])
    spec["layer"][0]["encoding"]["x"]["scale"] = {"zero": False}
    return [("ANTEDB exponent-record changes", spec, "")]
