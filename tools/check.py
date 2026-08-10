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
import re
import subprocess
import sys
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
# The index groups by domain, so the order is fixed here rather than left to
# whatever sorting a new value happens to fall under. The fourth group holds the
# series tracked to span verification cost, which is the argument's own
# explanatory variable and which the three worked domains barely vary.
DOMAIN_ORDER = ("vulnerabilities", "mathematics", "algorithms",
                "outside the three domains")

CHECKS = ("Document", "Data", "Figure", "Literature", "Refetch", "Reproduces")
PASS, FAIL, HAND, SKIP = "✅", "❌", "✍️", "➖"

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

INDEX_BEGIN = "<!-- BEGIN GENERATED: series-index -->"
INDEX_END = "<!-- END GENERATED: series-index -->"
CHECKS_BEGIN = "<!-- BEGIN GENERATED: checks-table -->"
CHECKS_END = "<!-- END GENERATED: checks-table -->"

# Wide enough that the shape of a series is readable in the index, narrow enough
# that four columns of prose still fit beside it.
THUMB_WIDTH = 240


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
        self.citations = set(re.findall(r"\[@([A-Za-z0-9_:-]+)\]", self.text))
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
        for name in sorted(self.linked_csvs):
            if not (self.folder / name).exists():
                self.fail("Data", f"links {name}, which is not in the folder")

        for key in sorted(self.citations - keys):
            self.fail("Literature", f"citation @{key} has no bibliography entry")

        if (self.folder / "fetch.py").exists():
            self.status["Refetch"] = PASS
        else:
            built = re.search(r"## How the chart was built\n(.*?)(?=\n## |\Z)",
                              self.text, re.S)
            if built and NO_FETCHER_REASONS.search(built.group(1)):
                self.status["Refetch"] = HAND
            else:
                self.fail("Refetch", "has no fetch.py, and 'How the chart was "
                                     "built' does not say how the data is "
                                     "maintained instead")

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


def in_reading_order(problems: list[Problem]) -> list[Problem]:
    """Domain order, then slug — the order both generated tables use."""
    rank = {domain: i for i, domain in enumerate(DOMAIN_ORDER)}
    return sorted(problems, key=lambda p: (rank.get(p.domain, len(rank)), p.slug))


def thumbnails(problem: Problem) -> str:
    """The folder's figures as links into it, sized to sit in a table cell.

    Written as HTML because markdown image syntax has no width, and a chart at
    its natural 1600 pixels makes the index unreadable. A folder with several
    figures stacks them, since a table cell is as wide as its contents and three
    thumbnails in a row would push the prose columns off the screen.
    """
    return "<br>".join(
        f'<a href="problems/{problem.slug}/">'
        f'<img src="problems/{problem.slug}/{figure.name}" width="{THUMB_WIDTH}" '
        f'alt="{problem.title}"></a>'
        for figure in problem.figures)


def index_rows(problems: list[Problem]) -> str:
    out: list[str] = []
    for domain in DOMAIN_ORDER + tuple(sorted(
            {p.domain for p in problems} - set(DOMAIN_ORDER))):
        rows = [p for p in in_reading_order(problems) if p.domain == domain]
        if not rows:
            continue
        out += [f"### {domain[:1].upper()}{domain[1:]}", "",
                "| Chart | Series | Metric | Coverage | Acceleration? |",
                "|---|---|---|---|---|"]
        out += [f"| {thumbnails(problem)} | "
                f"[{problem.title}](problems/{problem.slug}/) | "
                f"{problem.fields.get('Metric', '')} | "
                f"{problem.fields.get('Coverage', '')} | "
                f"{problem.fields.get('Verdict', '')} |"
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
    red = sum(p.status[group] == FAIL for p in problems for group in CHECKS)
    out += ["", f"{len(problems)} problems holding {sum(len(p.figures) for p in problems)} "
                f"figures and {sum(len(p.csvs) for p in problems)} data files. "
                f"{fetched} refetch from upstream and {hand} are maintained by hand "
                f"and say so. {red or 'No'} failing "
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true",
                        help="redraw every figure and compare it with the "
                             "committed one (slow, no network)")
    parser.add_argument("--write-index", action="store_true",
                        help="rewrite README's series and status tables; implies "
                             "--reproduce, so the status table never reports a "
                             "column it did not run")
    args = parser.parse_args()

    folders = sorted(p for p in PROBLEMS.iterdir() if p.is_dir())
    problems = [Problem(folder) for folder in folders]
    slugs = {problem.slug for problem in problems}
    keys = bib_keys()

    for problem in problems:
        problem.check(keys, slugs)
    duplicate_names(problems)
    if args.reproduce or args.write_index:
        reproduce(problems)

    failures = [message for problem in problems for message in problem.messages()]
    failures += strays()
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
