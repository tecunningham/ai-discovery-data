#!/usr/bin/env python3
"""Generate docs/ — the browsable, canonical rendering of the collection.

    python3 tools/build_docs.py

Each problem page renders its folder's README in full — the discussion is the
document, not a caption — with the interactive chart embedded where the README
embeds its primary PNG. Supplementary PNGs are shown from the repository's own
raw URLs, so the pages hold no image copies; every chart is a Vega-Lite spec
with the folder's CSV rows inlined, so a page is a self-contained artifact
rebuilt whenever the data or the document changes — the same model as the
PNGs, with `make docs` beside `make figures`. The site index is the root
README, rendered the same way, and CUMULATIVE.md and ADDITIONAL-CANDIDATES.md
get pages of their own, which is what makes GitHub Pages the one canonical
place to browse the data.

The registry at the bottom maps every series to one of a handful of chart
shapes (periodic bars, record steps, a problem ledger, plain lines, a labelled
scatter). A folder missing from the registry fails the build loudly rather
than silently shipping an index without it.

Markdown is rendered with the `markdown` package (pinned in requirements.txt
for the container; `pip install markdown` on a host that lacks it).
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.table import read_csv  # noqa: E402

DOCS = ROOT / "docs"
PAGES_BASE = "https://tecunningham.github.io/ai-discovery-data"
REPO_BASE = "https://github.com/tecunningham/ai-discovery-data"
RAW_BASE = ("https://raw.githubusercontent.com/tecunningham/"
            "ai-discovery-data/main")
BLOB_BASE = f"{REPO_BASE}/blob/main"

# The one place the pages' math is rendered; a couple of documents carry
# $…$ TeX. Inline math spans are shielded from the markdown pass below.
MATHJAX_CDN = (
    "<script>window.MathJax = {tex: {inlineMath: [['$', '$']]}};</script>\n"
    '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">'
    "</script>"
)
CHARTS_PLACEHOLDER = "\x00CHARTS\x00"

# lib/chart.py's palette, restated for the web pages so the interactive and
# static versions of a series read as the same chart.
AI = "#c1442f"
AI_SOFT = "#e09a8c"
HUMAN = "#2f6cc1"
HUMAN_SOFT = "#8fb3d9"
FUZZ = "#c98a00"
NEUTRAL = "#aaaaaa"
DARKGREY = "#37474f"

VEGA_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>'
)


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


def readme_fields(slug: str) -> dict[str, str]:
    text = (ROOT / "problems" / slug / "README.md").read_text(encoding="utf-8")
    fields = {"title": re.search(r"^#\s+(.+)$", text, re.M).group(1).strip()}
    for field in ("Metric", "Upstream", "Data"):
        match = re.search(rf"^- \*\*{field}:\*\*\s*(.+)$", text, re.M)
        fields[field.lower()] = match.group(1).strip() if match else ""
    return fields


def _protect_math(text: str) -> tuple[str, list[str]]:
    """Shield $…$ spans from the markdown pass; MathJax renders them later.

    Without this, underscores inside TeX become emphasis and the math never
    reaches the browser intact. Only single-line spans are shielded, which is
    all the documents use.
    """
    stash: list[str] = []

    def keep(match: re.Match) -> str:
        stash.append(match.group(0))
        return f"\x00MATH{len(stash) - 1}\x00"

    return re.sub(r"\$[^$\n]+\$", keep, text), stash


def _restore_math(rendered: str, stash: list[str]) -> str:
    for index, span in enumerate(stash):
        rendered = rendered.replace(f"\x00MATH{index}\x00", html.escape(span))
    return rendered


def render_markdown(text: str) -> str:
    shielded, stash = _protect_math(text)
    rendered = markdown.markdown(
        shielded, extensions=["tables", "fenced_code", "toc"])
    return _restore_math(rendered, stash)


def _rewrite_folder_markdown(text: str, slug: str) -> str:
    """Point a folder README's relative links at their browsable homes.

    Sibling documents become sibling pages, the cumulative index becomes its
    page, repository files go to the GitHub blob view, and supplementary PNGs
    are served from the repository's raw URLs — the pages keep no copies. The
    primary figure embed (the first image) becomes the placeholder the
    interactive charts are inserted at.
    """
    text = re.sub(r"!\[([^\]]*)\]\(([^)/]+\.png)\)", CHARTS_PLACEHOLDER, text,
                  count=1)
    text = re.sub(r"(?<=\])\(([^)/]+\.png)\)",
                  rf"({RAW_BASE}/problems/{slug}/\1)", text)
    text = re.sub(r"(?<=\])\(\.\./([a-z0-9-]+)/README\.md\)", r"(\1.html)",
                  text)
    text = re.sub(r"(?<=\])\(\.\./\.\./CUMULATIVE\.md\)", "(cumulative.html)",
                  text)
    text = re.sub(r"(?<=\])\(\.\./\.\./([^)#\s]+)\)",
                  rf"({BLOB_BASE}/\1)", text)
    text = re.sub(r"(?<=\])\(([^)/:#\s]+\.(?:csv|py|bib|json|yml|txt))\)",
                  rf"({BLOB_BASE}/problems/{slug}/\1)", text)
    return text


def readme_body(slug: str) -> str:
    """The folder README as page HTML, title line dropped, links rewritten.

    The H1 is dropped because the page template renders the title itself; the
    placeholder left by the first image embed is where render_page inserts
    the interactive charts.
    """
    text = (ROOT / "problems" / slug / "README.md").read_text(encoding="utf-8")
    text = re.sub(r"^#\s+.+\n", "", text, count=1)
    return render_markdown(_rewrite_folder_markdown(text, slug))


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


# ---------------------------------------------------------------- series ----

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


def build_cifar(slug: str):
    values = [{"date": r["date"], "seconds": num(r["seconds"]),
               "holder": r["holder"], "agent": r["agent"], "note": r["note"]}
              for r in load(slug, "cifar-speedrun-records.csv")]
    spec = record_steps(
        values, x="date", x_type="temporal", y="seconds",
        y_title="Seconds to 94% (log scale)", log=True,
        color=("agent", {"human": HUMAN, "ai_assisted": AI_SOFT, "ai": AI}),
        tips=[("date", "temporal", "date"),
              ("seconds", "quantitative", "seconds"),
              ("holder", "nominal", "holder"),
              ("agent", "nominal", "agent"),
              ("note", "nominal", "note")])
    return [("CIFAR-10 speedrun record", spec, "")]


def build_cvrplib(slug: str):
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


def build_ecdsa_circuit(slug: str):
    rows = load(slug, "ecdsa-circuit-records.csv")
    kind = {"yes": "note names an AI tool", "no": "no such tool named",
            "": "no note left"}
    values = [{"date": r["date"], "score": num(r["score"]),
               "toffoli": num(r["toffoli"]), "qubits": num(r["qubits"]),
               "solver": r["solver"],
               "tool": kind[r["ai_tool_in_note"]],
               "url": f'https://github.com/{r["solver"]}'}
              for r in rows]
    spec = record_steps(
        values, x="date", x_type="temporal", y="score",
        y_title="Score: Toffoli × qubits (log scale)", log=True, href=True,
        color=("tool", {"note names an AI tool": AI,
                        "no such tool named": NEUTRAL,
                        "no note left": HUMAN_SOFT}),
        tips=[("date", "temporal", "accepted"),
              ("score", "quantitative", "score"),
              ("toffoli", "quantitative", "avg Toffoli"),
              ("qubits", "quantitative", "peak qubits"),
              ("solver", "nominal", "solver"),
              ("tool", "nominal", "note")])
    # Colour marks the tool disclosure; the ladder itself is one frontier.
    del spec["layer"][0]["encoding"]["color"]
    return [("secp256k1 point-addition record ladder", spec,
             "Each point is an accepted record; click to open the solver's "
             "GitHub profile.")]


def build_enwik9(slug: str):
    values = [{"date": r["date"], "bytes": num(r["total_bytes"]),
               "series": r["series"], "program": r["program"],
               "author": r["author"], "note": r["note"]}
              for r in load(slug, "enwik9-records.csv")]
    series = sorted({v["series"] for v in values})
    palette = {name: colour for name, colour
               in zip(series, [HUMAN, DARKGREY, FUZZ, AI])}
    spec = record_steps(
        values, x="date", x_type="temporal", y="bytes",
        y_title="Decompressor + archive bytes",
        color=("series", palette),
        tips=[("date", "temporal", "date"),
              ("bytes", "quantitative", "bytes"),
              ("program", "nominal", "program"),
              ("author", "nominal", "author"),
              ("note", "nominal", "note")])
    return [("Hutter Prize enwik9 record", spec, "")]


def build_gurobi(slug: str):
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


def build_miplib(slug: str):
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


def build_nanogpt(slug: str):
    values = [{"date": r["date"], "minutes": num(r["minutes"]),
               "record": r["record"], "agent": r["agent"],
               "ai_system": r["ai_system"] or "—", "note": r["note"]}
              for r in load(slug, "nanogpt-records.csv")
              if num(r["minutes"]) is not None]
    spec = record_steps(
        values, x="date", x_type="temporal", y="minutes",
        y_title="Training minutes to target loss (log scale)", log=True,
        color=("agent", {"human": HUMAN, "ai_assisted": AI_SOFT, "ai": AI}),
        tips=[("record", "nominal", "record #"),
              ("date", "temporal", "date"),
              ("minutes", "quantitative", "minutes"),
              ("agent", "nominal", "agent"),
              ("ai_system", "nominal", "AI system"),
              ("note", "nominal", "note")])
    return [("modded-nanogpt speedrun records", spec, "")]


def build_stockfish(slug: str):
    values = [{"x": r["date"], "series": "Elo vs Stockfish 15",
               "value": num(r["elo_vs_sf15"])}
              for r in load(slug, "stockfish-ncm-elo.csv")]
    spec = plain_lines(values, x="x", x_type="temporal",
                       y_title="Elo versus Stockfish 15",
                       series_colors={"Elo vs Stockfish 15": HUMAN})
    return [("Stockfish strength by build date", spec,
             "One point per tested development build.")]


def build_openssl(slug: str):
    from collections import Counter, defaultdict

    columns = {"corroborated_ai": "corroborated AI",
               "ai_affiliated_unverified": "AI-affiliated, unverified",
               "conventional_or_fuzz": "conventional or fuzzing",
               "unknown": "unknown"}
    # The folder's PNG draws the affiliated band in the fuzzer amber (its chart
    # has no separate fuzz band), so the interactive page matches that choice.
    colors = {"corroborated AI": AI, "AI-affiliated, unverified": FUZZ,
              "conventional or fuzzing": HUMAN, "unknown": NEUTRAL}
    # The same quarter × provenance aggregation the folder's figure.py draws,
    # from the same per-CVE ledger, so the two views cannot disagree.
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for r in load(slug, "openssl-cves.csv"):
        quarter = f'{r["published"][:4]}-Q{(int(r["published"][5:7]) + 2) // 3}'
        if r["explicit_ai"] == "yes":
            per_quarter[quarter]["corroborated_ai"] += 1
        elif r["ai_affiliated"] == "yes":
            per_quarter[quarter]["ai_affiliated_unverified"] += 1
        elif r["reporter"]:
            per_quarter[quarter]["conventional_or_fuzz"] += 1
        else:
            per_quarter[quarter]["unknown"] += 1
    rows = _fill_periods(
        [{"quarter": quarter, **{key: str(per_quarter[quarter][key])
                                 for key in columns}}
         for quarter in sorted(per_quarter)], "quarter")
    spec = stacked_bars(rows, "quarter", columns, colors,
                        x_title="Quarter", y_title="CVEs disclosed")
    spec["encoding"]["x"]["axis"] = _period_axis("quarter")
    charts = [("Disclosures per quarter by finder provenance", spec,
               "The final bar is a partial quarter.")]
    per_cve = [{"date": r["published"], "severity": r["severity"],
                "cve": r["cve"], "reporter": (r["reporter"] or "—")[:160],
                "url": r["source_url"]}
               for r in load(slug, "openssl-cves.csv")]
    severity_order = ["Critical", "High", "Moderate", "Low", "Unknown"]
    spec = scatter(per_cve, x="date", x_type="temporal", y="severity",
                   y_type="nominal", y_title=None, y_sort=severity_order,
                   x_title="Published", href=True,
                   tips=[("cve", "nominal", "CVE"),
                         ("date", "temporal", "published"),
                         ("severity", "nominal", "severity"),
                         ("reporter", "nominal", "reporter")],
                   height=240)
    charts.append(("Every disclosure, by severity", spec,
                   "Click a point to open the OpenSSL metadata record."))
    return charts


def build_factoring(slug: str):
    values = [{"date": r["date"], "digits": num(r["digits"]),
               "record": r["record"], "who": r["who"], "method": r["method"],
               "domain": r["domain"], "ai": r["ai_involved"],
               "url": r["source_url"]}
              for r in load(slug, "factoring-records.csv")]
    domains = sorted({v["domain"] for v in values})
    palette = {name: colour for name, colour
               in zip(domains, [HUMAN, DARKGREY, FUZZ, AI])}
    spec = record_steps(
        values, x="date", x_type="temporal", y="digits",
        y_title="Record size (decimal digits)", href=True,
        color=("domain", palette),
        tips=[("record", "nominal", "record"),
              ("date", "temporal", "date"),
              ("digits", "quantitative", "digits"),
              ("who", "nominal", "who"),
              ("method", "nominal", "method"),
              ("ai", "nominal", "AI involved")])
    return [("Factoring and discrete-log records", spec,
             "Click a point for its source.")]


def build_alphaevolve_inventory(slug: str):
    values = [{"problem": r["problem"], "title": r["title"],
               "group": r["topic_group"], "status": r["status"],
               "citations": num(r["n_citations"]),
               "latest": num(r["latest_cited_year"]) or None,
               "earliest": num(r["earliest_cited_year"]) or None}
              for r in load(slug, "alphaevolve-inventory.csv")]
    values = [v for v in values if v["latest"] is not None]
    statuses = sorted({v["status"] for v in values})
    palette = {name: colour for name, colour
               in zip(statuses, [HUMAN, AI, FUZZ, NEUTRAL, DARKGREY,
                                 HUMAN_SOFT, AI_SOFT])}
    spec = scatter(values, x="latest", x_type="quantitative", y="citations",
                   y_type="quantitative",
                   y_title="Dated prior works cited",
                   x_title="Latest cited year",
                   color=("status", palette),
                   tips=[("problem", "nominal", "problem"),
                         ("title", "nominal", "title"),
                         ("group", "nominal", "group"),
                         ("status", "nominal", "status"),
                         ("citations", "quantitative", "cited works"),
                         ("earliest", "quantitative", "earliest cited")])
    return [("The 65 problems, by literature depth and recency", spec,
             "Each point is one problem from the AlphaEvolve paper's "
             "section 6.")]


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


def build_antedb(slug: str):
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


def build_erdos_with_history(slug: str):
    charts = build_erdos(slug)
    history = build_erdos_history(load(slug, "erdos-database-history.csv"))
    charts.append(("Catalogue snapshots", history,
                   "Monthly stocks from the project's statistics history."))
    return charts


def build_sphere_packing(slug: str):
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


def build_omega(slug: str):
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


def build_firefox(slug: str):
    charts = periodic_split_series(
        "firefox-quarterly.csv", "quarter",
        {"explicit_ai": "explicit AI", "ai_affiliated": "AI-affiliated",
         "fuzz": "fuzzer", "other": "other"},
        {"explicit AI": AI, "AI-affiliated": AI_SOFT, "fuzzer": FUZZ,
         "other": HUMAN}, "Distinct CVEs")(slug)
    per_cve = [{"date": r["date"], "impact": r["impact"], "cve": r["cve"],
                "band": r["band"],
                "reporters": (r["reporters"] or "—")[:160]}
               for r in load(slug, "firefox-cves.csv") if r["date"]]
    impact_order = ["Critical", "High", "Moderate", "Low", "Unrated"]
    spec = scatter(per_cve, x="date", x_type="temporal", y="impact",
                   y_type="nominal", y_title=None, y_sort=impact_order,
                   x_title="Announced",
                   tips=[("cve", "nominal", "CVE"),
                         ("date", "temporal", "announced"),
                         ("impact", "nominal", "impact"),
                         ("band", "nominal", "credit band"),
                         ("reporters", "nominal", "reporters")],
                   color=("band", {"explicit_ai": AI, "ai_affiliated": AI_SOFT,
                                   "fuzz": FUZZ, "other": HUMAN}),
                   height=260)
    charts.append(("Every distinct CVE, by impact", spec,
                   "Mozilla's advisory impact rating; colour is the credit "
                   "band. The few undated CVEs are absent."))
    return charts


def build_osv(slug: str):
    charts = periodic_series(
        "osv-cves-by-quarter.csv", "quarter", "distinct_cves",
        "Distinct CVEs")(slug)
    severity = stacked_bars(
        load(slug, "osv-severity-by-year.csv"), "year",
        {"critical": "Critical", "high": "High", "moderate": "Moderate",
         "low": "Low", "unrated": "Unrated"},
        {"Critical": "#002435", "High": "#234f61", "Moderate": "#547d8f",
         "Low": "#87afc1", "Unrated": NEUTRAL},
        y_title="CVEs")
    charts.append(("Ecosystem severity labels by year", severity,
                   "Labels cover about a third of CVEs; Unrated is missing "
                   "data, not a rating."))
    credits = stacked_bars(
        load(slug, "osv-credits-by-year.csv"), "year",
        {"explicit_ai": "explicit AI", "ai_affiliated": "AI-affiliated",
         "fuzz": "fuzzer", "other_credited": "other credited"},
        {"explicit AI": AI, "AI-affiliated": AI_SOFT, "fuzzer": FUZZ,
         "other credited": HUMAN},
        y_title="Credited CVEs")
    charts.append(("Finder credits by year", credits,
                   "About 1% of CVEs carry any credit; the uncredited "
                   "majority is not drawn."))
    return charts


# Mirrors the grouping in problems/output-arxiv/figure.py; the folder check
# recomputes the prose from the same rule, so the three cannot drift apart
# without a red cell.
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


def build_arxiv(slug: str):
    from collections import defaultdict

    values = [{"x": f'{r["month"]}-01', "series": "submissions",
               "value": num(r["submissions"])}
              for r in load(slug, "arxiv-monthly.csv")]
    spec = plain_lines(values, x="x", x_type="temporal",
                       y_title="Submissions per month",
                       series_colors={"submissions": DARKGREY})
    charts = [("arXiv monthly submissions", spec, "")]

    by_group: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_subfield: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int))
    for r in load(slug, "arxiv-monthly-by-category.csv"):
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


def build_crossref(slug: str):
    return annual_series("crossref-dois-by-year.csv", "dois_created",
                         "DOI records created")(slug)


def build_github_pushes(slug: str):
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


def build_frontiermath_open(slug: str):
    """Every problem page as a dot: solve date on x, or the right edge if open.

    The event ledger supplies dates, systems and notes for the solved rows;
    the tooltip carries them so the page states what the PNG's corner note
    can only summarise.
    """
    problems = load(slug, "frontiermath-open-problems.csv")
    events = {row["slug"]: row
              for row in load(slug, "frontiermath-open-solutions.csv")}
    tier_rank = {"Breakthrough": 0, "Major advance": 1, "Solid result": 2,
                 "Moderately interesting": 3}
    problems.sort(key=lambda row: (tier_rank.get(row["notability"], 4),
                                   row["title"].lower()))
    values = []
    for row in problems:
        event = events.get(row["slug"], {})
        values.append({
            "problem": row["title"][:64],
            "date": event.get("date") or "2026-08-14",
            "status": row["status"],
            "tier": row["notability"] or "withdrawn",
            "system": event.get("system") or "—",
            "note": (event.get("note") or "")[:220],
            "url": row["source_url"],
        })
    order = [value["problem"] for value in values]
    spec = scatter(
        values, x="date", x_type="temporal", y="problem", y_type="nominal",
        y_title=None, y_sort=order,
        x_title="Solve date (unsolved rows drawn at the read date)",
        tips=[("problem", "nominal", "problem"),
              ("tier", "nominal", "notability"),
              ("status", "nominal", "status"),
              ("date", "temporal", "date"),
              ("system", "nominal", "system"),
              ("note", "nominal", "note")],
        color=("status", {"solved_ai": AI, "solved_human": HUMAN,
                          "unsolved": NEUTRAL}),
        href=True,
        height=max(220, 16 * len(values)),
    )
    return [("Per-problem status and solve dates", spec,
             "Rows are grouped by notability tier, most notable first. "
             "Unsolved problems sit at the right edge; click a point to open "
             "its page, hover for the system and notes.")]


SERIES: dict[str, object] = {
    "algorithms-cifar10": build_cifar,
    "algorithms-cvrplib": build_cvrplib,
    "algorithms-enwik9": build_enwik9,
    "algorithms-gurobi": build_gurobi,
    "algorithms-miplib": build_miplib,
    "algorithms-nanogpt": build_nanogpt,
    "algorithms-stockfish": build_stockfish,
    "cyber-curl": periodic_split_series(
        "curl-vulnerabilities-quarterly.csv", "quarter",
        {"ai_attributed": "AI-attributed", "other_attributed": "other"},
        {"AI-attributed": AI, "other": HUMAN}, "CVEs disclosed"),
    "cyber-firefox": build_firefox,
    "cyber-kev-exploited": periodic_series(
        "kev-by-quarter.csv", "quarter", "kev_added", "CVEs added to KEV",
        drop_leading_zeros=True),
    "cyber-microsoft": periodic_split_series(
        "msrc-monthly.csv", "month",
        {"explicit_ai": "explicit AI", "ai_affiliated": "AI-affiliated",
         "fuzz": "fuzzer", "other": "other"},
        {"explicit AI": AI, "AI-affiliated": AI_SOFT, "fuzzer": FUZZ,
         "other": HUMAN}, "CVEs issued"),
    "cyber-nvd-disclosed": periodic_series(
        "nvd-by-quarter.csv", "quarter", "nvd_published", "CVEs published"),
    "cyber-openssl": build_openssl,
    "cyber-oss-fuzz": periodic_series(
        "ossfuzz-by-quarter.csv", "quarter", "discoveries",
        "Records published"),
    "cyber-osv-cves": build_osv,
    "algorithms-ecdsa-circuit": build_ecdsa_circuit,
    "integer-factorization": build_factoring,
    "math-alphaevolve-inventory": build_alphaevolve_inventory,
    "math-alphaevolve-records": build_record_ladder(
        "alphaevolve-records.csv", "problem",
        "Record steps across the five groups",
        keep={"6.5", "6.7", "6.48", "6.49", "6.50"}),
    "math-antedb": build_antedb,
    "math-erdos": build_erdos_with_history,
    "math-erdos-top10": ledger_series("erdos-top10-problems.csv"),
    "math-frontiermath-open": build_frontiermath_open,
    "math-green": ledger_series("green-problems.csv"),
    "math-hilbert": ledger_series("hilbert-problems.csv"),
    "math-landau": ledger_series("landau-problems.csv"),
    "math-millennium": ledger_series("millennium-problems.csv"),
    "math-smale": ledger_series("smale-problems.csv"),
    "math-sphere-packing": build_sphere_packing,
    "math-sums-autoconvolution": build_record_ladder(
        "sums-autoconvolution-records.csv", "quantity",
        "The two record ladders"),
    "math-thurston": ledger_series("thurston-questions.csv"),
    "math-topp": ledger_series("topp-problems.csv"),
    "matrix-omega": build_omega,
    "output-arxiv": build_arxiv,
    "output-crossref": build_crossref,
    "output-github-pushes": build_github_pushes,
}

STYLE = """
body { font: 15px/1.5 -apple-system, "Segoe UI", Helvetica, Arial,
       sans-serif; color: #1f2328; margin: 0 auto; max-width: 860px;
       padding: 24px 18px 60px; }
h1 { font-size: 1.5em; margin-bottom: 0.2em; }
h2 { font-size: 1.15em; margin: 1.8em 0 0.4em; border-bottom: 1px solid
     #d8dee4; padding-bottom: 0.2em; }
h3 { font-size: 1.02em; margin: 1.4em 0 0.3em; }
img { max-width: 100%; height: auto; }
table { border-collapse: collapse; margin: 0.8em 0; display: block;
        overflow-x: auto; }
th, td { border: 1px solid #d8dee4; padding: 4px 10px; }
th { background: #f6f8fa; }
code { background: #f6f8fa; padding: 0.1em 0.3em; border-radius: 4px;
       font-size: 0.9em; }
pre { background: #f6f8fa; padding: 10px 12px; border-radius: 6px;
      overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { color: #57606a; border-left: 3px solid #d8dee4;
             margin: 0.8em 0; padding: 0 1em; }
.metric { color: #57606a; margin: 0 0 0.6em; }
.links a { margin-right: 1.2em; }
.chart { width: 100%; }
.note { color: #57606a; font-size: 0.88em; margin-top: 0.3em; }
footer { margin-top: 3em; color: #57606a; font-size: 0.85em;
         border-top: 1px solid #d8dee4; padding-top: 0.8em; }
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — ai-discovery-data</title>
<base target="_blank">
{vega}
{mathjax}
<style>{style}</style>
</head>
<body>
<p class="links"><a href="index.html" target="_self">← all series</a></p>
<h1>{title}</h1>
{body}
<footer>This page renders the folder's
<a href="{repo}/tree/main/problems/{slug}/">README</a> with the interactive
chart inline; the PNGs committed in the repository remain the archival
record, drawn from the same CSVs. Rebuilt by
<code>tools/build_docs.py</code>.</footer>
<script>
{embeds}
</script>
</body>
</html>
"""

ROOT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<base target="_blank">
<style>{style}</style>
</head>
<body>
{nav}
{body}
<footer>Rendered from
<a href="{repo}/blob/main/{source}">{source}</a> by
<code>tools/build_docs.py</code>; the repository is the archival
record.</footer>
</body>
</html>
"""


def render_page(slug: str, charts) -> str:
    body = readme_body(slug)
    blocks, embeds = [], []
    for index, (heading, spec, note) in enumerate(charts):
        div = f"chart{index}"
        blocks.append(f"<h3>{html.escape(heading)}</h3>\n"
                      f'<div id="{div}" class="chart"></div>'
                      + (f'\n<p class="note">{html.escape(note)}</p>'
                         if note else ""))
        embeds.append(
            f"vegaEmbed('#{div}', "
            + json.dumps(spec, separators=(",", ":"), sort_keys=True)
            + ", {actions: {export: true, source: false, compiled: false, "
              "editor: false}});")
    charts_html = "\n".join(blocks)
    if CHARTS_PLACEHOLDER in body:
        # The placeholder may sit inside the <p> markdown wrapped around the
        # image it replaced; the chart divs are block elements, so close and
        # reopen the paragraph around them.
        body = body.replace(f"<p>{CHARTS_PLACEHOLDER}</p>", charts_html)
        body = body.replace(CHARTS_PLACEHOLDER, f"</p>{charts_html}<p>")
    else:
        body += charts_html
    return PAGE_TEMPLATE.format(
        title=html.escape(readme_fields(slug)["title"]),
        vega=VEGA_CDN, mathjax=MATHJAX_CDN, style=STYLE, body=body,
        repo=REPO_BASE, slug=slug, embeds="\n".join(embeds))


def _rewrite_root_markdown(text: str) -> str:
    """Point a root document's repository links at their browsable homes.

    Applies to both the markdown links the prose uses and the raw HTML the
    generated tables hold: folder links become series pages, PNGs are served
    from raw URLs, data files and code go to the blob view, and the two
    sibling root documents become their own pages.
    """
    text = re.sub(r'(href=")problems/([a-z0-9-]+)/(")', r"\1\2.html\3", text)
    text = re.sub(r'(src=")(problems/[^"]+\.png)(")',
                  rf"\1{RAW_BASE}/\2\3", text)
    text = re.sub(r'(href=")(problems/[^"]+)(")', rf"\1{BLOB_BASE}/\2\3", text)
    text = re.sub(r"(?<=\])\(problems/([a-z0-9-]+)/\)", r"(\1.html)", text)
    text = re.sub(r"(?<=\])\((problems/[^)#\s]+)\)", rf"({BLOB_BASE}/\1)",
                  text)
    text = re.sub(r"(?<=\])\(README\.md\)", "(index.html)", text)
    text = re.sub(r"(?<=\])\(CUMULATIVE\.md\)", "(cumulative.html)", text)
    text = re.sub(r"(?<=\])\(ADDITIONAL-CANDIDATES\.md\)",
                  "(additional-candidates.html)", text)
    text = re.sub(r"(?<=\])\((?!https?://|#|[a-z0-9-]+\.html)([^)\s]+)\)",
                  rf"({BLOB_BASE}/\1)", text)
    return text


def render_root(source: str) -> str:
    """One of the root documents (README, CUMULATIVE, the appendix) as a page."""
    text = (ROOT / source).read_text(encoding="utf-8")
    title = re.match(r"#\s+(.+)", text).group(1).strip()
    nav = ("" if source == "README.md" else
           '<p class="links"><a href="index.html" target="_self">'
           "← all series</a></p>")
    return ROOT_TEMPLATE.format(
        title=html.escape(title), style=STYLE, nav=nav,
        body=render_markdown(_rewrite_root_markdown(text)),
        repo=REPO_BASE, source=source)


ROOT_PAGES = {
    "index.html": "README.md",
    "cumulative.html": "CUMULATIVE.md",
    "additional-candidates.html": "ADDITIONAL-CANDIDATES.md",
}


def main() -> int:
    # Series are folders whose README is tracked in git, so a sibling
    # folder still being assembled does not block the docs build.
    tracked = subprocess.run(
        ["git", "ls-files", "problems/*/README.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    folders = sorted(path.split("/")[1] for path in tracked
                     if list((ROOT / path).parent.glob("*.csv")))
    missing = [slug for slug in folders if slug not in SERIES]
    if missing:
        print("no interactive spec registered for: " + ", ".join(missing))
        print("add entries to SERIES in tools/build_docs.py")
        return 1
    DOCS.mkdir(exist_ok=True)
    for slug in folders:
        charts = SERIES[slug](slug)
        (DOCS / f"{slug}.html").write_text(render_page(slug, charts),
                                           encoding="utf-8")
    for page, source in ROOT_PAGES.items():
        (DOCS / page).write_text(render_root(source), encoding="utf-8")
    print(f"wrote docs/: {len(folders)} series pages and "
          f"{len(ROOT_PAGES)} root pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
