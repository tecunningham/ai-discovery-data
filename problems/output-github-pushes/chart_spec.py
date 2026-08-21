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
    load,
    num,
    plain_lines,
)


def charts(slug: str):
    values = []
    for row in load(slug, "github-innovationgraph-global.csv"):
        year, quarter = row["quarter"].split("-Q")
        month = (int(quarter) - 1) * 3 + 2
        values.append({"x": f"{year}-{month:02d}-15", "series": "git pushes",
                       "value": num(row["git_pushes"]),
                       "quarter": row["quarter"]})
    spec = plain_lines(values, x="x", x_type="temporal",
                       y_title="Git pushes per quarter",
                       series_colors={"git pushes": DARKGREY})
    spec["encoding"]["tooltip"].append(
        {"field": "quarter", "type": "nominal", "title": "quarter"})
    return [("GitHub global git pushes", spec, "")]
