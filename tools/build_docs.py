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

from lib.document import title as document_title  # noqa: E402

DOCS = ROOT / "docs"
PAGES_BASE = "https://tecunningham.github.io/ai-discovery-data"
REPO_BASE = "https://github.com/tecunningham/ai-discovery-data"
RAW_BASE = ("https://raw.githubusercontent.com/tecunningham/"
            "ai-discovery-data/main")
BLOB_BASE = f"{REPO_BASE}/blob/main"

MATHJAX_CDN = (
    "<script>window.MathJax = {tex: {inlineMath: [['$', '$']]}};</script>\n"
    '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">'
    "</script>"
)


CHARTS_PLACEHOLDER = "\x00CHARTS\x00"


VEGA_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>'
)


def page_title(slug: str) -> str:
    text = (ROOT / "problems" / slug / "README.md").read_text(encoding="utf-8")
    return document_title(text)


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
        title=html.escape(page_title(slug)),
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
    print(f"wrote docs/: {len(folders)} series pages and "
          f"{len(ROOT_PAGES)} root pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
