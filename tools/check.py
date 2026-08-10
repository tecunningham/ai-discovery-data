#!/usr/bin/env python3
"""Consistency checks over problems/, lib/ and references.bib.

    python3 tools/check.py                 # report, exit non-zero on failure
    python3 tools/check.py --write-index   # also rewrite README's series table

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
"""

from __future__ import annotations

import argparse
import re
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

    @property
    def figures(self) -> list[Path]:
        return sorted(self.folder.glob("*.png"))

    @property
    def csvs(self) -> list[Path]:
        return sorted(self.folder.glob("*.csv"))

    @property
    def domain(self) -> str:
        return self.fields.get("Domain", "?")

    def check(self, keys: set[str], slugs: set[str]) -> list[str]:
        out: list[str] = []
        say = lambda msg: out.append(f"{self.slug}: {msg}")  # noqa: E731

        if not self.doc.exists():
            return [f"{self.slug}: no README.md"]
        for field in FIELDS:
            if field not in self.fields:
                say(f"no **{field}:** line")
        verdict = self.fields.get("Verdict", "").split(" —")[0].strip()
        if verdict and verdict not in VERDICTS:
            say(f"verdict {verdict!r} not one of {sorted(VERDICTS)}")
        for section in SECTIONS:
            if f"## {section}" not in self.text:
                say(f"no '## {section}' section")
        if "http" not in self.fields.get("Upstream", ""):
            say("**Upstream:** names no URL")

        figure_script = self.folder / "figure.py"
        if not figure_script.exists():
            say("no figure.py")
        if not self.figures:
            say("no figure on disk")
        script_text = figure_script.read_text(encoding="utf-8") if figure_script.exists() else ""
        for figure in self.figures:
            if figure.name not in self.embedded:
                say(f"{figure.name} is generated but the document does not embed it")
            if figure.name not in script_text:
                say(f"{figure.name} is not named in figure.py, so nothing rebuilds it")
        for name in sorted(self.embedded):
            if not (self.folder / name).exists():
                say(f"embeds {name}, which is not in the folder")

        if not self.csvs:
            say("holds no CSV")
        for csv_path in self.csvs:
            if csv_path.name not in self.linked_csvs:
                say(f"{csv_path.name} is vendored but the document does not link it")
        for name in sorted(self.linked_csvs):
            if not (self.folder / name).exists():
                say(f"links {name}, which is not in the folder")

        if not (self.folder / "fetch.py").exists():
            built = re.search(r"## How the chart was built\n(.*?)(?=\n## |\Z)",
                              self.text, re.S)
            if not (built and NO_FETCHER_REASONS.search(built.group(1))):
                say("has no fetch.py, and 'How the chart was built' does not say how "
                    "the data is maintained instead")

        for sibling in sorted(self.siblings - slugs):
            say(f"links ../{sibling}/README.md, which does not exist")
        for key in sorted(self.citations - keys):
            say(f"citation @{key} has no bibliography entry")
        return out


def bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(re.findall(r"^@[a-zA-Z]+\{([^,\s]+)", BIB.read_text(encoding="utf-8"), re.M))


def index_rows(problems: list[Problem]) -> str:
    domains = list(DOMAIN_ORDER) + sorted(
        {p.domain for p in problems} - set(DOMAIN_ORDER)
    )
    lines = ["| Series | Domain | Metric | Coverage | Acceleration? |",
             "|---|---|---|---|---|"]
    for domain in domains:
        for problem in sorted((p for p in problems if p.domain == domain),
                              key=lambda p: p.slug):
            lines.append(
                f"| [{problem.title}](problems/{problem.slug}/) | {domain} | "
                f"{problem.fields.get('Metric', '')} | "
                f"{problem.fields.get('Coverage', '')} | "
                f"{problem.fields.get('Verdict', '')} |")
    return "\n".join(lines)


def duplicate_names(problems: list[Problem]) -> list[str]:
    """Filenames must be unique across folders, not just within one.

    The blog repository reads these CSVs by name through its own resolver, since
    it has no reason to know which folder a series ended up in. Two folders both
    holding a `finders.csv` would make that lookup ambiguous, so the names carry
    the series: `curl-finders.csv`, not `finders.csv`.
    """
    seen: dict[str, str] = {}
    out = []
    for problem in problems:
        for path in problem.csvs + problem.figures:
            if path.name in seen:
                out.append(f"{problem.slug}/{path.name} collides with "
                           f"{seen[path.name]}/{path.name}; names must be unique "
                           "across folders")
            seen[path.name] = problem.slug
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()

    folders = sorted(p for p in PROBLEMS.iterdir() if p.is_dir())
    problems = [Problem(folder) for folder in folders]
    slugs = {problem.slug for problem in problems}
    keys = bib_keys()

    failures: list[str] = []
    if not problems:
        failures.append("problems/ has no folders")
    for problem in problems:
        failures.extend(problem.check(keys, slugs))
    failures.extend(duplicate_names(problems))
    failures.extend(strays())

    if args.write_index and README.exists():
        text = README.read_text(encoding="utf-8")
        if INDEX_BEGIN in text and INDEX_END in text:
            head, rest = text.split(INDEX_BEGIN, 1)
            _, tail = rest.split(INDEX_END, 1)
            README.write_text(
                f"{head}{INDEX_BEGIN}\n{index_rows(problems)}\n{INDEX_END}{tail}",
                encoding="utf-8")
            print("rewrote the series index in README.md")
        else:
            failures.append("README.md has no series-index markers")

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
