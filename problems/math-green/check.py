#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the CSV."""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "green-problems.csv")
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_count = sum(row["status"] == "open" for row in rows)
    partial = sum(row["status"] == "partial" for row in rows)
    undated = sum(row["status"] == "resolved" and not row["resolved_year"]
                  for row in rows)
    per_year = {year: dated.count(year) for year in set(dated)}
    by_year = " · ".join(f"{year}: {dated.count(year)}"
                         for year in sorted(set(dated)))
    span_years = max(dated) - min(dated) + 1
    rate = len(dated) / span_years

    failures: list[str] = []
    if undated:
        failures.append(f"{undated} resolved rows lack a year; the fact "
                        "lines assume every resolution is dated")
    if partial != 1:
        failures.append(f"{partial} partial rows, but the register and the "
                        "rows fact describe exactly one (Problem 11)")
    if per_year.get(2026, 0):
        failures.append(f"{per_year[2026]} rows dated 2026; the verdict and "
                        "the AI-attribution section assume zero")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {partial} partial; {open_count} open": "rows fact",
        f"**span:** dated resolutions {min(dated)}–{max(dated)}": "span fact",
        f"**by-year:** {by_year}": "by-year fact",
        f"**ai-attributed:** 0 of {len(dated)} dated resolutions": "AI fact",
        f"{per_year.get(2026, 0)} dated resolutions in 2026 against "
        f"{per_year.get(2025, 0)} in 2025 and a {rate:.1f}/year mean over "
        f"{min(dated)}–{max(dated)}": "verdict clause",
        f"read 2026-08-13; dated resolutions {min(dated)}–{max(dated)}":
            "coverage field",
        f"0 of the {len(dated)} dated resolutions carry AI credit":
            "AI negative",
    }
    # Every non-open row appears in the register with the CSV's own values,
    # in the fixed key order status / resolved / resolver / notes. Values are
    # whitespace-collapsed the same way lib.prose collapses the page.
    for row in rows:
        if row["status"] == "open":
            continue
        entry = (f"### {row['problem_id']} — {row['short_name']} "
                 f"- **status:** {row['status']} "
                 f"- **resolved:** {row['resolved_year']} "
                 f"- **resolver:** {row['resolver']}")
        if row["notes"]:
            entry += f" - **notes:** {row['notes']}"
        claims[re.sub(r"\s+", " ", entry)] = (
            f"register entry {row['problem_id']}")
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
