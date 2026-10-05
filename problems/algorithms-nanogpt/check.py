#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "nanogpt-records.csv")
    records = [row for row in rows if row["kind"] == "record"]
    retimings = [row for row in rows if row["kind"] == "retiming"]
    pending = [row for row in rows if row["kind"] == "pending"]
    unvetted = [row for row in rows if row["kind"] == "claim"]
    ai = [row for row in records if row["agent"] == "ai"]
    assisted = [row for row in records if row["agent"] == "ai_assisted"]
    failures = []
    if len(ai) != 5:
        failures.append(f"{len(ai)} AI-credited records; the page states five")
    if len(assisted) != 3:
        failures.append(f"{len(assisted)} AI-assisted records; the page states three")
    if len(retimings) != 2:
        failures.append(f"{len(retimings)} re-timing rows; the page states three")

    first, last = records[0], records[-1]
    # Each AI record is measured against the record it displaced, in table order.
    steps = []
    for row in ai:
        prev = records[records.index(row) - 1]
        steps.append(100 * (1 - float(row["minutes"]) / float(prev["minutes"])))
    by_year = {year: [row for row in records if row["date"].startswith(year)]
               for year in ("2024", "2025", "2026")}
    fell = [float(by_year["2024"][0]["minutes"]) / float(by_year["2024"][-1]["minutes"]),
            float(by_year["2024"][-1]["minutes"]) / float(by_year["2025"][-1]["minutes"]),
            float(by_year["2025"][-1]["minutes"]) / float(by_year["2026"][-1]["minutes"])]

    ai_list = ", ".join(
        f"record {row['record']} to {row['ai_system']} at {row['minutes']}"
        + (" minutes" if row is ai[0] else "") + f" ({row['date']})"
        for row in ai[:-1]) + (
        f", and record {ai[-1]['record']} to {ai[-1]['ai_system']} at "
        f"{ai[-1]['minutes']} ({ai[-1]['date']})")
    claims = {
        f"**span:** {first['minutes']} minutes at the llm.c baseline of "
        f"{first['date']}, down to {last['minutes']} minutes at record "
        f"{last['record']} on {last['date']} — a reduction of about "
        f"{round(float(first['minutes']) / float(last['minutes']))} times":
            "span fact",
        f"**records per period:** {len(by_year['2024'])} records in 2024, "
        f"{len(by_year['2025'])} in 2025, and {len(by_year['2026'])} in 2026 "
        f"through {by_year['2026'][-1]['date']}": "records-per-period fact",
        f"**standing-record falls:** over the same three periods the "
        f"standing record fell by a factor of {fell[0]:.1f}, then "
        f"{fell[1]:.1f}, then {fell[2]:.1f}": "standing-record-falls fact",
        f"**ai-records:** {len(ai)} records out of {len(records)}: {ai_list}":
            "ai-records fact",
        f"the five AI steps are {steps[0]:.1f}%, {steps[1]:.1f}%, "
        f"{steps[2]:.1f}%, {steps[3]:.1f}% and {steps[4]:.1f}%":
            "ai-step-sizes fact",
        "**ai-assisted records:** " + "; ".join(
            f"record {row['record']} at {row['minutes']} minutes "
            f"({row['date']}) with {row['ai_system']}"
            for row in assisted): "ai-assisted fact",
        f"at {retimings[0]['minutes']} minutes and again on the then-current "
        f"torch at {retimings[1]['minutes']}": "re-timing values",
        f"{'accelerating' if fell[2] > fell[1] else 'no acceleration'} — "
        f"the standing record fell {fell[2]:.1f}× in 2026 "
        f"({len(by_year['2026'])} records through {last['date']}) against "
        f"{fell[1]:.1f}× in 2025 ({len(by_year['2025'])} records) and "
        f"{fell[0]:.1f}× in 2024 ({len(by_year['2024'])} records)":
            "verdict clause",
        f"{first['date']} to {last['date']}, all {len(records)} records":
            "coverage field",
        "**pending:** " + (
            f"{len(pending)} open pull request{'s' if len(pending) != 1 else ''} "
            "claiming a time below the standing record with the evidence the "
            "rules ask for: " + ", ".join(
                f"#{row['record'][2:]} at {row['minutes']} minutes, opened "
                f"{row['date']}" for row in pending)
            if pending else
            "no open pull request claims a time below the standing record with "
            "the evidence the rules ask for"):
            "pending fact",
        "**unvetted claims:** " + (
            f"{len(unvetted)} more open pull request"
            f"{'s' if len(unvetted) != 1 else ''} claiming a lower time without "
            "it: " + ", ".join(
                f"#{row['record'][2:]} at {row['minutes']} minutes, opened "
                f"{row['date']}" for row in unvetted)
            if unvetted else "none"):
            "unvetted-claims fact",
    }
    # The biggest one-record cut in 2026, against the record it displaced.
    cuts = [(1 - float(row["minutes"]) / float(records[i - 1]["minutes"]), row,
             records[i - 1]) for i, row in enumerate(records)
            if i and row["date"].startswith("2026")]
    cut, big, before = max(cuts, key=lambda item: item[0])
    claims[f"**largest 2026 step:** record {big['record']} at {big['minutes']} "
           f"minutes, {100 * cut:.0f}% below record {before['record']}'s "
           f"{before['minutes']}"] = "largest-2026-step fact"
    twenty_two = [row for row in records if row["record"] in ("22", "23", "24")]
    claims[f"records 22 to 24 at {twenty_two[0]['minutes']}, "
           f"{twenty_two[1]['minutes']} and {twenty_two[2]['minutes']}"] = \
        "post-retiming records"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
