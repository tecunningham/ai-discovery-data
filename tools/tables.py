"""Rendering of the generated tables in README.md and CUMULATIVE.md.

tools/check.py validates the problem folders; `--write-index` renders its
results into README.md's series index and status table and CUMULATIVE.md's
cumulative index. The rendering lives here so the validator holds only
checks. The status vocabulary (CHECKS and its glyphs) lives here with the
table that displays it, and the checker imports it back — the dependency
runs one way, renderer never reaching into checker.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # the annotations only; the import runs one way at runtime
    from tools.check import Problem

ROOT = Path(__file__).resolve().parents[1]

# The index separates open-problem ledgers from mathematical records and bounds:
# the former count discrete status changes, while the latter track numerical
# quantities. Keeping them in one "mathematics" block made unlike instruments
# look interchangeable.
OPEN_PROBLEM_SLUGS = {
    "math-erdos",
    "math-erdos-top10",
    "math-frontiermath-open",
    "math-green",
    "math-hilbert",
    "math-landau",
    "math-millennium",
    "math-smale",
    "math-thurston",
    "math-topp",
}
INDEX_GROUP_ORDER = (
    "vulnerabilities",
    "open problems",
    "mathematical bounds and records",
    "algorithms",
    "outside the three domains",
)

# Arithmetic is separated from Document because the two answer different
# questions. Document asks whether the apparatus is present; Arithmetic asks
# whether the numbers the prose prints still follow from the CSV beside it, and
# only a folder shipping a check.py can answer it. Folding them together would
# show a tick for "nothing checked the numbers".
CHECKS = ("Document", "Data", "Figure", "Literature", "Arithmetic", "Refetch",
          "Reproduces")
PASS, FAIL, HAND, SKIP = "✅", "❌", "✍️", "➖"

# One mark per verdict, so the index can be read down the column. They answer
# only "did the rate of discovery change", which is why none of them says
# anything about AI: a rising series with no AI in it gets the same arrow as one
# full of it.
VERDICT_MARK = {
    "accelerating": "📈",
    "declining": "📉",
    "no acceleration": "➡️",
    "inconclusive": "❓",
    "too early": "⏳",
    "baseline": "⚪",
}

INDEX_BEGIN = "<!-- BEGIN GENERATED: series-index -->"
INDEX_END = "<!-- END GENERATED: series-index -->"
CHECKS_BEGIN = "<!-- BEGIN GENERATED: checks-table -->"
CHECKS_END = "<!-- END GENERATED: checks-table -->"

CUMULATIVE_BEGIN = "<!-- BEGIN GENERATED: cumulative-index -->"
CUMULATIVE_END = "<!-- END GENERATED: cumulative-index -->"

# GitHub clamps a markdown table to its 838-pixel content column and then
# squeezes the columns to fit, so an image in a table is only as wide as the
# prose beside it allows: at five columns of unwrapped prose the charts rendered
# 67 pixels across, which is no chart at all. Hence two columns, the details
# hard-wrapped, and a chart that gets its 400 pixels. Both numbers were measured
# against GitHub's own table CSS rather than guessed; changing either without
# re-measuring will silently shrink the charts again.
THUMB_WIDTH = 400
DETAIL_WRAP = 46

def index_group(problem: Problem) -> str:
    if problem.slug in OPEN_PROBLEM_SLUGS:
        return "open problems"
    if problem.domain == "mathematics" or problem.slug == "matrix-omega":
        return "mathematical bounds and records"
    return problem.domain

def in_reading_order(problems: list[Problem]) -> list[Problem]:
    """Index-group order, then slug — the order both generated tables use."""
    rank = {group: i for i, group in enumerate(INDEX_GROUP_ORDER)}
    return sorted(
        problems,
        key=lambda p: (rank.get(index_group(p), len(rank)), p.slug),
    )

def thumbnails(problem: Problem) -> str:
    """One primary figure linked into the folder, sized for the index table.

    Problem pages may carry diagnostics and sensitivity figures, but the main
    index is a scan of series rather than a gallery of every output.  By
    convention ``discovery-*.png`` is the primary time-series figure; when a
    folder has no such file, the first figure its own document embeds is the
    fallback — the folder's stated primary, where an alphabetical pick once
    put a sensitivity figure on the index. Written as HTML because markdown
    image syntax has no width.
    """
    if not problem.figures:
        return "<em>document + data only</em>"
    preferred = [figure for figure in problem.figures
                 if figure.name.startswith("discovery-")]
    # The cumulative view is CUMULATIVE.md's panel, never the main index's.
    fallback = [problem.folder / name for name in problem.embed_order
                if not name.startswith("cumulative-")
                and (problem.folder / name).exists()]
    figure = (preferred or fallback or problem.figures)[0]
    return (
        f'<a href="problems/{problem.slug}/">'
        f'<img src="problems/{problem.slug}/{figure.name}" width="{THUMB_WIDTH}" '
        f'alt="{problem.title}"></a>'
    )

def cumulative_thumbnail(problem: Problem) -> str:
    """The folder's shared-format panel for CUMULATIVE.md, when it has one.

    A folder without a cumulative view is still a row on that page — the page
    is the whole collection in one format, and a gap in it should be a stated
    fact rather than a silently missing series.
    """
    name = f"cumulative-{problem.slug}.png"
    if not (problem.folder / name).exists():
        return "<em>no cumulative view: not a time series</em>"
    return (
        f'<a href="problems/{problem.slug}/">'
        f'<img src="problems/{problem.slug}/{name}" width="{THUMB_WIDTH}" '
        f'alt="{problem.title}, cumulative view"></a>'
    )

def marked_verdict(problem: Problem) -> str:
    verdict = problem.fields.get("Verdict", "")
    mark = VERDICT_MARK.get(verdict.split(" —")[0].strip(), "")
    return f"{mark} {verdict}".strip()

def caption_links(problem: Problem) -> str:
    """Compact provenance links for a row in the main series index.

    The problem page is the full source ledger.  The index links directly to
    the first folder-local CSV named on its **Data:** line and the first URL on
    its **Upstream:** line: those are the primary plotted data and primary
    upstream source by the repository's documentation convention.  Additional
    inputs remain linked and explained on the problem page, keeping this strip
    short enough to scan beside a chart.
    """
    links = [f'<a href="problems/{problem.slug}/">Discussion</a>']

    named_csvs = re.findall(
        r"\(([^()/]+\.csv)\)", problem.fields.get("Data", "")
    )
    primary_csv = next(
        (name for name in named_csvs if (problem.folder / name).exists()),
        problem.csvs[0].name if problem.csvs else "",
    )
    if primary_csv:
        links.append(
            f'<a href="problems/{problem.slug}/{primary_csv}">Data</a>'
        )

    upstream = re.search(
        r"https?://[^\s<>()\[\]`\"']+", problem.fields.get("Upstream", "")
    )
    if upstream:
        links.append(f'<a href="{upstream.group(0).rstrip(".,;")}">Source</a>')

    # The interactive companion is built by tools/build_docs.py into docs/ and
    # served by GitHub Pages; the PNG in this table stays the static record.
    if (ROOT / "docs" / f"{problem.slug}.html").exists():
        links.append(
            "<a href=\"https://tecunningham.github.io/ai-discovery-data/"
            f'{problem.slug}.html">Interactive</a>'
        )

    return " · ".join(links)

def details(problem: Problem) -> str:
    """Caption metadata and provenance links for the cell beside the chart.

    Wrapped rather than left to the browser because a table column is as wide as
    its longest unbroken line, and one 90-character sentence would take the width
    the chart needs.
    """
    lines = [f'<b><a href="problems/{problem.slug}/">{problem.title}</a></b>']
    for label, value in (("Metric:", problem.fields.get("Metric", "")),
                         ("Coverage:", problem.fields.get("Coverage", "")),
                         ("Acceleration?", marked_verdict(problem))):
        wrapped = textwrap.wrap(f"{label} {value}", DETAIL_WRAP) or [label]
        wrapped[0] = wrapped[0].replace(label, f"<b>{label}</b>", 1)
        lines += wrapped
    lines.append(caption_links(problem))
    return "<br>".join(lines)

def index_rows(problems: list[Problem], thumbnail=thumbnails) -> str:
    out: list[str] = []
    groups = {index_group(problem) for problem in problems}
    for group in INDEX_GROUP_ORDER + tuple(sorted(groups - set(INDEX_GROUP_ORDER))):
        rows = [
            problem
            for problem in in_reading_order(problems)
            if index_group(problem) == group
        ]
        if not rows:
            continue
        out += [f"### {group[:1].upper()}{group[1:]}", "",
                "| Series | Chart |", "|---|---|"]
        out += [f"| {details(problem)} | {thumbnail(problem)} |"
                for problem in rows]
        out.append("")
    return "\n".join(out).rstrip()

def checks_rows(problems: list[Problem]) -> str:
    rows = in_reading_order(problems)
    out = ["| Problem | " + " | ".join(CHECKS) + " |",
           "|---|" + "---|" * len(CHECKS)]
    out += [f"| [{problem.title}](problems/{problem.slug}/) | "
            + " | ".join(problem.status[group] for group in CHECKS) + " |"
            for problem in rows]

    fetched = sum(p.status["Refetch"] == PASS for p in problems)
    hand = sum(p.status["Refetch"] == HAND for p in problems)
    checked = sum(p.status["Arithmetic"] != SKIP for p in problems)
    unchecked = len(problems) - checked
    red = sum(p.status[group] == FAIL for p in problems for group in CHECKS)
    arithmetic = f"{checked} recompute their prose arithmetic" + (
        f"; the other {unchecked} state numbers no check reads. "
        if unchecked else ". ")
    out += ["", f"{len(problems)} problems holding {sum(len(p.figures) for p in problems)} "
                f"figures and {sum(len(p.csvs) for p in problems)} data files. "
                f"{fetched} refetch from upstream and {hand} are maintained by hand "
                f"and say so. {arithmetic}"
                f"{red or 'No'} failing "
                f"{'cell' if red == 1 else 'cells'}."]
    if red:
        out += ["", "Failing:"]
        out += [f"- `{problem.slug}` {group}: {message}"
                for problem in rows
                for group in CHECKS
                for message in problem.failures.get(group, [])]
    return "\n".join(out)

def rewrite(text: str, begin: str, end: str, body: str) -> str | None:
    if begin not in text or end not in text:
        return None
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{begin}\n{body}\n{end}{tail}"
