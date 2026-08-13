#!/usr/bin/env python3
"""Consistency checks over problems/, lib/ and references.bib.

    python3 tools/check.py                 # report, exit non-zero on failure
    python3 tools/check.py --reproduce     # also redraw every figure and compare
    python3 tools/check.py --write-index   # rewrite README's two generated tables

What this is for. The repository's claim is that every chart can be traced to a
public source, so the failure mode that matters is a file arriving without the
apparatus that makes it checkable: a figure nobody documents, a CSV nobody plots
or explains, a citation with no bibliography entry, a series whose provenance is
nowhere stated. None of those are visible by reading any single file.

The layout does most of the work: one folder per problem, holding its data, the
script that fetches it, the script that draws it, the figure, and the document.
So the checks are mostly local — does this folder account for its own contents —
and the two cross-folder rules are that sibling links resolve and that nothing is
left lying outside a folder.

Metadata is parsed out of the prose rather than hidden in front matter, because a
reader of the document should see the same source and coverage the checker does.

Every check belongs to one of the six groups the README's status table has a
column for, so a red cell there and a FAIL line here are the same fact stated
twice. The grouping is the only reason the checks are collected into named
buckets rather than one list: a reader wants to know which kind of thing is
wrong with a series, and "the figure is fine but the data is unlinked" is a
different situation from the reverse.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import textwrap
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "problems"
BIB = ROOT / "references.bib"
README = ROOT / "README.md"

FIELDS = ("Domain", "Metric", "Coverage", "Data", "Upstream", "Verdict")
SECTIONS = ("The problem", "What the chart shows", "How the chart was built",
            "What it cannot support", "LLM contributions", "Related literature")
VERDICTS = {"accelerating", "no acceleration", "declining", "inconclusive",
            "too early", "baseline"}
# The index separates open-problem ledgers from mathematical records and bounds:
# the former count discrete status changes, while the latter track numerical
# quantities. Keeping them in one "mathematics" block made unlike instruments
# look interchangeable.
OPEN_PROBLEM_SLUGS = {
    "math-erdos",
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

# A folder with no fetch.py has to say how its CSV is maintained, in the section
# a reader goes to for exactly that, so a series nobody can refetch is a stated
# fact rather than an omission. Checked as vocabulary rather than as a fixed
# field because the reasons genuinely differ: hand transcription from prose, a
# hand-scored ledger, or generation by a sibling folder's fetcher.
NO_FETCHER_REASONS = re.compile(
    r"transcrib|by hand|hand-scored|hand-collected|assembled from|no fetcher"
    r"|no maintained ledger|generated, not separately maintained|written by hand",
    re.I,
)
# A folder can keep its CSVs and document without a chart, when the series is
# not plottable as a measured time series (text-stated anchors, a claimed rate,
# and so on). Same pattern as a missing fetcher: the document has to say so in
# the section a reader opens for that.
NO_FIGURE_REASONS = re.compile(
    r"no chart|no figure|not plotted|no visualization|not a digitized series",
    re.I,
)

INDEX_BEGIN = "<!-- BEGIN GENERATED: series-index -->"
INDEX_END = "<!-- END GENERATED: series-index -->"
CHECKS_BEGIN = "<!-- BEGIN GENERATED: checks-table -->"
CHECKS_END = "<!-- END GENERATED: checks-table -->"

# GitHub clamps a markdown table to its 838-pixel content column and then
# squeezes the columns to fit, so an image in a table is only as wide as the
# prose beside it allows: at five columns of unwrapped prose the charts rendered
# 67 pixels across, which is no chart at all. Hence two columns, the details
# hard-wrapped, and a chart that gets its 400 pixels. Both numbers were measured
# against GitHub's own table CSS rather than guessed; changing either without
# re-measuring will silently shrink the charts again.
THUMB_WIDTH = 400
DETAIL_WRAP = 46


class Problem:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.slug = folder.name
        self.doc = folder / "README.md"
        self.text = self.doc.read_text(encoding="utf-8") if self.doc.exists() else ""
        title = re.search(r"^#\s+(.+)$", self.text, re.M)
        self.title = title.group(1).strip() if title else ""
        # Folder-local links only: an embed or a data link reaching outside the
        # folder means the split is incomplete.
        self.embedded = set(re.findall(r"!\[[^\]]*\]\(([^)/]+\.png)\)", self.text))
        self.linked_csvs = set(re.findall(r"\(([^)/]+\.csv)\)", self.text))
        self.siblings = set(re.findall(r"\(\.\./([a-z0-9-]+)/README\.md\)", self.text))
        # A bracket can hold several keys, `[@a; @b]`. Matching `@key]` would see
        # only the last of them and leave a typo in any earlier key unchecked.
        self.citations = {key
                          for group in re.findall(r"\[@[^\]]*\]", self.text)
                          for key in re.findall(r"@([A-Za-z0-9_:-]+)", group)}
        self.fields = {}
        for field in FIELDS:
            match = re.search(rf"^\*\*{field}:\*\*\s*(.+)$", self.text, re.M)
            if match:
                self.fields[field] = match.group(1).strip()
        # Reproduction is off unless asked for, since it redraws every figure.
        self.status = {name: SKIP for name in CHECKS}
        self.failures: dict[str, list[str]] = {}

    @property
    def figures(self) -> list[Path]:
        return sorted(self.folder.glob("*.png"))

    @property
    def csvs(self) -> list[Path]:
        return sorted(self.folder.glob("*.csv"))

    @property
    def domain(self) -> str:
        return self.fields.get("Domain", "?")

    def fail(self, group: str, message: str) -> None:
        self.failures.setdefault(group, []).append(message)
        self.status[group] = FAIL

    def check(self, keys: set[str], slugs: set[str]) -> None:
        if not self.doc.exists():
            for group in CHECKS:
                self.status[group] = FAIL
            self.fail("Document", "no README.md")
            return

        for field in FIELDS:
            if field not in self.fields:
                self.fail("Document", f"no **{field}:** line")
        verdict = self.fields.get("Verdict", "").split(" —")[0].strip()
        if verdict and verdict not in VERDICTS:
            self.fail("Document",
                      f"verdict {verdict!r} not one of {sorted(VERDICTS)}")
        for section in SECTIONS:
            if f"## {section}" not in self.text:
                self.fail("Document", f"no '## {section}' section")
        if "http" not in self.fields.get("Upstream", ""):
            self.fail("Document", "**Upstream:** names no URL")
        for sibling in sorted(self.siblings - slugs):
            self.fail("Document",
                      f"links ../{sibling}/README.md, which does not exist")

        figure_script = self.folder / "figure.py"
        built = re.search(r"## How the chart was built\n(.*?)(?=\n## |\Z)",
                          self.text, re.S)
        built_body = built.group(1) if built else ""
        if not figure_script.exists() and not self.figures:
            if NO_FIGURE_REASONS.search(built_body) or NO_FIGURE_REASONS.search(self.text):
                self.status["Figure"] = HAND
            else:
                self.fail("Figure", "no figure.py")
                self.fail("Figure", "no figure on disk")
        else:
            if not figure_script.exists():
                self.fail("Figure", "no figure.py")
            if not self.figures:
                self.fail("Figure", "no figure on disk")
            script_text = (figure_script.read_text(encoding="utf-8")
                           if figure_script.exists() else "")
            for figure in self.figures:
                if figure.name not in self.embedded:
                    self.fail("Figure", f"{figure.name} is generated but the document "
                                        "does not embed it")
                if figure.name not in script_text:
                    self.fail("Figure", f"{figure.name} is not named in figure.py, so "
                                        "nothing rebuilds it")
            for name in sorted(self.embedded):
                if not (self.folder / name).exists():
                    self.fail("Figure", f"embeds {name}, which is not in the folder")

        if not self.csvs:
            self.fail("Data", "holds no CSV")
        for csv_path in self.csvs:
            if csv_path.name not in self.linked_csvs:
                self.fail("Data", f"{csv_path.name} is vendored but the document "
                                  "does not link it")
            for message in csv_errors(csv_path):
                self.fail("Data", message)
        for name in sorted(self.linked_csvs):
            if not (self.folder / name).exists():
                self.fail("Data", f"links {name}, which is not in the folder")

        for key in sorted(self.citations - keys):
            self.fail("Literature", f"citation @{key} has no bibliography entry")

        if (self.folder / "fetch.py").exists():
            self.status["Refetch"] = PASS
        elif NO_FETCHER_REASONS.search(built_body):
            self.status["Refetch"] = HAND
        else:
            self.fail("Refetch", "has no fetch.py, and 'How the chart was "
                                 "built' does not say how the data is "
                                 "maintained instead")

        folder_check = self.folder / "check.py"
        if folder_check.exists():
            result = subprocess.run(
                [sys.executable, str(folder_check)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                output = (result.stdout + result.stderr).strip()
                for message in output.splitlines() or ["folder check failed"]:
                    self.fail("Arithmetic", f"check.py: {message}")
            else:
                self.status["Arithmetic"] = PASS
        else:
            # No check.py, so nothing read this folder's numbers. That is a
            # gap to show, not a pass to award.
            self.status["Arithmetic"] = SKIP

        for group in ("Document", "Data", "Figure", "Literature"):
            if self.status[group] == SKIP:
                self.status[group] = PASS

    def messages(self) -> list[str]:
        return [f"{self.slug}: {message}"
                for group in CHECKS
                for message in self.failures.get(group, [])]


def bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(re.findall(r"^@[a-zA-Z]+\{([^,\s]+)", BIB.read_text(encoding="utf-8"), re.M))


def check_chart_as_of(problems: list[Problem]) -> None:
    """Fail if vendored data has advanced beyond the chart snapshot date."""
    chart_text = (ROOT / "lib/chart.py").read_text(encoding="utf-8")
    match = re.search(
        r"^AS_OF_DATE\s*=\s*date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)",
        chart_text,
        re.M,
    )
    if not match:
        for problem in problems:
            problem.fail("Figure", "lib/chart.py has no parseable AS_OF_DATE")
        return
    as_of = date(*(int(part) for part in match.groups()))
    date_fields = {"date", "published", "announced", "data_through", "release_date"}
    for problem in problems:
        newest: date | None = None
        source = ""
        for path in problem.csvs:
            with path.open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    for field, value in row.items():
                        value = value or ""
                        candidate: date | None = None
                        if field == "year" and re.fullmatch(r"20\d{2}", value):
                            candidate = date(int(value), 1, 1)
                        elif field in date_fields or field.endswith("_date"):
                            if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value):
                                candidate = date.fromisoformat(value)
                        if candidate and (newest is None or candidate > newest):
                            newest, source = candidate, path.name
        if newest and newest > as_of:
            problem.fail(
                "Figure",
                f"{source} contains {newest.isoformat()}, newer than "
                f"lib/chart.py AS_OF_DATE {as_of.isoformat()}",
            )


def csv_errors(path: Path) -> list[str]:
    """Report structural CSV damage before a figure silently ignores it."""
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = csv.reader(handle, strict=True)
            header = next(rows, None)
            if header is None:
                return [f"{path.name} is empty"]
            errors = []
            duplicate_fields = [
                field for field, count in Counter(header).items() if count > 1
            ]
            if duplicate_fields:
                errors.append(
                    f"{path.name} has duplicate column(s): "
                    f"{', '.join(duplicate_fields)}"
                )
            if any(not field.strip() for field in header):
                errors.append(f"{path.name} has an empty column name")
            url_columns = [
                (index, field)
                for index, field in enumerate(header)
                if field.endswith("_url")
            ]
            finder_columns = [
                index
                for index, field in enumerate(header)
                if field in {"finder", "reporter"}
            ]
            for line_number, row in enumerate(rows, 2):
                if len(row) != len(header):
                    errors.append(
                        f"{path.name}:{line_number} has {len(row)} fields; "
                        f"header has {len(header)}"
                    )
                    continue
                for index, field in url_columns:
                    # Evidence URLs are conditional: an empty value is expected
                    # when the corresponding classification is false. Folder
                    # semantic checks enforce that classified rows supply one.
                    if field == "ai_evidence_url" and not row[index]:
                        continue
                    if not row[index].startswith(("http://", "https://")):
                        errors.append(
                            f"{path.name}:{line_number} has no public URL in "
                            f"{field}"
                        )
                for index in finder_columns:
                    finder = row[index]
                    if len(finder) == 160:
                        errors.append(
                            f"{path.name}:{line_number} finder is exactly 160 "
                            "characters and may retain an old parser truncation"
                        )
                    if finder.count("(") != finder.count(")"):
                        errors.append(
                            f"{path.name}:{line_number} finder has unbalanced "
                            "parentheses and may be a split credit"
                        )
            return errors
    except (OSError, UnicodeError, csv.Error) as error:
        return [f"{path.name} cannot be parsed as CSV: {error}"]


def reproduce(problems: list[Problem]) -> None:
    """Redraw every figure and check the committed PNG is what its script draws.

    The claim this repository makes is that a chart can be rebuilt from the CSV
    beside it, which is only worth anything if the file in git is the one the
    script produces today. A figure hand-edited after generation, or left behind
    when its data was refetched, is invisible to every other check here.

    The original bytes are put back afterwards, so a stale figure is reported
    rather than quietly staged for commit.
    """
    print(f"redrawing {len(problems)} folders to compare with the committed "
          f"figures (no network)", flush=True)
    for problem in problems:
        script = problem.folder / "figure.py"
        if not script.exists():
            # A documented chartless folder has nothing to reproduce.
            if problem.status.get("Figure") == HAND:
                problem.status["Reproduces"] = HAND
            else:
                problem.status["Reproduces"] = FAIL
            continue
        before = {path: path.read_bytes() for path in problem.figures}
        run = subprocess.run([sys.executable, str(script)], cwd=ROOT,
                             capture_output=True, text=True)
        stale = [path for path, data in before.items() if path.read_bytes() != data]
        for path in stale:  # leave the tree as it was found
            path.write_bytes(before[path])
        if run.returncode != 0:
            said = (run.stderr or run.stdout).strip().splitlines()
            problem.fail("Reproduces", f"figure.py exited {run.returncode}: "
                                       f"{said[-1] if said else 'no output'}")
            continue
        if stale:
            problem.fail("Reproduces",
                         f"{', '.join(p.name for p in stale)} differs from what "
                         "figure.py draws today, so the committed figure is stale")
        for path in problem.figures:
            if path not in before:
                problem.fail("Reproduces", f"figure.py wrote {path.name}, which "
                                           "was not committed")
        if problem.status["Reproduces"] == SKIP:
            problem.status["Reproduces"] = PASS


def duplicate_names(problems: list[Problem]) -> None:
    """Filenames must be unique across folders, not just within one.

    The blog repository reads these CSVs by name through its own resolver, since
    it has no reason to know which folder a series ended up in. Two folders both
    holding a `finders.csv` would make that lookup ambiguous, so the names carry
    the series: `curl-finders.csv`, not `finders.csv`.
    """
    seen: dict[str, Problem] = {}
    for problem in problems:
        for path in problem.csvs + problem.figures:
            first = seen.get(path.name)
            if first is not None:
                group = "Data" if path.suffix == ".csv" else "Figure"
                problem.fail(group, f"{path.name} collides with the one in "
                                    f"{first.slug}/; names must be unique across "
                                    "folders")
            seen[path.name] = problem
    return None


def unused_bib(problems: list[Problem], keys: set[str]) -> list[str]:
    """A bibliography entry no document cites.

    The reverse of the per-problem citation check, and it catches the residue of
    a rewrite: prose gets reworded, the citation goes with it, and the entry sits
    in references.bib looking like part of the apparatus.
    """
    cited = {key for problem in problems for key in problem.citations}
    return [f"references.bib: @{key} is cited by no document"
            for key in sorted(keys - cited)]


def dead_links(problems: list[Problem], timeout: float = 25.0) -> list[str]:
    """Every URL in every document, fetched. Opt-in: this one needs the network.

    A source that has moved is not visible from inside the repository, and the
    documents are mostly links. Kept out of the default run because it is the
    only check that can fail for a reason that is nobody's fault.
    """
    import urllib.error
    import urllib.request

    urls: dict[str, str] = {}
    for problem in problems:
        for url in re.findall(r"https?://[^\s<>()\[\]`\"']+", problem.text):
            urls.setdefault(url.rstrip(".,;"), problem.slug)
    # The bibliography's url fields rot like any other link, and unlike the
    # documents' they were checked by nothing (found in review: a bib entry
    # pointing at a 404 while its README pointed at the live page).
    if BIB.exists():
        for url in re.findall(r"^\s*url\s*=\s*\{([^}]+)\}",
                              BIB.read_text(encoding="utf-8"), re.M):
            urls.setdefault(url.replace("\\_", "_").rstrip(".,;"),
                            "references.bib")
    print(f"fetching {len(urls)} URLs from {len(problems)} documents "
          "and references.bib", flush=True)
    out = []
    for url, slug in sorted(urls.items()):
        request = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent": "ai-discovery-data link check"})
        try:
            urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            # 403 and 405 are how a live server says "not like that", which is a
            # bot policy rather than a missing page.
            if error.code not in (403, 405):
                out.append(f"{slug}: {url} returns {error.code}")
        except Exception as error:  # DNS, TLS, timeout
            out.append(f"{slug}: {url} unreachable ({type(error).__name__})")
    return out


def strays() -> list[str]:
    """Files left outside a problem folder by an incomplete migration."""
    out = []
    for legacy in ("data", "figures"):
        folder = ROOT / legacy
        if not folder.exists():
            continue
        left = sorted(p.name for p in folder.iterdir() if p.suffix in (".csv", ".png"))
        if left:
            out.append(f"{legacy}/ still holds {len(left)} file(s): {', '.join(left)}")
        else:
            out.append(f"{legacy}/ is empty and should be removed")
    for orphan in sorted(PROBLEMS.glob("*.md")):
        out.append(f"problems/{orphan.name} is a loose document, not a folder")
    return out


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
    folder has no such file, its first (usually only) figure is the fallback.
    Written as HTML because markdown image syntax has no width.
    """
    if not problem.figures:
        return "<em>document + data only</em>"
    preferred = [figure for figure in problem.figures
                 if figure.name.startswith("discovery-")]
    figure = preferred[0] if preferred else problem.figures[0]
    return (
        f'<a href="problems/{problem.slug}/">'
        f'<img src="problems/{problem.slug}/{figure.name}" width="{THUMB_WIDTH}" '
        f'alt="{problem.title}"></a>'
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


def index_rows(problems: list[Problem]) -> str:
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
        out += [f"| {details(problem)} | {thumbnails(problem)} |"
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
    red = sum(p.status[group] == FAIL for p in problems for group in CHECKS)
    out += ["", f"{len(problems)} problems holding {sum(len(p.figures) for p in problems)} "
                f"figures and {sum(len(p.csvs) for p in problems)} data files. "
                f"{fetched} refetch from upstream and {hand} are maintained by hand "
                f"and say so. {checked} recompute their prose arithmetic; the other "
                f"{len(problems) - checked} state numbers no check reads. "
                f"{red or 'No'} failing "
                f"{'cell' if red == 1 else 'cells'}."]
    if red:
        out += ["", "Failing:"]
        out += [f"- `{problem.slug}` {group}: {message}"
                for problem in rows
                for group in CHECKS
                for message in problem.failures.get(group, [])]
    return "\n".join(out)


def stale_readme(problems: list[Problem]) -> list[str]:
    """The committed generated tables must match what the folders generate now.

    A series can be merged without `make index` having run, and nothing else
    notices: every folder-local check passes, CI reproduces every figure, and
    the README simply stays one series short. The series index is compared in
    full because the fast path can compute all of it; the status table's cells
    depend on the reproduction run, so only its row set is checked here.
    """
    text = README.read_text(encoding="utf-8") if README.exists() else ""
    out = []
    for begin, end, what in ((INDEX_BEGIN, INDEX_END, "series index"),
                             (CHECKS_BEGIN, CHECKS_END, "status table")):
        if begin not in text or end not in text:
            out.append(f"README.md has no {what} markers")
    if out:
        return out
    committed = text.split(INDEX_BEGIN, 1)[1].split(INDEX_END, 1)[0].strip()
    if committed != index_rows(problems).strip():
        out.append("README.md series index does not match the problem folders; "
                   "run `make index`")
    checks_block = text.split(CHECKS_BEGIN, 1)[1].split(CHECKS_END, 1)[0]
    for problem in problems:
        if f"(problems/{problem.slug}/)" not in checks_block:
            out.append(f"README.md status table has no row for {problem.slug}; "
                       "run `make index`")
    return out


def stale_docs(problems: list[Problem]) -> list[str]:
    """Every series needs a registered, current interactive page.

    `make docs` fails loudly on a missing registry entry, but only when it is
    run — a series merged without it ships no page, and a CSV refreshed
    without it leaves a stale one. The pages are deterministic functions of
    the CSVs and the registry, so staleness is a byte comparison, the same
    claim `--reproduce` makes for the PNGs. The folder list comes from the
    same discovery as every other check (not `git ls-files`, which the
    pinned figure container cannot run).
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_docs", ROOT / "tools" / "build_docs.py")
    build_docs = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(build_docs)
    except Exception as error:  # a broken registry is itself the finding
        return [f"tools/build_docs.py cannot be loaded: {error}"]

    folders = sorted(problem.slug for problem in problems if problem.csvs)
    out = []
    for slug in folders:
        if slug not in build_docs.SERIES:
            out.append(f"tools/build_docs.py SERIES has no entry for {slug}")
            continue
        page = ROOT / "docs" / f"{slug}.html"
        if not page.exists():
            out.append(f"docs/{slug}.html is missing; run `make docs`")
            continue
        try:
            rendered = build_docs.render_page(slug, build_docs.SERIES[slug](slug))
        except Exception as error:
            out.append(f"docs builder for {slug} fails: {error}")
            continue
        if page.read_text(encoding="utf-8") != rendered:
            out.append(f"docs/{slug}.html is stale; run `make docs`")
    return out


def rewrite(text: str, begin: str, end: str, body: str) -> str | None:
    if begin not in text or end not in text:
        return None
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{begin}\n{body}\n{end}{tail}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true",
                        help="redraw every figure and compare it with the "
                             "committed one (slow, no network)")
    parser.add_argument("--write-index", action="store_true",
                        help="rewrite README's series and status tables; implies "
                             "--reproduce, so the status table never reports a "
                             "column it did not run")
    parser.add_argument("--links", action="store_true",
                        help="fetch every URL in every document (needs network)")
    args = parser.parse_args()

    # Ignore directories containing only nested build artifacts.  They can keep
    # an otherwise deleted folder alive in a long-used checkout (notably via a
    # stale __pycache__/), but a folder with any real top-level file must still
    # be checked so that an accidentally deleted README is reported.
    folders = sorted(
        path
        for path in PROBLEMS.iterdir()
        if path.is_dir() and any(child.is_file() for child in path.iterdir())
    )
    problems = [Problem(folder) for folder in folders]
    slugs = {problem.slug for problem in problems}
    keys = bib_keys()

    for problem in problems:
        problem.check(keys, slugs)
    check_chart_as_of(problems)
    duplicate_names(problems)
    if args.reproduce or args.write_index:
        # Import lazily: the ordinary document/data check does not need
        # matplotlib. This also turns a direct host invocation into one clear
        # instruction instead of 31 near-identical figure.py failures.
        sys.path.insert(0, str(ROOT))
        from lib.renderer import assert_canonical_renderer

        try:
            assert_canonical_renderer()
        except RuntimeError as error:
            print(f"ERROR {error}")
            return 2
        reproduce(problems)

    failures = [message for problem in problems for message in problem.messages()]
    failures += unused_bib(problems, keys)
    failures += strays()
    if not args.write_index:
        # Pointless when the tables are about to be rewritten anyway.
        failures += stale_readme(problems)
    failures += stale_docs(problems)
    if args.links:
        failures += dead_links(problems)
    if not problems:
        failures.append("problems/ has no folders")

    if args.write_index:
        text = README.read_text(encoding="utf-8") if README.exists() else ""
        for begin, end, body, what in (
                (INDEX_BEGIN, INDEX_END, index_rows(problems), "series index"),
                (CHECKS_BEGIN, CHECKS_END, checks_rows(problems), "status table")):
            written = rewrite(text, begin, end, body)
            if written is None:
                failures.append(f"README.md has no {what} markers")
            else:
                text = written
        README.write_text(text, encoding="utf-8")
        print("rewrote the series index and the status table in README.md")

    figures = sum(len(p.figures) for p in problems)
    csvs = sum(len(p.csvs) for p in problems)
    fetchers = sum((p.folder / "fetch.py").exists() for p in problems)
    print(f"{len(problems)} problem folders, {figures} figures, {csvs} data files, "
          f"{fetchers} with a fetcher, {len(keys)} bibliography entries")
    for failure in failures:
        print(f"  FAIL {failure}")
    print("ok" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
