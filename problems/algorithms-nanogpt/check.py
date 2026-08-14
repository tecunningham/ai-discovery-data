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
    ai = [row for row in records if row["agent"] == "ai"]
    failures = []
    if len(ai) != 5:
        failures.append(f"{len(ai)} AI-credited records; the page states five")
    if len(retimings) != 2:
        failures.append(f"{len(retimings)} re-timing rows; the page states two")

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
        f"{len(by_year['2025'])} in 2025, and {len(by_year['2026'])} in the "
        "first seven months of 2026": "records-per-period fact",
        f"**standing-record falls:** over the same three periods the "
        f"standing record fell by a factor of {fell[0]:.1f}, then "
        f"{fell[1]:.1f}, then {fell[2]:.1f}": "standing-record-falls fact",
        f"**ai-records:** {len(ai)} records out of {len(records)}: {ai_list}":
            "ai-records fact",
        f"the five AI steps are {steps[0]:.1f}%, {steps[1]:.1f}%, "
        f"{steps[2]:.1f}%, {steps[3]:.1f}% and {steps[4]:.1f}%":
            "ai-step-sizes fact",
        f"at {retimings[0]['minutes']} minutes and again on the then-current "
        f"torch at {retimings[1]['minutes']}": "re-timing values",
        f"no acceleration — the standing record fell {fell[2]:.1f}× in 2026 "
        f"({len(by_year['2026'])} records through {last['date']}) against "
        f"{fell[1]:.1f}× in 2025 ({len(by_year['2025'])} records) and "
        f"{fell[0]:.1f}× in 2024 ({len(by_year['2024'])} records)":
            "verdict clause",
        f"{first['date']} to {last['date']}, all {len(records)} records":
            "coverage field",
    }
    twenty_two = [row for row in records if row["record"] in ("22", "23", "24")]
    claims[f"records 22 to 24 at {twenty_two[0]['minutes']}, "
           f"{twenty_two[1]['minutes']} and {twenty_two[2]['minutes']}"] = \
        "post-retiming records"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
