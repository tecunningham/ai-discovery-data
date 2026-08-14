#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the ledgers.

Also cross-checks the two ledgers against each other: every solved status the
fetcher writes must have a hand-transcribed event row, and vice versa, so a
refetch that flips a status without the event ledger being reviewed fails
here rather than standing silently.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

TIERS = ("Moderately interesting", "Solid result", "Major advance",
         "Breakthrough")


def main() -> int:
    problems = read_csv(HERE / "frontiermath-open-problems.csv")
    events = read_csv(HERE / "frontiermath-open-solutions.csv")
    failures: list[str] = []

    by_slug = {row["slug"]: row for row in problems}
    solved = {row["slug"]: row["status"] for row in problems
              if row["status"] != "unsolved"}
    evented = {row["slug"]: row["event"] for row in events}
    for slug in sorted(set(solved) ^ set(evented)):
        failures.append(f"{slug} is in one ledger's solved set but not the "
                        "other's; review the event ledger against the refetch")
    for slug in sorted(set(solved) & set(evented)):
        if solved[slug] != evented[slug]:
            failures.append(f"{slug} is {solved[slug]} on its page but "
                            f"{evented[slug]} in the event ledger")

    dated = sorted(row["date"] for row in events if row["date"])
    ai_solves = sum(row["status"] == "solved_ai" for row in problems)
    human_solves = sum(row["status"] == "solved_human" for row in problems)
    unsolved = sum(row["status"] == "unsolved" for row in problems)
    tier_counts = {tier: sum(row["notability"] == tier for row in problems)
                   for tier in TIERS}
    off_scale = len(problems) - sum(tier_counts.values())
    solve_tiers = [by_slug[slug]["notability"] for slug in solved
                   if slug in by_slug]
    top_two_solves = sum(tier in ("Major advance", "Breakthrough")
                         for tier in solve_tiers)
    if top_two_solves:
        failures.append(f"{top_two_solves} solves sit in the top two tiers; "
                        "the placement fact and the AI-attribution negative "
                        "say both stand at zero")
    if off_scale != 1:
        failures.append(f"{off_scale} pages sit outside the four tiers; the "
                        "tiers fact describes exactly one (Novel example)")

    claims = {
        f"**pages:** {len(problems)} problem pages in the sitemap read of "
        f"2026-08-14; {ai_solves} marked solved by AI, {human_solves} by "
        f"humans, {unsolved} unsolved": "pages fact",
        f"**tiers:** {tier_counts['Moderately interesting']} moderately "
        f"interesting · {tier_counts['Solid result']} solid result · "
        f"{tier_counts['Major advance']} major advance · "
        f"{tier_counts['Breakthrough']} breakthrough; {off_scale} withdrawn "
        "page badged Novel example": "tiers fact",
        f"**events:** {len(events)} recorded solves; {len(dated)} carry a "
        f"date, running {dated[0]} to {dated[-1]}": "events fact",
        f"**placement:** "
        f"{solve_tiers.count('Moderately interesting')} solves in moderately "
        f"interesting, {solve_tiers.count('Solid result')} in solid result, "
        f"{solve_tiers.count('Novel example')} on the Novel-example page; "
        f"{solve_tiers.count('Major advance')} in major advance and "
        f"{solve_tiers.count('Breakthrough')} in breakthrough":
            "placement fact",
        f"{len(dated)} dated solves between {dated[0]} and {dated[-1]}":
            "verdict clause",
        f"recorded solves from {dated[0]} to {dated[-1]}": "coverage field",
        f"{ai_solves} of the {len(events)} recorded solves are credited to "
        "AI systems in the event ledger": "AI share",
    }
    # Every event row appears in the register keyed on its slug, with the
    # page ledger's title and tier and the event ledger's own values, in the
    # fixed key order event / date / system / elicited by / tier / notes.
    # The stale note on the withdrawn row is not restated (its page has
    # since named a system), so notes are asserted for the other rows only.
    for row in events:
        entry = (f"### {row['slug']} — {by_slug[row['slug']]['title']} "
                 f"- **event:** {row['event']} "
                 f"- **date:** {row['date']} "
                 f"- **system:** {row['system']} "
                 f"- **elicited by:** {row['elicited_by']} "
                 f"- **tier:** {by_slug[row['slug']]['notability']}")
        if row["slug"] != "explicit-deformations":
            entry += f" - **notes:** {row['note']}"
        claims[re.sub(r"\s+", " ", entry)] = f"register entry {row['slug']}"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
