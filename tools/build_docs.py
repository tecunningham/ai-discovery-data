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

Every folder declares its own page's charts in a chart_spec.py beside its
figure.py, drawn from the shared shapes in lib/vega.py — the same
one-folder-per-problem rule the PNGs follow, so adding a series never means
editing this file. A folder with data but no chart_spec.py fails the build
loudly rather than silently shipping an index without it.

Markdown is rendered with the `markdown` package (pinned in requirements.txt
for the container; `pip install markdown` on a host that lacks it).
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.document import front_matter  # noqa: E402
from lib.document import title as document_title  # noqa: E402

DOCS = ROOT / "docs"
PAGES_BASE = "https://tecunningham.github.io/ai-discovery-data"
REPO_BASE = "https://github.com/tecunningham/ai-discovery-data"
RAW_BASE = ("https://raw.githubusercontent.com/tecunningham/"
            "ai-discovery-data/main")
BLOB_BASE = f"{REPO_BASE}/blob/main"

# The one place the pages' math is rendered; a couple of documents carry
# $…$ TeX. Inline math spans are shielded from the markdown pass in
# render_markdown.
#
# The CDN scripts here and in VEGA_CDN are pinned to exact versions with
# subresource integrity, the same standard the PNGs meet with the pinned
# renderer: a floating @major would let every published page change under a
# CDN release nobody reviewed. Each hash is the sha384 of the file exactly as
# published on npm (which jsdelivr serves verbatim for exact-version paths);
# when bumping a version, recompute it from the npm tarball, e.g.
#   curl -sL https://registry.npmjs.org/vega/-/vega-<v>.tgz | tar -xzO \
#     package/build/vega.min.js | openssl dgst -sha384 -binary | base64
MATHJAX_CDN = (
    "<script>window.MathJax = {tex: {inlineMath: [['$', '$']]}};</script>\n"
    '<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"'
    ' integrity="sha384-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2'
    'iH2VWil6r4" crossorigin="anonymous"></script>'
)


CHARTS_PLACEHOLDER = "\x00CHARTS\x00"


VEGA_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/vega@5.33.1/build/vega.min.js"'
    ' integrity="sha384-NMXhl2TbCXxcN7o4ROC56Funm78m4AylL8gMg/7Kn4YU+wrm23K9l7'
    'cY8lDRXQ9d" crossorigin="anonymous"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-lite@5.23.0/build/'
    'vega-lite.min.js" integrity="sha384-D9LYH0esGjcxQJsBuxOuXtCDJGXRWW1+Khluz'
    'WPqi0rLJmiR/ygPChefaD+rFFDQ" crossorigin="anonymous"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-embed@6.29.0/build/'
    'vega-embed.min.js" integrity="sha384-M+Ax7e/WFJpxSOF09HzI+Sj4wg9ottVd/uxm'
    'V2ItGGh02fLH28t2FAOJx3TJBap5" crossorigin="anonymous"></script>'
)


def page_title(slug: str) -> str:
    text = (ROOT / "problems" / slug / "README.md").read_text(encoding="utf-8")
    return document_title(text)


def _clip(text: str, limit: int = 180) -> str:
    """One collapsed line for a meta description, cut at a word boundary."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [text](url) -> text
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:limit].rsplit(" ", 1)[0] + "…"


def page_description(slug: str) -> str:
    """The Metric field — what the series counts — as the page description."""
    text = (ROOT / "problems" / slug / "README.md").read_text(encoding="utf-8")
    return _clip(front_matter(text).get("Metric", "") or document_title(text))


def root_description(text: str) -> str:
    """A root document's first prose paragraph, for its page description."""
    for block in re.split(r"\n\s*\n", text)[1:]:
        if not block.lstrip().startswith(("#", "|", "<", "-", ">", "!")):
            return _clip(block)
    return ""


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
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
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
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
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
        title=html.escape(page_title(slug)),
        description=html.escape(page_description(slug)),
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
        description=html.escape(root_description(text)),
        body=render_markdown(_rewrite_root_markdown(text)),
        repo=REPO_BASE, source=source)


ROOT_PAGES = {
    "index.html": "README.md",
    "cumulative.html": "CUMULATIVE.md",
    "additional-candidates.html": "ADDITIONAL-CANDIDATES.md",
}


# ---------------------------------------------------------------- compare.html

COMPARE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cumulative series compared — ai-discovery-data</title>
<meta name="description" content="{description}">
<meta property="og:title" content="Cumulative series compared">
<meta property="og:description" content="{description}">
<base target="_blank">
{vega}
<style>{style}
body {{ max-width: 1180px; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 8px 22px; align-items: center;
             margin: 0.8em 0; font-size: 0.92em; }}
.controls label {{ white-space: nowrap; }}
.controls input[type=number] {{ width: 5.5em; }}
.layout {{ display: flex; gap: 20px; align-items: flex-start; }}
.picker {{ flex: 0 0 300px; font-size: 0.86em; max-height: 560px;
           overflow-y: auto; border: 1px solid #d8dee4; border-radius: 6px;
           padding: 6px 10px; }}
.picker h4 {{ margin: 0.7em 0 0.2em; font-size: 1em; display: flex;
              justify-content: space-between; align-items: baseline; }}
.picker h4 span {{ font-weight: normal; }}
.picker h4 span a {{ margin-left: 6px; font-size: 0.85em; }}
.picker label {{ display: block; line-height: 1.35; margin: 2px 0; }}
.picker .swatch {{ display: inline-block; width: 10px; height: 10px;
                   border-radius: 2px; margin-right: 5px; vertical-align: -1px; }}
.chartwrap {{ flex: 1 1 auto; min-width: 0; }}
#chart {{ width: 100%; }}
.dropped {{ color: #9a6700; font-size: 0.85em; margin-top: 0.4em; }}
@media (max-width: 800px) {{
  .layout {{ flex-direction: column; }}
  .picker {{ flex-basis: auto; max-height: 260px; width: 100%;
             box-sizing: border-box; }}
}}
</style>
</head>
<body>
<p class="links"><a href="index.html" target="_self">← all series</a>
<a href="cumulative.html" target="_self">cumulative index</a></p>
<h1>Cumulative series compared</h1>
<p class="metric">Every panel of the <a href="cumulative.html"
target="_self">cumulative index</a> on one chart: the same step lines the
committed PNGs draw, from the same numbers. Pick series on the left; the
defaults index each line to its value on the reference date and use a log
axis, so equal slopes are equal growth rates whatever the units.</p>
<div class="controls">
  <label>Y axis:
    <select id="scale"><option value="log">log</option>
    <option value="linear">linear</option></select></label>
  <label>Normalise:
    <select id="norm">
      <option value="index">= 1 on reference date</option>
      <option value="share">share of latest value</option>
      <option value="raw">raw values</option></select></label>
  <label>Reference <input id="ref" type="number" step="1" min="1900"
    max="2026" value="2020"></label>
  <label>From <input id="from" type="number" step="1" min="1900" max="2026"
    value="2000"></label>
  <label>Colour by:
    <select id="colour"><option value="series">series</option>
    <option value="domain">domain</option></select></label>
</div>
<div class="layout">
  <div class="picker" id="picker"></div>
  <div class="chartwrap">
    <div id="chart"></div>
    <p class="dropped" id="dropped"></p>
  </div>
</div>
<footer>Lines are read from each folder's <code>cumulative-&lt;slug&gt;.json</code>,
written by the folder's <code>figure.py</code> beside its PNG and compared in
CI; <em>counts</em> and <em>events</em> rise from zero, <em>remaining</em>
falls toward zero, and a <em>staircase</em> is a standing record's own value
(the tooltip says which direction is better). A series with no value on the
reference date, or a zero there, is listed under the chart instead of drawn.
Rebuilt by <code>tools/build_docs.py</code>.</footer>
<script>
const SERIES = {series};
const DOMAINS = {domains};
const PALETTE = ["#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f","#edc948",
  "#b07aa1","#ff9da7","#9c755f","#bab0ac","#1f77b4","#ff7f0e","#2ca02c",
  "#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf",
  "#393b79","#637939","#8c6d31","#843c39","#7b4173","#5254a3","#8ca252",
  "#bd9e39","#ad494a","#a55194","#6b6ecf","#b5cf6b","#e7ba52","#d6616b",
  "#ce6dbd","#9c9ede","#cedb9c","#e7cb94","#e7969c","#de9ed6"];
const DOMAIN_COLOURS = {domain_colours};
SERIES.forEach((s, i) => {{ s.colour = PALETTE[i % PALETTE.length]; }});

const $ = id => document.getElementById(id);
const state = {{ selected: new Set(SERIES.map(s => s.key)) }};

function readHash() {{
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.has("s")) state.selected = new Set(h.get("s").split(",").filter(Boolean));
  for (const k of ["scale", "norm", "ref", "from", "colour"])
    if (h.has(k)) $(k).value = h.get(k);
}}
function writeHash() {{
  const h = new URLSearchParams();
  if (state.selected.size !== SERIES.length) h.set("s", [...state.selected].join(","));
  for (const k of ["scale", "norm", "ref", "from", "colour"]) h.set(k, $(k).value);
  history.replaceState(null, "", "#" + h.toString());
}}

function toDate(yf) {{
  const year = Math.floor(yf);
  return new Date(Date.UTC(year, 0, 1) + (yf - year) * 365.25 * 864e5);
}}
function valueAt(s, t) {{  // step-after: the last value observed at or before t
  let v = null;
  for (let i = 0; i < s.x.length; i++) {{ if (s.x[i] <= t) v = s.y[i]; else break; }}
  return v;
}}

function buildPicker() {{
  const box = $("picker");
  box.innerHTML = "";
  for (const domain of DOMAINS) {{
    const members = SERIES.filter(s => s.domain === domain);
    if (!members.length) continue;
    const h = document.createElement("h4");
    h.innerHTML = `${{domain}} <span><a href="#" data-all="${{domain}}">all</a>` +
                  `<a href="#" data-none="${{domain}}">none</a></span>`;
    box.appendChild(h);
    for (const s of members) {{
      const label = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox"; cb.checked = state.selected.has(s.key); cb.dataset.key = s.key;
      label.appendChild(cb);
      const sw = document.createElement("span");
      sw.className = "swatch"; sw.style.background = s.colour;
      label.appendChild(sw);
      label.appendChild(document.createTextNode(" " + s.name));
      label.title = s.subtitle;
      box.appendChild(label);
    }}
  }}
  box.onchange = e => {{
    if (e.target.dataset.key) {{
      e.target.checked ? state.selected.add(e.target.dataset.key)
                       : state.selected.delete(e.target.dataset.key);
      render();
    }}
  }};
  box.onclick = e => {{
    const all = e.target.dataset.all, none = e.target.dataset.none;
    if (!all && !none) return;
    e.preventDefault();
    for (const s of SERIES) if (s.domain === (all || none))
      all ? state.selected.add(s.key) : state.selected.delete(s.key);
    box.querySelectorAll("input").forEach(cb => cb.checked = state.selected.has(cb.dataset.key));
    render();
  }};
}}

function render() {{
  const scale = $("scale").value, norm = $("norm").value;
  const ref = +$("ref").value, from = +$("from").value, byDomain = $("colour").value === "domain";
  const values = [], dropped = [];
  for (const s of SERIES) {{
    if (!state.selected.has(s.key)) continue;
    let base = 1;
    if (norm === "index") {{
      base = valueAt(s, ref + 0.5);  // mid-year of the reference year
      if (!(base > 0)) {{
        // Nothing stood in the reference year (the series starts later, or
        // was still at zero): index to its first non-zero value instead,
        // and say so under the chart.
        const i = s.y.findIndex(v => v > 0);
        if (i >= 0 && s.x[i] > ref) {{
          base = s.y[i];
          dropped.push(`${{s.name}} is indexed to its first value (${{Math.floor(s.x[i])}}) instead of ${{ref}}`);
        }} else base = null;
      }}
    }} else if (norm === "share") base = s.kind === "remaining" ? s.y[0] : s.y[s.y.length - 1];
    if (norm !== "raw" && !(base > 0)) {{
      dropped.push(`${{s.name}} is not drawn (no value to normalise by)`);
      continue;
    }}
    const xs = s.x.slice(), ys = s.y.slice();
    if (xs[xs.length - 1] < s.now) {{ xs.push(s.now); ys.push(ys[ys.length - 1]); }}
    // Enter the window on the value already standing at its left edge.
    const startV = valueAt(s, from);
    const pts = [];
    if (startV !== null && xs[0] < from) pts.push([from, startV]);
    for (let i = 0; i < xs.length; i++) if (xs[i] >= from) pts.push([xs[i], ys[i]]);
    let kept = 0;
    for (const [x, y] of pts) {{
      const v = y / base;
      if (scale === "log" && !(v > 0)) continue;
      kept++;
      values.push({{ name: s.name, domain: s.domain, date: toDate(x).toISOString(),
                    value: v, raw: y, unit: s.ylabel, note: s.subtitle, url: s.url,
                    colour: byDomain ? DOMAIN_COLOURS[s.domain] : s.colour }});
    }}
    if (!kept) dropped.push(`${{s.name}} has nothing to draw in this window`);
  }}
  $("dropped").textContent = dropped.length ? "Note: " + dropped.join("; ") + "." : "";
  const names = [...new Set(values.map(v => v.name))];
  const colours = names.map(n => values.find(v => v.name === n).colour);
  const yTitle = norm === "index" ? `value relative to ${{ref}} (= 1)` :
                 norm === "share" ? "share of latest value" : "value (mixed units)";
  const spec = {{
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    width: "container", height: 520,
    data: {{ values }},
    params: [{{ name: "pick", select: {{ type: "point", fields: ["name"], on: "pointerover",
                                         clear: "pointerout" }} }}],
    mark: {{ type: "line", interpolate: "step-after", strokeWidth: 1.7, clip: true }},
    encoding: {{
      x: {{ field: "date", type: "temporal", title: null,
           axis: {{ format: "%Y", labelOverlap: "greedy", tickCount: "year" }} }},
      y: {{ field: "value", type: "quantitative", title: yTitle,
           scale: {{ type: scale, nice: scale !== "log", zero: scale !== "log" }},
           axis: {{ format: norm === "raw" ? "~s" : "~g" }} }},
      color: {{ field: "name", type: "nominal", title: null, legend: null,
               scale: {{ domain: names, range: colours }} }},
      opacity: {{ condition: {{ param: "pick", value: 1, empty: true }}, value: 0.18 }},
      strokeWidth: {{ condition: {{ param: "pick", value: 2.6, empty: false }}, value: 1.6 }},
      href: {{ field: "url" }},
      tooltip: [{{ field: "name", title: "series" }},
                {{ field: "date", type: "temporal", title: "date", format: "%Y-%m-%d" }},
                {{ field: "value", type: "quantitative", title: yTitle, format: ".3~g" }},
                {{ field: "raw", type: "quantitative", title: "value", format: ",.6~g" }},
                {{ field: "unit", title: "unit" }},
                {{ field: "note", title: "reading" }}]
    }},
    config: {{ view: {{ stroke: null }}, axis: {{ grid: true, gridColor: "#eef1f4" }} }}
  }};
  vegaEmbed("#chart", spec, {{ actions: {{ export: true, source: false, compiled: false,
                                           editor: false }} }});
  writeHash();
}}

readHash();
buildPicker();
for (const k of ["scale", "norm", "ref", "from", "colour"]) $(k).onchange = render;
render();
</script>
</body>
</html>
"""

# The domain vocabulary of FORMAT.md front matter, in the index's order, and
# one hue each for the colour-by-domain view (the collection's slate for the
# denominator frames outside the three domains).
COMPARE_DOMAINS = ("vulnerabilities", "mathematics", "algorithms",
                   "outside the three domains")
COMPARE_DOMAIN_COLOURS = {"vulnerabilities": "#e15759", "mathematics": "#4e79a7",
                          "algorithms": "#59a14f",
                          "outside the three domains": "#8c96a0"}


def compare_series() -> list[dict]:
    """Every cumulative panel's lines, from the sidecars beside the PNGs.

    One entry per drawn line: a folder whose panel holds two or three ladders
    contributes each as its own selectable series, named after the folder
    and the line's own label.
    """
    out = []
    for sidecar in sorted((ROOT / "problems").glob("*/cumulative-*.json")):
        slug = sidecar.parent.name
        text = (sidecar.parent / "README.md").read_text(encoding="utf-8")
        domain = front_matter(text).get("Domain", "").lower()
        if domain not in COMPARE_DOMAINS:
            domain = COMPARE_DOMAINS[-1]
        panel = json.loads(sidecar.read_text(encoding="utf-8"))
        folder_title = document_title(text) or slug
        for line in panel["series"]:
            name = folder_title if not line["label"] else \
                f"{folder_title} — {line['label']}"
            out.append({
                "key": slug if not line["label"] else f"{slug}:{line['label']}",
                "slug": slug, "name": name, "domain": domain,
                "kind": panel["kind"], "subtitle": panel["subtitle"],
                "ylabel": panel["ylabel"], "now": panel["now"],
                "url": f"{slug}.html", "x": line["x"], "y": line["y"],
            })
    rank = {d: i for i, d in enumerate(COMPARE_DOMAINS)}
    out.sort(key=lambda s: (rank[s["domain"]], s["name"]))
    return out


def render_compare() -> str:
    series = compare_series()
    description = (f"{len(series)} cumulative series from the collection on "
                   "one interactive chart, with a log axis and normalisation "
                   "to a reference date.")
    dump = lambda value: json.dumps(value, separators=(",", ":"),  # noqa: E731
                                    sort_keys=True, ensure_ascii=False)
    return COMPARE_TEMPLATE.format(
        description=html.escape(description), vega=VEGA_CDN, style=STYLE,
        series=dump(series), domains=dump(list(COMPARE_DOMAINS)),
        domain_colours=dump(COMPARE_DOMAIN_COLOURS))


# Pages built from the folders as a whole rather than from one document.
GENERATED_PAGES = {"compare.html": render_compare}


def charts_for(slug: str):
    """The folder's declared interactive charts, from its chart_spec.py.

    Loaded by path, the same way tools/check.py loads this module: the
    problem folders are not a package, and the docs build should read the
    file beside the data it renders.
    """
    spec_path = ROOT / "problems" / slug / "chart_spec.py"
    spec = importlib.util.spec_from_file_location(f"chart_spec_{slug}",
                                                  spec_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.charts(slug)



def main() -> int:
    # The same discovery rule stale_docs() in tools/check.py uses: a series
    # is a problem folder holding data. One rule, so the build and the
    # staleness check can never disagree about the page set.
    folders = sorted(
        path.name for path in (ROOT / "problems").iterdir()
        if path.is_dir() and any(path.glob("*.csv")))
    missing = [slug for slug in folders
               if not (ROOT / "problems" / slug / "chart_spec.py").exists()]
    if missing:
        print("no chart_spec.py beside the data in: " + ", ".join(missing))
        print("declare the page's charts there, using lib/vega.py's shapes")
        return 1
    DOCS.mkdir(exist_ok=True)
    for slug in folders:
        (DOCS / f"{slug}.html").write_text(
            render_page(slug, charts_for(slug)), encoding="utf-8")
    for page, source in ROOT_PAGES.items():
        (DOCS / page).write_text(render_root(source), encoding="utf-8")
    for page, render in GENERATED_PAGES.items():
        (DOCS / page).write_text(render(), encoding="utf-8")
    print(f"wrote docs/: {len(folders)} series pages, {len(ROOT_PAGES)} root "
          f"pages and {len(GENERATED_PAGES)} generated page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
