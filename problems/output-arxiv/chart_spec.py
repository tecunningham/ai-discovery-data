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
    base_spec,
    load,
    num,
    plain_lines,
    tooltip,
)


# Mirrors the grouping in this folder's figure.py; the folder check
# recomputes the prose from the same rule, so the three cannot drift
# apart without a red cell.
ARXIV_LEGACY = {
    "alg-geom": "math.AG", "dg-ga": "math.DG", "funct-an": "math.FA",
    "q-alg": "math.QA", "cmp-lg": "cs.CL", "chao-dyn": "nlin.CD",
    "patt-sol": "nlin.PS", "adap-org": "nlin.AO", "comp-gas": "nlin.CG",
    "solv-int": "nlin.SI", "acc-phys": "physics.acc-ph",
    "ao-sci": "physics.ao-ph", "atom-ph": "physics.atom-ph",
    "bayes-an": "physics.data-an", "chem-ph": "physics.chem-ph",
    "plasm-ph": "physics.plasm-ph", "supr-con": "cond-mat.supr-con",
    "mtrl-th": "cond-mat.mtrl-sci",
}


ARXIV_PHYSICS = {
    "astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th",
    "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph",
}


ARXIV_FIELD_COLOURS = {
    "physics": "#4477aa", "mathematics": "#ee6677",
    "computer science": "#228833", "statistics": "#ccbb44",
    "elec. eng. & systems": "#66ccee", "quantitative biology": "#aa3377",
    "quantitative finance": "#ee8866", "economics": "#888888",
}


ARXIV_GROUPS = {
    "math": "mathematics", "cs": "computer science", "stat": "statistics",
    "eess": "elec. eng. & systems", "econ": "economics",
    "q-bio": "quantitative biology", "q-fin": "quantitative finance",
}


def charts(slug: str):
    from collections import defaultdict

    values = [{"x": f'{r["month"]}-01', "series": "submissions",
               "value": num(r["submissions"])}
              for r in load(slug, "arxiv-by-month.csv")]
    spec = plain_lines(values, x="x", x_type="temporal",
                       y_title="Submissions per month",
                       series_colors={"submissions": DARKGREY})
    charts = [("arXiv monthly submissions", spec, "")]

    by_group: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_subfield: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int))
    for r in load(slug, "arxiv-categories-by-month.csv"):
        if r["month"] < "1991-07":
            continue
        category = ARXIV_LEGACY.get(r["category"], r["category"])
        archive = category.split(".")[0]
        group = ("physics" if archive in ARXIV_PHYSICS
                 else ARXIV_GROUPS[archive])
        by_group[group][r["month"]] += int(r["submissions"])
        if archive == "math":
            by_subfield[category][r["month"]] += int(r["submissions"])
    # The final month is partial everywhere; end the lines at the last
    # complete one, exactly as the PNGs do.
    months = sorted({month for series in by_group.values()
                     for month in series})[:-1]

    field_values = [{"x": f"{month}-01", "series": group,
                     "value": by_group[group][month]}
                    for group in ARXIV_FIELD_COLOURS for month in months]
    charts.append((
        "Submissions per month by field",
        plain_lines(field_values, x="x", x_type="temporal",
                    y_title="Submissions per month",
                    series_colors=ARXIV_FIELD_COLOURS),
        "Primary category only, grouped to arXiv's own top level.",
    ))

    sub_values = [{"x": f"{month}-01", "series": subfield,
                   "value": by_subfield[subfield][month]}
                  for subfield in sorted(by_subfield) for month in months]
    sub_spec = base_spec(sub_values, height=420)
    sub_spec.update({
        "mark": {"type": "line", "strokeWidth": 1.3},
        "params": [{
            "name": "picked",
            "select": {"type": "point", "fields": ["series"]},
            "bind": "legend",
        }],
        "encoding": {
            "x": {"field": "x", "type": "temporal", "title": "Month"},
            "y": {"field": "value", "type": "quantitative",
                  "title": "Submissions per month"},
            "color": {"field": "series", "type": "nominal", "title": None,
                      "scale": {"scheme": "tableau20"},
                      "legend": {"orient": "right", "columns": 1,
                                 "symbolLimit": 40}},
            "opacity": {"condition": {"param": "picked", "value": 1},
                        "value": 0.15},
            "tooltip": tooltip([("x", "temporal", "month"),
                                ("series", "nominal", "subfield"),
                                ("value", "quantitative", "submissions")]),
        },
    })
    charts.append((
        "Mathematics subfields, all of them",
        sub_spec,
        "Click a legend entry to isolate a subfield; shift-click to compare "
        "several. Colours repeat across the thirty-plus series, so the "
        "legend, not the hue, identifies a line.",
    ))
    return charts
