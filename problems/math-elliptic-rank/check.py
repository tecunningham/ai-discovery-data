#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the four CSVs."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {8: "eight", 18: "eighteen", 19: "nineteen"}


def main() -> int:
    records = read_csv(HERE / "elliptic-curve-rank-records.csv")
    exact = read_csv(HERE / "elliptic-curve-rank-exact.csv")
    board = read_csv(HERE / "elliptic-rank-leaderboard.csv")
    timeline = read_csv(HERE / "rank30-timeline.csv")
    years = [int(row["year"]) for row in records]
    failures: list[str] = []

    humans = [row for row in records if row["credit"] == "human"]
    ais = [row for row in records if row["credit"] == "ai"]
    if len(humans) + len(ais) != len(records):
        stray = sorted({row["credit"] for row in records} - {"human", "ai"})
        failures.append(f"credit values {stray} are neither human nor ai")
    if [row["year"] for row in ais] != ["2026"]:
        failures.append("the page states the 2026 row is the only ai-credited "
                        f"row; the CSV's ai rows are dated "
                        f"{[row['year'] for row in ais]}")
    # The page's whole reading of the frontier is that it only ever rises, and
    # a table row transcribed out of order would break that silently.
    if years != sorted(years) or [int(r["rank"]) for r in records] != sorted(
            int(r["rank"]) for r in records):
        failures.append("record rows are not in nondecreasing year and rank "
                        "order, so the frontier is not a staircase")

    first, last = records[0], records[-1]
    early = [year for year in years if 1974 <= year <= 2000]
    late = [year for year in years if year > 2000]
    pre = [year for year in years if year < 1974]
    gap, gap_from, gap_to = max(
        (years[i + 1] - years[i], years[i], years[i + 1])
        for i in range(len(years) - 1))
    recent = [row for row in records if int(row["year"]) > 2000]
    count = lambda year: years.count(year)  # noqa: E731

    dates = sorted(row["date"] for row in board)
    ranks = [int(row["rank"]) for row in board]
    months = Counter(row["date"][:7] for row in board)
    top = max(board, key=lambda row: (int(row["rank"]), -int(row["curve_id"])))

    # The gap the page prints is the difference between the two timeline rows
    # it rests on, not a number typed into the prose.
    challenge = next(row for row in timeline if "challenge" in row["event"])
    submitted = next(row for row in timeline if "submitted" in row["event"])
    latency = (date.fromisoformat(submitted["date"])
               - date.fromisoformat(challenge["date"])).days
    if latency != 15:
        failures.append(f"the page says the challenge was met fifteen days "
                        f"later; the timeline gives {latency}")
    dated = [row["date"] for row in timeline]
    if dated != sorted(dated):
        failures.append("rank30-timeline.csv rows are not in date order")

    step = lambda row, sign: (  # noqa: E731
        f"rank {sign} {row['rank']} ({row['discoverer']}, {row['year']})")
    claims = {
        f"**steps:** {len(records)} recorded steps, {first['year']} to "
        f"{last['year']}, {len(humans)} credited human and {len(ais)} "
        "credited ai": "steps fact",
        f"**span:** {step(first, '≥')} to {step(last, '≥')}": "span fact",
        f"**by-period:** {len(pre)} steps over 1938–1945 · {len(early)} steps "
        f"over 1974–2000 · {len(late)} steps over 2001–2026": "by-period fact",
        f"**longest gap:** {gap} years, from {gap_from} to {gap_to}":
            "longest-gap fact",
        "**recent steps:** " + " · ".join(step(row, "≥") for row in recent):
            "recent-steps fact",
        f"**exact frontier:** {len(exact)} recorded steps, "
        f"{step(exact[0], '=')} to {step(exact[-1], '=')}": "exact fact",
        f"**ai-attributed:** {len(ais)} of {len(records)} record steps":
            "ai-attributed fact",
        f"**board rows:** {len(board)} curves, {dates[0]} to {dates[-1]}, from "
        f"{len({row['submitter'] for row in board})} submitters, covering "
        f"ranks {min(ranks)} to {max(ranks)}": "board-rows fact",
        "**board cadence:** " + " · ".join(
            f"{count} curves in {month}" if index == 0 else f"{count} in {month}"
            for index, (month, count) in enumerate(sorted(months.items()))):
            "board-cadence fact",
        f"**board record curve:** curve #{top['curve_id']}, rank ≥ "
        f"{top['rank']}, log conductor {top['log_conductor']}, naive height "
        f"{top['naive_height']}, submitted {top['date']}":
            "board-record fact",
        f"**timeline:** {len(timeline)} dated events, "
        f"{timeline[0]['date']} to {timeline[-1]['date']}": "timeline fact",
        f"posed publicly on {challenge['date']} and submitted on "
        f"{submitted['date']}, {latency} days later": "challenge-gap fact",
        f"On {challenge['date']}, fifteen days before the curve was submitted":
            "challenge-gap lead",
        f"inconclusive — {count(2026)} record step in 2026 against "
        f"{count(2025)} in 2025 and {count(2024)} in 2024; {len(late)} steps "
        f"over 2001–2026 against {len(early)} over 1974–2000": "verdict clause",
        f"Coverage:** {WORDS[len(records)]} record steps, {first['year']} to "
        f"{last['year']}": "coverage field",
        f"One of the {len(records)} record steps carries an AI credit: the "
        "`credit` column is `ai` for the 2026 row and `human` for the other "
        f"{len(humans)}": "AI-attribution lead",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
