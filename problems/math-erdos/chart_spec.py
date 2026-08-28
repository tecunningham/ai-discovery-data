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
    HUMAN,
    HUMAN_SOFT,
    NEUTRAL,
    base_spec,
    load,
    num,
    plain_lines,
    scatter,
)


def build_erdos(slug: str):
    rows = load(slug, "erdos-solution-years.csv")
    dated = [r for r in rows if r["solution_year"]]
    kind_labels = {"published": "published paper",
                   "preprint": "arXiv preprint only",
                   "stated": "stated on the page",
                   "ai_wiki": "AI-wiki entry only"}
    colors = {"published paper": HUMAN, "arXiv preprint only": HUMAN_SOFT,
              "stated on the page": NEUTRAL, "AI-wiki entry only": AI}
    bars_values = [{"x": r["solution_year"],
                    "series": kind_labels[r["reference_kind"]], "value": 1}
                   for r in dated]
    bars = base_spec(bars_values)
    bars.update({
        "mark": {"type": "bar"},
        "encoding": {
            "x": {"field": "x", "type": "ordinal",
                  "title": "Imputed solution year",
                  "axis": {"labelAngle": -45, "values": [
                      str(y) for y in range(1940, 2027, 10)]}},
            "y": {"aggregate": "sum", "field": "value",
                  "type": "quantitative", "title": "Problems first resolved"},
            "color": {"field": "series", "type": "nominal", "title": None,
                      "scale": {"domain": list(colors),
                                "range": list(colors.values())},
                      "legend": {"orient": "top"}},
            "tooltip": [{"field": "x", "type": "ordinal", "title": "year"},
                        {"field": "series", "type": "nominal",
                         "title": "dated by"},
                        {"aggregate": "sum", "field": "value",
                         "type": "quantitative", "title": "problems"}],
        },
    })
    points = [{"year": num(r["solution_year"]), "number": num(r["problem"]),
               "problem": f'#{r["problem"]}', "status": r["status"],
               "kind": kind_labels[r["reference_kind"]],
               "reference": r["reference"], "basis": r["basis"],
               "url": f'https://www.erdosproblems.com/{r["problem"]}'}
              for r in dated]
    detail = scatter(points, x="year", x_type="quantitative", y="number",
                     y_type="quantitative",
                     y_title="Problem number (order of cataloguing)",
                     x_title="Imputed solution year",
                     color=("kind", colors), href=True,
                     tips=[("problem", "nominal", "problem"),
                           ("status", "nominal", "status"),
                           ("year", "quantitative", "imputed year"),
                           ("kind", "nominal", "dated by"),
                           ("reference", "nominal", "reference"),
                           ("basis", "nominal", "basis")],
                     height=420)
    detail["encoding"]["x"]["scale"] = {"zero": False}
    return [("Imputed solution years", bars,
             "Bars count solved problems by the year of their resolving "
             "reference; see the folder README for the imputation rules."),
            ("Every dated solution — click through to the problem page",
             detail,
             "Each point is one solved problem; clicking opens its page on "
             "erdosproblems.com.")]


def build_erdos_history(rows: list[dict]) -> dict:
    values = []
    for row in rows:
        for column, label in (("total_problems", "catalogued"),
                              ("total_solved", "marked solved"),
                              ("lean_formalized", "Lean-formalized")):
            values.append({"x": row["date"], "series": label,
                           "value": num(row[column])})
    return plain_lines(values, x="x", x_type="temporal",
                       y_title="Problems",
                       series_colors={"catalogued": NEUTRAL,
                                      "marked solved": HUMAN,
                                      "Lean-formalized": "#8a6fb8"})


def charts(slug: str):
    charts = build_erdos(slug)
    history = build_erdos_history(load(slug, "erdos-database-history.csv"))
    charts.append(("Catalogue snapshots", history,
                   "Monthly stocks from the project's statistics history."))
    return charts
