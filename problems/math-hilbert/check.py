#!/usr/bin/env python3
"""Recompute this page's fact lines and register entries from the CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def register_entry(row: dict[str, str]) -> str:
    """A register ### block, collapsed the way prose() collapses the page."""
    return " ".join((
        f"### {row['problem_id']} — {row['short_name']}",
        f"- **status:** {row['status']}",
        f"- **resolved:** {row['resolved_year']}".rstrip(),
        f"- **resolver:** {row['resolver']}".rstrip(),
    ))


def main() -> int:
    rows = read_csv(HERE / "hilbert-problems.csv")
    status = Counter(row["status"] for row in rows)
    dated = sorted(int(row["resolved_year"]) for row in rows
                   if row["status"] == "resolved" and row["resolved_year"])
    open_ids = [row["problem_id"] for row in rows if row["status"] == "open"]
    by_year = " · ".join(f"{year}: {dated.count(year)}"
                         for year in sorted(set(dated)))
    failures: list[str] = []
    if status["resolved"] != len(dated):
        failures.append("a resolved row has no resolved_year; the facts "
                        "count dated resolutions only")
    if dated and dated[-1] > 2025:
        failures.append("a dated resolution in 2026 exists; the verdict "
                        "clause stating 0 in 2026 is stale")

    claims = {
        f"**rows:** {len(rows)} scored; {len(dated)} resolved with a dated "
        f"year; {len(open_ids)} open; {status['contested']} contested; "
        f"{status['vague']} vague": "rows fact",
        f"**span:** dated resolutions {dated[0]}–{dated[-1]}": "span fact",
        f"**by-year:** {by_year}": "by-year fact",
        f"**ai-attributed:** 0 of {len(dated)} dated resolutions": "AI fact",
        "**open rows:** " + ", ".join(open_ids): "open-rows fact",
        f"0 resolutions in 2026 and 0 since {dated[-1]}; {len(dated)} dated "
        f"resolutions over {dated[0]}–{dated[-1]}": "verdict clause",
    }
    # Every non-open row appears in the register with the CSV's own values,
    # in the fixed key order status / resolved / resolver.
    for row in rows:
        if row["status"] == "open":
            continue
        claims[register_entry(row)] = f"register entry {row['problem_id']}"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
