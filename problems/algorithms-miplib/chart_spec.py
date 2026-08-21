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
    NEUTRAL,
    load,
    melt,
    stacked_bars,
)


def charts(slug: str):
    rows = load(slug, "miplib-solution-releases.csv")
    columns = {"better_incumbents": "better incumbent",
               "new_optimal_solutions": "new optimal",
               "first_known_feasible": "first feasible",
               "optimal_status_only": "status-only optimal"}
    values = melt(rows, "release_date", columns)
    spec = stacked_bars(rows, "release_date", columns,
                        {"better incumbent": HUMAN, "new optimal": DARKGREY,
                         "first feasible": FUZZ,
                         "status-only optimal": NEUTRAL},
                        x_title="Solufile release", y_title="Solutions updated")
    spec["data"]["values"] = values
    return [("MIPLIB 2017 solufile releases", spec, "")]
