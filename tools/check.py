#!/usr/bin/env python3
"""Consistency checks over data/, figures/, problems/ and references.bib.

    python3 tools/check.py                 # report, exit non-zero on failure
    python3 tools/check.py --write-index   # also rewrite README's series table

What this is for. The repository's claim is that every chart can be traced to a
public source, so the failure mode that matters is a series arriving without the
apparatus that makes it checkable: a figure nobody documents, a CSV nobody
plots or explains, a citation with no bibliography entry. None of those are
visible by reading any single file, so they are checked mechanically here.

Metadata is parsed out of the prose rather than hidden in front matter, because
a reader of the document should see the same source and coverage the checker
does.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
PROBLEMS = ROOT / "problems"
BIB = ROOT / "references.bib"
README = ROOT / "README.md"

FIELDS = ("Domain", "Metric", "Coverage", "Data", "Upstream", "Verdict")
SECTIONS = ("The problem", "What the chart shows", "How the chart was built",
            "What it cannot support", "LLM contributions", "Related literature")
VERDICTS = {"accelerating", "no acceleration", "declining", "inconclusive", "baseline"}

# Support files: vendored and documented, but not plotted on their own. Each is
# named by the document that uses it, so the exemption is not a silent hole.
SUPPORTING = {
    "discovery-finders.csv",
    "curl-vulnerabilities-quarterly.csv",
    "nvd-kev-by-quarter.csv",
    "antedb-bounds.csv",
    "alphaevolve-inventory.csv",
}

INDEX_BEGIN = "<!-- BEGIN GENERATED: series-index -->"
INDEX_END = "<!-- END GENERATED: series-index -->"


class Doc:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", self.text, re.M)
        self.title = title.group(1).strip() if title else ""
        self.figures = re.findall(r"!\[[^\]]*\]\(\.\./figures/([^)]+)\)", self.text)
        self.csvs = re.findall(r"\.\./data/([A-Za-z0-9_.-]+\.csv)", self.text)
        self.citations = set(re.findall(r"\[@([A-Za-z0-9_:-]+)\]", self.text))
        self.fields = {}
        for field in FIELDS:
            match = re.search(rf"^\*\*{field}:\*\*\s*(.+)$", self.text, re.M)
            if match:
                self.fields[field] = match.group(1).strip()

    @property
    def slug(self) -> str:
        return self.path.stem


def bib_keys() -> set[str]:
    if not BIB.exists():
        return set()
    return set(re.findall(r"^@[a-zA-Z]+\{([^,\s]+)", BIB.read_text(encoding="utf-8"), re.M))


def strip_links(value: str) -> str:
    return re.sub(r"[`\[\]()<>]|\.\./data/", "", value).strip()


def index_rows(docs: list[Doc]) -> str:
    by_domain: dict[str, list[Doc]] = {}
    for doc in docs:
        by_domain.setdefault(doc.fields.get("Domain", "?"), []).append(doc)
    lines = ["| Series | Domain | Metric | Coverage | Acceleration? |",
             "|---|---|---|---|---|"]
    for domain in ("vulnerabilities", "mathematics", "algorithms"):
        for doc in sorted(by_domain.get(domain, []), key=lambda d: d.slug):
            lines.append(
                f"| [{doc.title}](problems/{doc.path.name}) | {domain} | "
                f"{doc.fields.get('Metric', '')} | {doc.fields.get('Coverage', '')} | "
                f"{doc.fields.get('Verdict', '')} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()

    docs = [Doc(p) for p in sorted(PROBLEMS.glob("*.md")) if p.name != "README.md"]
    keys = bib_keys()
    failures: list[str] = []

    if not docs:
        failures.append("problems/ has no documents")

    documented_figures: dict[str, str] = {}
    documented_csvs: set[str] = set()
    for doc in docs:
        for field in FIELDS:
            if field not in doc.fields:
                failures.append(f"{doc.slug}: no **{field}:** line")
        verdict = doc.fields.get("Verdict", "").split(" —")[0].strip()
        if verdict and verdict not in VERDICTS:
            failures.append(f"{doc.slug}: verdict {verdict!r} not one of {sorted(VERDICTS)}")
        for section in SECTIONS:
            if f"## {section}" not in doc.text:
                failures.append(f"{doc.slug}: no '## {section}' section")
        if not doc.figures:
            failures.append(f"{doc.slug}: embeds no figure from ../figures/")
        for figure in doc.figures:
            if not (FIGURES / figure).exists():
                failures.append(f"{doc.slug}: figure {figure} missing on disk")
            if figure in documented_figures:
                failures.append(f"{doc.slug}: figure {figure} already documented by "
                                f"{documented_figures[figure]}")
            documented_figures[figure] = doc.slug
        if not doc.csvs:
            failures.append(f"{doc.slug}: links no CSV under ../data/")
        for csv_name in doc.csvs:
            if not (DATA / csv_name).exists():
                failures.append(f"{doc.slug}: data file {csv_name} missing on disk")
            documented_csvs.add(csv_name)
        if "http" not in doc.fields.get("Upstream", ""):
            failures.append(f"{doc.slug}: **Upstream:** names no URL")
        for key in sorted(doc.citations - keys):
            failures.append(f"{doc.slug}: citation @{key} has no bibliography entry")

    for figure in sorted(p.name for p in FIGURES.glob("*.png")):
        if figure not in documented_figures:
            failures.append(f"figure {figure} is generated but no document explains it")

    for csv_path in sorted(DATA.glob("*.csv")):
        if csv_path.name not in documented_csvs and csv_path.name not in SUPPORTING:
            failures.append(f"data/{csv_path.name} is vendored but no document uses it")

    if args.write_index and README.exists():
        text = README.read_text(encoding="utf-8")
        if INDEX_BEGIN in text and INDEX_END in text:
            head, rest = text.split(INDEX_BEGIN, 1)
            _, tail = rest.split(INDEX_END, 1)
            README.write_text(
                f"{head}{INDEX_BEGIN}\n{index_rows(docs)}\n{INDEX_END}{tail}",
                encoding="utf-8")
            print("rewrote the series index in README.md")
        else:
            failures.append("README.md has no series-index markers")

    print(f"{len(docs)} documents, {len(documented_figures)} figures, "
          f"{len(documented_csvs)} data files, {len(keys)} bibliography entries")
    for failure in failures:
        print(f"  FAIL {failure}")
    print("ok" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
