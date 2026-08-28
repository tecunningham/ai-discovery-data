#!/usr/bin/env python3
"""Consistency checks over problems/, lib/ and references.bib.

    python3 tools/check.py                 # report, exit non-zero on failure
    python3 tools/check.py --reproduce     # also redraw every figure and compare
    python3 tools/check.py --write-index   # rewrite README's two generated
                                           # tables and CUMULATIVE.md's index

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
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.dates import AS_OF_DATE  # noqa: E402  (matplotlib-free)
from lib.document import front_matter, title  # noqa: E402
from tools.tables import (  # noqa: E402
    CHECKS,
    CHECKS_BEGIN,
    CHECKS_END,
    CUMULATIVE_BEGIN,
    CUMULATIVE_END,
    FAIL,
    HAND,
    INDEX_BEGIN,
    INDEX_END,
    PASS,
    SKIP,
    checks_rows,
    cumulative_thumbnail,
    index_rows,
    rewrite,
)

PROBLEMS = ROOT / "problems"
BIB = ROOT / "references.bib"
README = ROOT / "README.md"

FIELDS = ("Domain", "Role", "Metric", "Coverage", "Data", "Upstream",
          "Verdict")
SECTIONS = ("Definition", "Facts", "Method", "Limitations", "AI attribution",
            "Sources")
# The one place a page states why it is in the collection, as a controlled
# phrase rather than a paragraph; FORMAT.md defines the vocabulary.
ROLES = {"discovery series", "prestige ledger", "control: no-AI baseline",
         "contrast case: volume", "denominator frame"}
VERDICTS = {"accelerating", "no acceleration", "declining", "inconclusive",
            "too early", "baseline"}


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

# The pages are reference material (see FORMAT.md): facts a reader can check,
# not readings. These are the rhetorical devices the 2026-08 style audit found
# doing interpretive work; each match is a Document failure. Blockquote lines
# are exempt, since quoted sources may use any words they like.
STYLE_LINT = (
    r"\bworth (stating|naming|noting|recording|carrying|knowing|having"
    r"|being explicit)\b",
    r"\bthe story of\b",
    r"\bis the (reading|finding|whole point)\b",
    r"\bthat is the reading\b",
    r"\bcuts? the (reading|finding) down\b",
    r"\bfamously\b",
    r"\bremarkabl",
    r"\binterestingly\b",
    r"\bthe interesting (number|one|part|region)\b",
    r"\bhonest (summary|alternative|layer)\b",
    r"\bearns (a|its own) (place|document)\b",
    r"\b(best|worst|weakest|cleanest|sharpest|most useful) "
    r"(available )?(instrument|aggregate|baseline|control|warning)\b",
)

# A quote a reader cannot locate is not checkable. Every blockquote block must
# end with an attribution line naming its source and carrying a year.
QUOTE_ATTRIBUTION = re.compile(r"^>\s*[—–-]\s+.*\b(19|20)\d{2}\b")

CUMULATIVE = ROOT / "CUMULATIVE.md"

# Every plottable series also appears on CUMULATIVE.md in one shared step
# format, drawn by the same figure.py as cumulative-<slug>.png. A folder whose
# series has no time axis states that instead, in the same way a chartless
# folder states why there is no figure.
NO_CUMULATIVE_REASONS = re.compile(r"no cumulative view", re.I)


class Problem:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.slug = folder.name
        self.doc = folder / "README.md"
        self.text = self.doc.read_text(encoding="utf-8") if self.doc.exists() else ""
        self.title = title(self.text)
        # Folder-local links only: an embed or a data link reaching outside the
        # folder means the split is incomplete. Embeds keep document order, so
        # the index can take "the first figure the page shows" as its primary.
        self.embed_order = re.findall(r"!\[[^\]]*\]\(([^)/]+\.png)\)", self.text)
        self.embedded = set(self.embed_order)
        self.linked_csvs = set(re.findall(r"\(([^)/]+\.csv)\)", self.text))
        self.siblings = set(re.findall(r"\(\.\./([a-z0-9-]+)/README\.md\)", self.text))
        # A bracket can hold several keys, `[@a; @b]`. Matching `@key]` would see
        # only the last of them and leave a typo in any earlier key unchecked.
        self.citations = {key
                          for group in re.findall(r"\[@[^\]]*\]", self.text)
                          for key in re.findall(r"@([A-Za-z0-9_:-]+)", group)}
        self.fields = {field: value
                       for field, value in front_matter(self.text).items()
                       if field in FIELDS and value}
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
        # FORMAT.md: Coverage carries the span, the cadence, and the as-of
        # date of the last read. Presence of the field is not enough — a
        # coverage line with no date leaves the reader no way to tell a
        # current series from an abandoned one.
        coverage = self.fields.get("Coverage", "")
        if coverage and not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", coverage):
            self.fail("Document",
                      "**Coverage:** carries no as-of date (FORMAT.md: the "
                      "span, the cadence, and the date of the last read)")
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

        # Style register (FORMAT.md): quoted sources are exempt, the page's
        # own prose is not.
        own_prose = "\n".join(line for line in self.text.splitlines()
                              if not line.startswith(">"))
        for pattern in STYLE_LINT:
            match = re.search(pattern, own_prose, re.I)
            if match:
                self.fail("Document",
                          f"style lint: {match.group(0)!r} (see FORMAT.md)")
        lines = self.text.splitlines()
        for index, line in enumerate(lines):
            block_end = (line.startswith(">")
                         and (index + 1 == len(lines)
                              or not lines[index + 1].startswith(">")))
            if block_end and not QUOTE_ATTRIBUTION.match(line):
                self.fail("Document",
                          f"quote block ending {line[:48]!r} has no dated "
                          "attribution line (see FORMAT.md)")

        role = self.fields.get("Role", "")
        if role and role not in ROLES:
            self.fail("Document", f"role {role!r} not one of {sorted(ROLES)}")

        figure_script = self.folder / "figure.py"
        built = re.search(r"## Method\n(.*?)(?=\n## |\Z)",
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
                # The two prefixed names are reserved: the index takes
                # discovery-<slug>.png as the folder's primary figure and
                # CUMULATIVE.md takes cumulative-<slug>.png, so a near-miss
                # name silently drops the figure from those pages.
                for prefix in ("discovery-", "cumulative-"):
                    expected = f"{prefix}{self.slug}.png"
                    if figure.name.startswith(prefix) and figure.name != expected:
                        self.fail("Figure",
                                  f"{figure.name} does not match {expected}; the "
                                  f"{prefix}*.png name is reserved for the folder's "
                                  "own view (FORMAT.md)")
            for name in sorted(self.embedded):
                if not (self.folder / name).exists():
                    self.fail("Figure", f"embeds {name}, which is not in the folder")
            if (f"cumulative-{self.slug}.png" not in script_text
                    and not NO_CUMULATIVE_REASONS.search(self.text)):
                self.fail("Figure",
                          f"figure.py draws no cumulative-{self.slug}.png for "
                          "CUMULATIVE.md, and the document does not say why not")

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
            self.fail("Refetch", "has no fetch.py, and 'Method' does not say "
                                 "how the data is maintained instead")

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
    as_of = AS_OF_DATE
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
                f"lib/dates.py AS_OF_DATE {as_of.isoformat()}",
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


# The root documents also cite the bibliography, so their citekeys join both
# directions of the bibliography check. FORMAT.md is excluded: its [@citekey]
# is a literal example, not a citation.
ROOT_DOCS = ("README.md", "CUMULATIVE.md", "ADDITIONAL-CANDIDATES.md")


def root_citations() -> dict[str, str]:
    """Citekey to the root document that cites it."""
    cited: dict[str, str] = {}
    for name in ROOT_DOCS:
        text = (ROOT / name).read_text(encoding="utf-8")
        # A `[@citekey]` inside backticks is the syntax being described, not a
        # citation (README's check-table legend carries one).
        text = re.sub(r"`[^`]*`", "", text)
        for group in re.findall(r"\[@[^\]]*\]", text):
            for key in re.findall(r"@([A-Za-z0-9_:-]+)", group):
                cited.setdefault(key, name)
    return cited


def unused_bib(problems: list[Problem], keys: set[str]) -> list[str]:
    """A bibliography entry no document cites, or a root citation no entry backs.

    The reverse of the per-problem citation check, and it catches the residue of
    a rewrite: prose gets reworded, the citation goes with it, and the entry sits
    in references.bib looking like part of the apparatus. Root documents were
    once invisible here, so a key cited only by README.md read as unused, and a
    root citation with no entry was checked by nothing.
    """
    rooted = root_citations()
    cited = {key for problem in problems for key in problem.citations}
    out = [f"references.bib: @{key} is cited by no document"
           for key in sorted(keys - cited - set(rooted))]
    out += [f"{name}: citation @{key} has no bibliography entry"
            for key, name in sorted(rooted.items()) if key not in keys]
    return out


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


def stale_cumulative(problems: list[Problem]) -> list[str]:
    """CUMULATIVE.md's generated table must match the folders, like README's.

    Same claim, same mechanism: the page is a deterministic function of the
    problem folders, so a series merged or refetched without `make index`
    leaves it silently short or stale, and a byte comparison is the check.
    """
    text = CUMULATIVE.read_text(encoding="utf-8") if CUMULATIVE.exists() else ""
    if CUMULATIVE_BEGIN not in text or CUMULATIVE_END not in text:
        return ["CUMULATIVE.md has no cumulative-index markers"]
    committed = text.split(CUMULATIVE_BEGIN, 1)[1].split(CUMULATIVE_END, 1)[0].strip()
    if committed != index_rows(problems, cumulative_thumbnail).strip():
        return ["CUMULATIVE.md cumulative index does not match the problem "
                "folders; run `make index`"]
    return []


def stale_docs(problems: list[Problem]) -> list[str]:
    """Every series needs a declared, current interactive page.

    `make docs` fails loudly on a folder with no chart_spec.py, but only when
    it is run — a series merged without one ships no page, and a CSV
    refreshed without a rebuild leaves a stale one. The pages are
    deterministic functions of the CSVs, the READMEs and the folder specs, so
    staleness is a byte comparison, the same claim `--reproduce` makes for
    the PNGs.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_docs", ROOT / "tools" / "build_docs.py")
    build_docs = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(build_docs)
    except Exception as error:
        return [f"tools/build_docs.py cannot be loaded: {error}"]

    folders = sorted(problem.slug for problem in problems if problem.csvs)
    out = []
    for slug in folders:
        if not (PROBLEMS / slug / "chart_spec.py").exists():
            out.append(f"problems/{slug}/chart_spec.py is missing; declare "
                       "the page's charts there, using lib/vega.py's shapes")
            continue
        page = ROOT / "docs" / f"{slug}.html"
        if not page.exists():
            out.append(f"docs/{slug}.html is missing; run `make docs`")
            continue
        try:
            rendered = build_docs.render_page(slug, build_docs.charts_for(slug))
        except Exception as error:
            out.append(f"docs builder for {slug} fails: {error}")
            continue
        if page.read_text(encoding="utf-8") != rendered:
            out.append(f"docs/{slug}.html is stale; run `make docs`")
    # The root pages are deterministic functions of the root documents, so
    # they get the same byte comparison: an edited README with an unbuilt
    # index page is the docs equivalent of a stale generated table.
    for page_name, source in build_docs.ROOT_PAGES.items():
        page = ROOT / "docs" / page_name
        if not page.exists():
            out.append(f"docs/{page_name} is missing; run `make docs`")
            continue
        try:
            rendered = build_docs.render_root(source)
        except Exception as error:
            out.append(f"docs builder for {source} fails: {error}")
            continue
        if page.read_text(encoding="utf-8") != rendered:
            out.append(f"docs/{page_name} is stale; run `make docs`")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true",
                        help="redraw every figure and compare it with the "
                             "committed one (slow, no network)")
    parser.add_argument("--write-index", action="store_true",
                        help="rewrite README's series and status tables and "
                             "CUMULATIVE.md's index; implies --reproduce, so "
                             "the status table never reports a column it did "
                             "not run")
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
        # Checked up front so a direct host invocation gets one clear
        # instruction instead of 37 near-identical figure.py failures.
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
        failures += stale_cumulative(problems)
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
        cumulative_text = (CUMULATIVE.read_text(encoding="utf-8")
                           if CUMULATIVE.exists() else "")
        written = rewrite(cumulative_text, CUMULATIVE_BEGIN, CUMULATIVE_END,
                          index_rows(problems, cumulative_thumbnail))
        if written is None:
            failures.append("CUMULATIVE.md has no cumulative-index markers")
        else:
            CUMULATIVE.write_text(written, encoding="utf-8")
        print("rewrote the series index and the status table in README.md, "
              "and the cumulative index in CUMULATIVE.md")

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
