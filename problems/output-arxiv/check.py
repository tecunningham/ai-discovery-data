#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def as_of_month() -> str:
    """lib/chart.py's snapshot month, read textually: importing lib.chart would
    pull in matplotlib, which the host-side checks deliberately do not need."""
    import re

    text = (HERE.parents[1] / "lib" / "chart.py").read_text(encoding="utf-8")
    year, month, _ = re.search(
        r"^AS_OF_DATE\s*=\s*date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)",
        text, re.M).groups()
    return f"{year}-{int(month):02d}"


def main() -> int:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The final row is the month in progress at fetch time, so the last complete
    # month is the one before it. The prose quotes that one. The rule silently
    # breaks when a fetch lands just after a month boundary, before arXiv opens
    # the new month's row — so it is asserted rather than assumed.
    failures = []
    if rows[-1]["month"] != as_of_month():
        failures.append(
            f"the last row is {rows[-1]['month']}, not the AS_OF_DATE month; "
            "the last-row-is-partial rule no longer holds")
    complete = rows[-2]["month"]
    growth = round((counts[complete] / counts["2022-11"] - 1) * 100)
    claims = {
        f"from {counts['2022-11']:,} in November 2022": "ChatGPT-month baseline",
        f"to {counts[complete]:,} in July 2026, the last complete month":
            "latest complete month",
        f"{growth}% in three years": "growth since 2022-11",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
