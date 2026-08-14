#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose.

Also cross-checks the two ledgers against each other: every solved status the
fetcher writes must have a hand-transcribed event row, and vice versa, so a
refetch that flips a status without the event ledger being reviewed fails
here rather than standing silently.
"""

from __future__ import annotations

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
    top_two_solves = sum(
        by_slug[slug]["notability"] in ("Major advance", "Breakthrough")
        for slug in solved)
    if top_two_solves:
        failures.append(f"{top_two_solves} solves sit in the top two tiers; "
                        "the prose says both are untouched")

    claims = {
        f"{len(problems)} problem pages": "page count",
        f"{ai_solves} are marked solved by AI, {human_solves} by humans, "
        f"and {unsolved} stand unsolved": "status split",
        f"{tier_counts['Moderately interesting']} moderately interesting, "
        f"{tier_counts['Solid result']} solid result, "
        f"{tier_counts['Major advance']} major advance, and "
        f"{tier_counts['Breakthrough']} breakthrough": "tier split",
        f"{len(dated)} of the {len(events)} recorded solves carry a date":
            "dated events",
        f"from {dated[0]} to {dated[-1]}": "event span",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
