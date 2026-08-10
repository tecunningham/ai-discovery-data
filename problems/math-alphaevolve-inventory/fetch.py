#!/usr/bin/env python3
"""Build an inventory of the AlphaEvolve mathematics problems, with dated citations.

Run: python3 problems/math-alphaevolve-inventory/fetch.py --paper-text ae.txt --repo path/to/repo

Writes this folder's alphaevolve-inventory.csv.

Why this exists. The AlphaEvolve mathematics paper reports improved bounds on a
share of 67 problems, and the discussion of that result has no historical
baseline: nobody has assembled the dated record of prior improvements on those
same problems, so the AI-era step cannot be compared with the distribution of
historical steps. The paper's authors say so themselves — "we do not attempt to
exhaustively survey the history of each of the problems listed here." This is
phase one of building that baseline: an inventory saying, per problem, what the
quantity is, what the incumbent bound was, which prior work is cited, and what
year each cited work dates from.

What it extracts, and what it does not. Per problem the paper states the
quantity, usually gives the prior best bounds inline, and names one to three
prior contributors with bracketed reference numbers. Joining those numbers to
the bibliography yields a *partial* dated history — typically the last one to
three record steps, not the full sequence. Completing a sequence needs
citation-chain walking through the primary literature, which is manual. So the
output here is the frame for that work plus whatever history the paper already
carries, and the `cited_years` column should never be read as a complete record.

Inputs, neither vendored:

  --paper-text  a pdftotext extraction of arXiv:2511.02864. Produce with:
                  curl -sL -o ae.pdf https://arxiv.org/pdf/2511.02864
                  pdftotext ae.pdf ae.txt
                The paper is not redistributed here; only derived counts and
                short quoted bound strings go into the CSV.
  --repo        a checkout of github.com/google-deepmind/alphaevolve_repository_of_problems,
                for status.json and the experiment directory names.

Known limits, recorded rather than papered over:

  * The paper numbers problems 6.1 to 6.65, while status.json indexes 1 to 67.
    The two enumerations therefore cannot be identical. The repository's README
    identifies its Problem 2 as the Sidon autocorrelation problem, which is the
    paper's Problem 6.2, so the mapping agrees at least there; it is assumed to
    be the identity and every row carries `status_mapping` = "assumed" to say
    so. Rows above 65 have no paper counterpart.
  * Bound strings are extracted by pattern and are lightly normalised LaTeX, so
    they are for orientation and must be re-read against the paper before use.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402

OUT = HERE / "alphaevolve-inventory.csv"

# "Problem 6.12 (Some title)." — the definition, as against a cross-reference.
PROBLEM_RE = re.compile(r"Problem\s+6\.(\d{1,2})\s*(?:\(([^)]{2,80})\))?")
# Section 6 is where the problems are actually defined. Everything before it
# (intro, meta-analysis) only cross-references them, and treating a
# cross-reference as a definition silently merges two problems' spans.
SECTION6_RE = re.compile(r"^\d?\s*6\.\s*M\s*ATHEMATICAL\s+PROBLEMS", re.M | re.I)
# A definition continues "(Title)." or "Let"/"Define"/"Consider"/"For".
DEFINITION_TAIL_RE = re.compile(r"^\s*(?:\([^)]{2,80}\))?\s*\.?\s*(?:Let|Define|Consider|For|Denote|Given|We|Fix|Suppose|What)")
# Topic groups: "19. Packing problems." Some headings carry trailing prose, so
# the title is taken up to the first full stop rather than to end of line.
GROUP_RE = re.compile(r"^(\d{1,2})\.\s+([A-Z][^\n.]{4,70})\.", re.M)
BIB_ENTRY_RE = re.compile(r"^\[(\d{1,3})\]\s+(.{0,400}?)(?=^\[\d{1,3}\]|\Z)", re.M | re.S)
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20[0-2]\d)\b")
# Citation brackets, which frequently carry a locator: "[129, 128]" but also
# "[244, Theorem 4.1]" and "[205, Conjecture 1.2]". Requiring the whole bracket
# to be digits and commas silently dropped every cited work with a locator, so
# the bracket is captured whole and its comma-separated parts filtered below.
CITE_RE = re.compile(r"\[([^\]\n]{1,80})\]")
# Inequality chains such as "1.28 \leq C_{6.2} \leq 1.50992", after pdftotext
# has turned the maths into unicode.
BOUND_RE = re.compile(r"[0-9][0-9.,]*\s*[≤≥<>=]\s*𝐶[^\n]{0,40}?[≤≥<>=]\s*[0-9][0-9.]*")
SIMPLE_BOUND_RE = re.compile(r"𝐶[6.\d]{0,8}\s*[≤≥=]\s*[0-9][0-9.]*")


def parse_bibliography(text: str) -> dict[int, dict]:
    """{reference number: {authors, year, raw}} from the paper's reference list."""
    start = text.find("R EFERENCES")
    if start < 0:
        start = text.find("REFERENCES")
    if start < 0:
        return {}
    tail = text[start:]
    out: dict[int, dict] = {}
    for match in BIB_ENTRY_RE.finditer(tail):
        number = int(match.group(1))
        raw = re.sub(r"\s+", " ", match.group(2)).strip()
        years = [int(y) for y in YEAR_RE.findall(raw)]
        # A reference may carry both a journal year and an arXiv year; the
        # earliest is the better estimate of when the result became public.
        out[number] = {
            "authors": raw.split(".")[0][:90],
            "year": min(years) if years else None,
            "raw": raw[:200],
        }
    return out


def _body(text: str) -> tuple[str, int]:
    """The problem section, and its offset in the full text."""
    end = text.find("R EFERENCES")
    if end < 0:
        end = len(text)
    match = SECTION6_RE.search(text[:end])
    start = match.start() if match else 0
    return text[start:end], start


def problem_spans(text: str) -> dict[int, tuple[int, int, str]]:
    """{problem number: (start, end, title)} within the problem section.

    A problem's definition is its first occurrence inside section 6 that reads
    like a definition — a parenthetical title, or a following "Let"/"Define"/
    "Consider". Occurrences elsewhere are cross-references; treating one as a
    definition makes the preceding problem's span swallow this one's content,
    which is what an earlier version of this script did.
    """
    body, offset = _body(text)
    chosen: dict[int, tuple[int, str, bool]] = {}
    for match in PROBLEM_RE.finditer(body):
        number = int(match.group(1))
        title = (match.group(2) or "").strip()
        tail = body[match.end(): match.end() + 60]
        looks_defined = bool(title) or bool(DEFINITION_TAIL_RE.match(tail))
        if number not in chosen:
            chosen[number] = (match.start(), title, looks_defined)
        elif looks_defined and not chosen[number][2]:
            chosen[number] = (match.start(), title, looks_defined)
    ordered = sorted((pos, number, title)
                     for number, (pos, title, _ok) in chosen.items())
    spans: dict[int, tuple[int, int, str]] = {}
    for index, (pos, number, title) in enumerate(ordered):
        end = ordered[index + 1][0] if index + 1 < len(ordered) else len(body)
        spans[number] = (pos + offset, end + offset, title)
    return spans


def topic_groups(text: str) -> list[tuple[int, str]]:
    """(character position, group name) for the paper's topic headings.

    Headings are numbered sequentially, so a candidate whose number does not
    continue the run is a false positive (a numbered list item, a display
    equation label) and is dropped.
    """
    body, offset = _body(text)
    out: list[tuple[int, str]] = []
    expected = 1
    for match in GROUP_RE.finditer(body):
        number = int(match.group(1))
        if number != expected:
            continue
        out.append((match.start() + offset, match.group(2).strip()))
        expected += 1
    return out


def group_for(position: int, groups: list[tuple[int, str]]) -> str:
    name = ""
    for start, label in groups:
        if start <= position:
            name = label
        else:
            break
    return name


def status_index(repo: Path) -> tuple[dict[int, str], set[str]]:
    path = repo / "status.json"
    statuses: dict[int, str] = {}
    if path.exists():
        for label, numbers in json.loads(path.read_text()).items():
            for number in numbers:
                statuses[int(number)] = label
    experiments = set()
    experiments_dir = repo / "experiments"
    if experiments_dir.is_dir():
        experiments = {p.name for p in experiments_dir.iterdir() if p.is_dir()}
    return statuses, experiments


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-text", required=True, help="pdftotext output of arXiv:2511.02864")
    parser.add_argument("--repo", required=True, help="checkout of alphaevolve_repository_of_problems")
    args = parser.parse_args()

    text = Path(args.paper_text).expanduser().read_text(encoding="utf-8", errors="replace")
    repo = Path(args.repo).expanduser()

    bibliography = parse_bibliography(text)
    spans = problem_spans(text)
    groups = topic_groups(text)
    statuses, experiments = status_index(repo)

    print(f"bibliography entries parsed: {len(bibliography)} "
          f"({sum(1 for b in bibliography.values() if b['year'])} with a year)")
    print(f"problems located in the paper: {len(spans)} "
          f"(6.{min(spans)}–6.{max(spans)})")
    print(f"status.json classifies: {len(statuses)} of 67")
    print(f"experiment directories: {len(experiments)}")

    rows = []
    for number in sorted(spans):
        start, end, title = spans[number]
        body = text[start:end]
        cited: list[int] = []
        for match in CITE_RE.finditer(body):
            for part in match.group(1).split(","):
                part = part.strip()
                # Keep bare reference numbers; drop locators ("Theorem 4.1"),
                # footnote markers and anything else non-numeric.
                if part.isdigit() and int(part) in bibliography:
                    cited.append(int(part))
        cited = sorted(set(cited))
        years = sorted({bibliography[c]["year"] for c in cited
                        if c in bibliography and bibliography[c]["year"]})
        bounds = BOUND_RE.findall(body) or SIMPLE_BOUND_RE.findall(body)
        rows.append({
            "problem": f"6.{number}",
            "index": number,
            "title": title,
            "topic_group": group_for(start, groups),
            "status": statuses.get(number, ""),
            "status_mapping": "assumed" if number in statuses else "",
            "n_citations": len(cited),
            "cited_refs": ";".join(str(c) for c in cited[:12]),
            "n_cited_years": len(years),
            "earliest_cited_year": years[0] if years else "",
            "latest_cited_year": years[-1] if years else "",
            "cited_years": ";".join(str(y) for y in years),
            "stated_bound": re.sub(r"\s+", " ", bounds[0])[:120] if bounds else "",
        })

    write_csv(OUT, rows)

    dated = [r for r in rows if r["n_cited_years"] >= 2]
    spans_yrs = [int(r["latest_cited_year"]) - int(r["earliest_cited_year"])
                 for r in dated if r["earliest_cited_year"]]
    print(f"  with a stated bound string:        {sum(1 for r in rows if r['stated_bound'])}")
    print(f"  with >=1 dated citation:           {sum(1 for r in rows if r['n_cited_years'] >= 1)}")
    print(f"  with >=2 dated citations:          {len(dated)}")
    print(f"  with >=4 dated citations:          {sum(1 for r in rows if r['n_cited_years'] >= 4)}")
    if spans_yrs:
        spans_yrs.sort()
        print(f"  median span of cited years:        {spans_yrs[len(spans_yrs)//2]} years")
    by_status: dict[str, int] = {}
    for row in rows:
        by_status[row["status"] or "(unclassified)"] = by_status.get(
            row["status"] or "(unclassified)", 0) + 1
    print("  by status (mapping assumed):")
    for label, count in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"    {label:20s} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
