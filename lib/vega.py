"""Vega-Lite chart shapes and series families for the interactive pages.

tools/build_docs.py renders each problem folder's README into a page and
embeds the charts the folder's own chart_spec.py declares. The spec shapes
(bars, record steps, scatter, plain lines) and the families shared by several
folders live here — the exact analogue of lib/chart.py and lib/families.py
for the committed PNGs — so a folder holding a series of a known kind is a
short declaration rather than a copy of the spec. The palette is re-exported
so a chart_spec.py has one import surface.
"""

from __future__ import annotations

from pathlib import Path

from lib.palette import (  # noqa: F401
    AI,
    AI_SOFT,
    FUZZ,
    HUMAN,
    HUMAN_SOFT,
    NEUTRAL,
    UNATTRIBUTED as DARKGREY,
)
from lib.table import read_csv

ROOT = Path(__file__).resolve().parents[1]


def load(slug: str, name: str) -> list[dict[str, str]]:
    return read_csv(ROOT / "problems" / slug / name)


def num(value: str) -> float | int | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return int(parsed) if parsed.is_integer() else parsed


def base_spec(values: list[dict], height: int = 340) -> dict:
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": "container",
        "height": height,
        "data": {"values": values},
        "config": {
            "axis": {"labelFontSize": 12, "titleFontSize": 12,
                     "gridColor": "#e3e3e3"},
            "legend": {"labelFontSize": 12, "titleFontSize": 12},
            "view": {"stroke": None},
        },
    }


def tooltip(fields: list[tuple[str, str, str]]) -> list[dict]:
    """fields is a list of (field, vega type, title)."""
    return [{"field": f, "type": t, "title": name} for f, t, name in fields]


def melt(rows: list[dict], x: str, columns: dict[str, str]) -> list[dict]:
    """Wide annual columns to long form for stacked bars."""
    out = []
    for row in rows:
        for column, label in columns.items():
            value = num(row.get(column, ""))
            if value is not None:
                out.append({"x": row[x], "series": label, "value": value})
    return out


def stacked_bars(rows: list[dict], x: str, columns: dict[str, str],
                 colors: dict[str, str], *, x_title: str = "Year",
                 y_title: str, extra_tip: str = "") -> dict:
    values = melt(rows, x, columns)
    spec = base_spec(values)
    spec.update({
        "mark": {"type": "bar"},
        "encoding": {
            "x": {"field": "x", "type": "ordinal", "title": x_title,
                  "axis": {"labelAngle": -45}},
            "y": {"field": "value", "type": "quantitative",
                  "title": y_title, "stack": True},
            "color": {"field": "series", "type": "nominal", "title": None,
                      "scale": {"domain": [columns[c] for c in columns],
                                "range": [colors[columns[c]] for c in columns]},
                      "legend": {"orient": "top"}},
            "tooltip": tooltip([("x", "ordinal", x_title),
                                ("series", "nominal", "series"),
                                ("value", "quantitative", "count")]),
        },
    })
    if extra_tip:
        spec["encoding"]["tooltip"].append(
            {"field": "note", "type": "nominal", "title": extra_tip})
    return spec


def record_steps(values: list[dict], *, x: str, x_type: str, y: str,
                 y_title: str, tips: list[tuple[str, str, str]],
                 color: tuple[str, dict[str, str]] | None = None,
                 log: bool = False, href: bool = False,
                 x_title: str = "Date", height: int = 340) -> dict:
    spec = base_spec(values, height)
    x_axis = {}
    if x_type == "quantitative":
        x_axis = {"axis": {"format": "d"}}
    elif x_type == "temporal" and values:
        # d3's multi-scale ticks can label a two-year span with bare month
        # names; pick an explicit format from the span instead.
        span = sorted(row[x] for row in values)
        years = int(span[-1][:4]) - int(span[0][:4])
        x_axis = {"axis": {"format": "%b %Y" if years < 4 else "%Y",
                           "labelAngle": -40}}
    encoding = {
        "x": {"field": x, "type": x_type, "title": x_title, **x_axis},
        "y": {"field": y, "type": "quantitative", "title": y_title,
              **({"scale": {"type": "log"}} if log else {})},
        "tooltip": tooltip(tips),
    }
    if color:
        field, mapping = color
        encoding["color"] = {
            "field": field, "type": "nominal", "title": None,
            "scale": {"domain": list(mapping), "range": list(mapping.values())},
            "legend": {"orient": "top"},
        }
    if href:
        encoding["href"] = {"field": "url", "type": "nominal"}
    spec["layer"] = [
        {"mark": {"type": "line", "interpolate": "step-after",
                  "strokeWidth": 1.6}, "encoding": encoding},
        {"mark": {"type": "point", "filled": True, "size": 70,
                  "cursor": "pointer" if href else "default"},
         "encoding": encoding},
    ]
    return spec


def plain_lines(values: list[dict], *, x: str, x_type: str, y_title: str,
                series_colors: dict[str, str], x_title: str = "Date") -> dict:
    spec = base_spec(values)
    spec.update({
        "mark": {"type": "line", "strokeWidth": 1.6},
        "encoding": {
            "x": {"field": "x", "type": x_type, "title": x_title},
            "y": {"field": "value", "type": "quantitative", "title": y_title},
            "color": {"field": "series", "type": "nominal", "title": None,
                      "scale": {"domain": list(series_colors),
                                "range": list(series_colors.values())},
                      "legend": {"orient": "top"}},
            "tooltip": tooltip([("x", x_type, x_title),
                                ("series", "nominal", "series"),
                                ("value", "quantitative", y_title)]),
        },
    })
    return spec


def scatter(values: list[dict], *, x: str, x_type: str, y: str, y_type: str,
            y_title: str, tips: list[tuple[str, str, str]],
            color: tuple[str, dict[str, str]] | None = None,
            href: bool = False, x_title: str = "Year",
            height: int = 340, y_sort: list | None = None) -> dict:
    spec = base_spec(values, height)
    encoding = {
        "x": {"field": x, "type": x_type, "title": x_title,
              **({"axis": {"format": "d"}} if x_type == "quantitative"
                 else {})},
        "y": {"field": y, "type": y_type, "title": y_title,
              **({"axis": {"format": "d"}} if y_type == "quantitative"
                 else {}),
              **({"sort": y_sort} if y_sort else {})},
        "tooltip": tooltip(tips),
    }
    if color:
        field, mapping = color
        encoding["color"] = {
            "field": field, "type": "nominal", "title": None,
            "scale": {"domain": list(mapping), "range": list(mapping.values())},
            "legend": {"orient": "top"},
        }
    if href:
        encoding["href"] = {"field": "url", "type": "nominal"}
    spec.update({
        "mark": {"type": "point", "filled": True, "size": 72, "opacity": 0.85,
                 "cursor": "pointer" if href else "default"},
        "encoding": encoding,
    })
    return spec


# ------------------------------------------------------------- families ----


def _period_axis(period: str) -> dict:
    """An ordinal period axis labelled once a year.

    Forty quarters or a hundred months of tick labels are unreadable; the
    year is written on each January or Q1 bar and the tooltip carries the
    full period label.
    """
    marker = "-Q1" if period == "quarter" else "-01"
    return {"labelExpr": f"test(/{marker}$/, datum.value) ? "
                         "substring(datum.value, 0, 4) : ''",
            "labelAngle": 0}


def _fill_periods(rows: list[dict], period: str) -> list[dict]:
    """Insert zero rows for periods a sparse CSV skips.

    An ordinal axis draws only the labels it is given, so a quiet quarter
    that has no CSV row would silently compress time — 2004 sitting beside
    2009. Numeric columns of the synthesized rows are empty strings, which
    ``num`` reads as None and Vega-Lite draws as nothing.
    """
    def successor(label: str) -> str:
        year, part = label.split("-")
        if period == "quarter":
            index = int(part[1])
            return (f"{year}-Q{index + 1}" if index < 4
                    else f"{int(year) + 1}-Q1")
        index = int(part)
        return (f"{year}-{index + 1:02d}" if index < 12
                else f"{int(year) + 1}-01")

    filled = []
    expected = rows[0][period]
    for row in rows:
        while row[period] != expected:
            filled.append({key: ("0" if key != period else expected)
                           for key in row})
            expected = successor(expected)
        filled.append(row)
        expected = successor(row[period])
    return filled


def annual_series(csv: str, y_column: str, y_title: str):
    def build(slug: str):
        rows = load(slug, csv)
        values = [{"x": r["year"], "value": num(r[y_column]),
                   "note": "partial year" if r.get("partial_year") == "yes"
                           else ""}
                  for r in rows]
        spec = base_spec(values)
        spec.update({
            "mark": {"type": "bar", "color": DARKGREY},
            "encoding": {
                "x": {"field": "x", "type": "ordinal", "title": "Year",
                      "axis": {"labelAngle": -45}},
                "y": {"field": "value", "type": "quantitative",
                      "title": y_title},
                "tooltip": tooltip([("x", "ordinal", "year"),
                                    ("value", "quantitative", y_title),
                                    ("note", "nominal", "note")]),
            },
        })
        return [(y_title, spec,
                 "The final bar is a partial year; hover for the flag.")]
    return build


def split_series(csv: str, columns: dict[str, str], colors: dict[str, str],
                 y_title: str):
    def build(slug: str):
        rows = load(slug, csv)
        return [(y_title,
                 stacked_bars(rows, "year", columns, colors, y_title=y_title),
                 "The final bar is a partial year.")]
    return build


def periodic_series(csv: str, period: str, y_column: str, y_title: str,
                    drop_leading_zeros: bool = False):
    """Single-band bars at a quarterly or monthly cadence."""
    def build(slug: str):
        rows = load(slug, csv)
        if drop_leading_zeros:
            first = next(i for i, r in enumerate(rows) if num(r[y_column]))
            rows = rows[first:]
        rows = _fill_periods(rows, period)
        values = [{"x": r[period], "value": num(r[y_column]),
                   "note": ("partial " + period
                            if r.get(f"partial_{period}") == "yes" else "")}
                  for r in rows]
        spec = base_spec(values)
        spec.update({
            "mark": {"type": "bar", "color": DARKGREY},
            "encoding": {
                "x": {"field": "x", "type": "ordinal",
                      "title": period.capitalize(),
                      "axis": _period_axis(period)},
                "y": {"field": "value", "type": "quantitative",
                      "title": y_title},
                "tooltip": tooltip([("x", "ordinal", period),
                                    ("value", "quantitative", y_title),
                                    ("note", "nominal", "note")]),
            },
        })
        return [(y_title, spec,
                 f"The final bar is a partial {period}; hover for the flag.")]
    return build


def periodic_split_series(csv: str, period: str, columns: dict[str, str],
                          colors: dict[str, str], y_title: str):
    """Stacked bands at a quarterly or monthly cadence."""
    def build(slug: str):
        rows = _fill_periods(load(slug, csv), period)
        spec = stacked_bars(rows, period, columns, colors,
                            x_title=period.capitalize(), y_title=y_title)
        spec["encoding"]["x"]["axis"] = _period_axis(period)
        return [(y_title, spec,
                 f"The final bar is a partial {period}.")]
    return build


def ledger_series(csv: str):
    """The six problem-list folders share one schema and one chart."""
    def build(slug: str):
        rows = load(slug, csv)
        list_year = int(rows[0]["list_year"])
        values = []
        for row in rows:
            resolved = num(row["resolved_year"])
            values.append({
                "problem": row["short_name"],
                "year": resolved if resolved is not None else 2026,
                "status": row["status"] if resolved is not None
                          or row["status"] != "resolved"
                          else "resolved, undated",
                "resolver": row["resolver"] or "—",
                "notes": (row["notes"] or "")[:220],
            })
        order = [v["problem"] for v in values]
        colors = {"resolved": HUMAN, "open": NEUTRAL, "partial": HUMAN_SOFT,
                  "unresolvable": DARKGREY, "withdrawn": DARKGREY,
                  "resolved, undated": HUMAN_SOFT}
        present = {v["status"] for v in values}
        spec = scatter(
            values, x="year", x_type="quantitative", y="problem",
            y_type="nominal", y_title=None, y_sort=order,
            x_title=f"Resolution year (open problems drawn at 2026; "
                    f"list posed {list_year})",
            tips=[("problem", "nominal", "problem"),
                  ("status", "nominal", "status"),
                  ("year", "quantitative", "year"),
                  ("resolver", "nominal", "resolver"),
                  ("notes", "nominal", "notes")],
            color=("status", {s: colors.get(s, DARKGREY)
                              for s in sorted(present)}),
            height=max(220, 20 * len(values)),
        )
        spec["encoding"]["x"]["scale"] = {
            "domain": [min(list_year, min(v["year"] for v in values)) - 2,
                       2028]}
        return [("Per-problem resolution timeline", spec,
                 "Open problems sit on the right edge. Hover a point for "
                 "resolver and notes.")]
    return build


def build_record_ladder(csv: str, group_field: str, heading: str,
                        keep: set[str] | None = None):
    """Cumulative record steps for the AlphaEvolve-adjacent ladders.

    keep restricts to the same problem groups the folder's static figure
    plots; None keeps every group in the file.
    """
    def build(slug: str):
        rows = [r for r in load(slug, csv) if r.get("is_record") == "yes"
                and r["year"] and (keep is None or r[group_field] in keep)]
        rows.sort(key=lambda r: (r[group_field], int(r["year"]),
                                 int(r["step"] or 0)))
        counts: dict[str, int] = {}
        values = []
        for row in rows:
            counts[row[group_field]] = counts.get(row[group_field], 0) + 1
            values.append({"year": num(row["year"]),
                           "group": row[group_field],
                           "steps": counts[row[group_field]],
                           "value": row["value"],
                           "agent": row["agent"],
                           "attribution": (row["attribution"] or "")[:160]})
        groups = sorted(counts)
        cycle = [HUMAN, AI, FUZZ, DARKGREY, HUMAN_SOFT, AI_SOFT, NEUTRAL]
        palette = {name: cycle[i % len(cycle)]
                   for i, name in enumerate(groups)}
        spec = record_steps(
            values, x="year", x_type="quantitative", y="steps",
            y_title="Cumulative record steps", x_title="Year",
            color=("group", palette),
            tips=[("group", "nominal", "quantity"),
                  ("year", "quantitative", "year"),
                  ("value", "nominal", "record value"),
                  ("agent", "nominal", "agent"),
                  ("attribution", "nominal", "attribution")])
        spec["layer"][0]["encoding"]["x"]["scale"] = {"zero": False}
        return [(heading, spec, "Hover a step for its value and attribution.")]
    return build
