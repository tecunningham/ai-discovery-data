#!/usr/bin/env python3
"""Impute a solution year for every solved problem in the Erdős catalogue.

Run: python3 problems/math-erdos/fetch_solutions.py

Slow by design: it downloads the LaTeX source of every solved problem's page
(about 560 requests, throttled), which is why it is not part of `make fetch`.
Responses are cached under .cache/ for the day, so a same-day rerun is fast.

The catalogue's status dates are editing dates, not solution dates: the site
warns the gap can run to decades. This script recovers an approximate solution
year per solved problem from three sources, in order:

1. review overrides (erdos-solution-year-overrides.csv) — rows where the rules
   below misfire, each carrying the reference and reason; maintained by reading
   the problem pages, so a refetch keeps them until the page text changes;
2. the solving citation — the page's discussion usually states the resolution
   in a sentence like "Solved by Maynard [Ma16]"; the imputed year is the
   publication year of the newest reference cited in the first such sentence
   (newest, because a resolving sentence cites the prior work it builds on);
3. the AI wiki — problems whose only recorded resolution is an AI system's,
   dated in the project wiki's primary-contribution tables, which often have
   no citable paper.

Where a solving citation and an AI wiki date both exist, the earlier wins: the
question is when the problem was first resolved. Problems where no source
states a resolution are kept with an empty year, basis "none".

The imputed year is the publication year of the solving reference, not the day
the mathematics happened — the standard convention, and still an approximation.
"""

from __future__ import annotations

import re
import sys
import time
from html import unescape
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib import web  # noqa: E402
from lib.table import read_csv, write_csv  # noqa: E402

PROBLEMS_YAML = (
    "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
)
WIKI_MD = (
    "https://raw.githubusercontent.com/wiki/teorth/erdosproblems/"
    "AI-contributions-to-Erd%C5%91s-problems.md"
)
LATEX_URL = "https://www.erdosproblems.com/latex/{}"

# The catalogue's own definition: its solved count is the problems whose
# informal status is one of these three states.
SOLVED_STATES = ("proved", "disproved", "solved")

CITE = re.compile(r"\\cite\{([^}]+)\}")

# A sentence counts as stating the resolution when it attributes it: an
# explicit "solved/disproved/... by", a stated answer ("the answer is no"), a
# stated truth value, or a page-initial "Proved by X [key]".
RESOLVE_BY = re.compile(
    r"\b(?:solved|resolved|settled|answered|disproved|proved|refuted|confirmed)\b"
    r"[^.]{0,60}?\bby\b", re.I)
ANSWER_IS = re.compile(
    r"\banswer(?:\s+to\s+[^.]{0,60})?\s+(?:is|was)\s+"
    r"(?:['\"]?(?:yes|no|negative|positive|affirmative)"
    r"|in\s+the\s+(?:affirmative|negative))", re.I)
TRUE_FALSE = re.compile(
    r"\b(?:this|conjecture|question|problem|it)\b[^.]{0,40}\b(?:is|was)\s+"
    r"(?:(?:extremely|very)\s+)?(?:true|false)\b", re.I)
LEADING = re.compile(
    r"^\s*(?:This\s+(?:was|is|has\s+been)\s+)?"
    r"(?:Solved|Resolved|Settled|Answered|Disproved|Proved|Refuted)\b", re.I)
# Vocabulary of partial progress: a sentence carrying these is describing work
# towards the problem, not its resolution, however resolute its verbs.
PARTIAL_HINTS = re.compile(
    r"\b(?:partial|special\s+case|weaker|towards|first\s+progress|best\s+known|"
    r"improved|extended|generalised|generalized|strengthened|sharpened|"
    r"motivated\s+by|conjectured\s+by|asked\s+by|a\s+question\s+of)\b", re.I)

MONTHS = {name: i + 1 for i, name in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def fetch_page(number: str) -> str:
    url = LATEX_URL.format(number)
    cached = web._cache_path(url).exists()
    text = web.fetch(url).decode("utf-8", "replace")
    if not cached:
        time.sleep(0.3)
    return text


def page_parts(raw: str) -> tuple[str, dict[str, int], dict[str, str]]:
    """The page's discussion LaTeX, each cited key's publication year, and
    each key's raw bibliography entry."""
    text = re.sub(r"<script.*?</script>", "", raw, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    match = re.search(r'class="problem-additional-text"[^>]*>(.*?)</div>',
                      text, re.S)
    discussion = ""
    if match:
        discussion = unescape(re.sub(r"<[^>]+>", " ", match.group(1)))
        discussion = re.sub(r"\s+", " ", discussion).strip()
    plain = unescape(re.sub(r"<[^>]+>", " ", text))
    references: dict[str, int] = {}
    entries: dict[str, str] = {}
    tail = plain[plain.find("References"):] if "References" in plain else ""
    for entry in re.finditer(
            r"\[([A-Za-z]+\d{2}[a-z]?)\]\s+(.{10,500}?)"
            r"(?=\[[A-Za-z]+\d{2}[a-z]?\]\s|Back to the problem|$)",
            tail, re.S):
        key, body = entry.group(1), entry.group(2)
        entries[key] = re.sub(r"\s+", " ", body).strip()
        years = re.findall(r"\((\d{4})\)", body)
        if years:
            references[key] = int(years[-1])
        else:
            arxiv = re.search(r"arXiv:\s*(\d{2})\d{2}\.", body)
            if arxiv:
                references[key] = 2000 + int(arxiv.group(1))
    return discussion, references, entries


def reference_kind(reference: str, year: str, basis: str,
                   entries: dict[str, str]) -> str:
    """Classify what kind of record dates this row.

    published — the dating reference has a venue in the page's bibliography;
    preprint — every dating reference is an arXiv preprint;
    ai_wiki — dated by the AI wiki (directly or via a reviewed wiki date);
    stated — a year is stated on the page with no matching bibliography entry.
    """
    if not year:
        return ""
    if basis == "ai_wiki" or re.search(r"\d{4}-\d{2}-\d{2}", reference):
        return "ai_wiki"
    keys = [key for key in reference.split()
            if re.fullmatch(r"[A-Za-z]+\d{2}[a-z]?", key)]
    found = [entries[key] for key in keys if key in entries]
    if not found:
        return "stated"
    return "preprint" if all("arXiv" in entry for entry in found) else "published"


def sentences(discussion: str) -> list[str]:
    # Display math swallows sentence boundaries; collapse it first, and drop
    # "(see also ...)" asides so their citations do not count as solvers.
    discussion = re.sub(r"\\\[.*?\\\]", " [math] ", discussion)
    discussion = re.sub(r"\(\s*see\s+also[^)]*\)", " ", discussion, flags=re.I)
    return re.split(r"(?<=[.!?])[)'\"]*\s+(?=[A-Z\\(])", discussion)


def solving_citation(discussion: str,
                     references: dict[str, int]) -> tuple[int | None, str]:
    for sentence in sentences(discussion):
        keys = [key.strip()
                for group in CITE.findall(sentence)
                for key in group.split(",")]
        if not keys:
            continue
        cued = (LEADING.search(sentence)
                or (RESOLVE_BY.search(sentence)
                    and not PARTIAL_HINTS.search(sentence))
                or ANSWER_IS.search(sentence)
                or (TRUE_FALSE.search(sentence)
                    and not PARTIAL_HINTS.search(sentence)))
        if cued:
            years = [references[key] for key in keys if key in references]
            if years:
                newest = max(years)
                named = [key for key in keys
                         if references.get(key) == newest]
                return newest, " ".join(named)
    return None, ""


def wiki_full_solutions() -> dict[str, str]:
    """Problem number -> earliest dated full AI solution in the wiki.

    Only the primary-contribution tables (sections 1(a)-1(d)) count, and only
    rows marked as a full resolution. The four tables order their columns
    differently, so rows are scanned for a date and the marker rather than
    split positionally.
    """
    text = web.fetch(WIKI_MD).decode("utf-8", "replace")
    primary = text.split('<a id="sect-2"></a>')[0]
    dates: dict[str, str] = {}
    for line in primary.splitlines():
        if "🟢" not in line or "Full solution" not in line:
            continue
        number = re.search(r"\|\s*\[\[(\d+)\]\]", line)
        found = re.search(
            r"(\d{1,2})\s+([A-Z][a-z]{2}),?\s+(\d{4})"
            r"|([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})", line)
        if not number or not found:
            continue
        if found.group(1):
            day, month, year = (int(found.group(1)), MONTHS[found.group(2)],
                                int(found.group(3)))
        else:
            day, month, year = (int(found.group(5)), MONTHS[found.group(4)],
                                int(found.group(6)))
        iso = f"{year:04d}-{month:02d}-{day:02d}"
        key = number.group(1)
        if key not in dates or iso < dates[key]:
            dates[key] = iso
    return dates


def main() -> None:
    problems = yaml.safe_load(web.fetch(PROBLEMS_YAML).decode("utf-8"))
    solved = [(str(p["number"]), (p.get("informal_status") or {}).get("state"))
              for p in problems
              if (p.get("informal_status") or {}).get("state") in SOLVED_STATES]
    overrides = {row["problem"]: row
                 for row in read_csv(HERE / "erdos-solution-year-overrides.csv")}
    ai_dates = wiki_full_solutions()
    rows = []
    for number, state in solved:
        discussion, references, entries = page_parts(fetch_page(number))
        year, reference = solving_citation(discussion, references)
        basis = "solving_citation" if year else "none"
        wiki_date = ai_dates.get(number)
        if wiki_date and (year is None or int(wiki_date[:4]) < year):
            year, reference, basis = int(wiki_date[:4]), wiki_date, "ai_wiki"
        if number in overrides:
            entry = overrides[number]
            if entry["solution_year"]:
                year, basis = int(entry["solution_year"]), "review"
            else:
                year, basis = None, "none"
            reference = entry["reference"]
        year_text = str(year) if year else ""
        rows.append({
            "problem": number,
            "status": state,
            "solution_year": year_text,
            "basis": basis,
            "reference": reference,
            "reference_kind": reference_kind(reference, year_text, basis,
                                             entries),
        })
    rows.sort(key=lambda row: int(row["problem"]))
    write_csv(HERE / "erdos-solution-years.csv", rows)
    dated = [row for row in rows if row["solution_year"]]
    bases = {basis: sum(row["basis"] == basis for row in rows)
             for basis in ("solving_citation", "ai_wiki", "review", "none")}
    print(f"erdos solutions: {len(rows)} solved problems, "
          f"{len(dated)} with an imputed year "
          f"({bases['solving_citation']} citation, {bases['ai_wiki']} AI wiki, "
          f"{bases['review']} review, {bases['none']} none)")


if __name__ == "__main__":
    main()
