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
    HUMAN,
    load,
    num,
    record_steps,
)


def charts(slug: str):
    rows = sorted(load(slug, "cvrplib-x-frontier.csv"),
                  key=lambda r: r["recorded_date"])
    values = []
    for i, row in enumerate(rows, 1):
        values.append({"date": row["recorded_date"], "events": i,
                       "instance": row["instance"],
                       "objective": num(row["objective"]),
                       "kind": row["event_type"].replace("_", " "),
                       "url": row["source_url"]})
    spec = record_steps(
        values, x="date", x_type="temporal", y="events",
        y_title="Cumulative record events", href=True,
        color=("kind", {"objective improvement": HUMAN,
                        "optimality proof": DARKGREY}),
        tips=[("date", "temporal", "posted"),
              ("instance", "nominal", "instance"),
              ("kind", "nominal", "event"),
              ("objective", "quantitative", "objective")])
    # The counter is global across both event kinds, so a per-kind colored
    # line would misread as two separate counts; keep colour on points only.
    del spec["layer"][0]["encoding"]["color"]
    return [("CVRPLIB X-instance record events", spec,
             "Click a point to open the update page it was posted on.")]
