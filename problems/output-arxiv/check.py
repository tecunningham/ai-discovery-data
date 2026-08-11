#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The final row is the month in progress at fetch time, so the last complete
    # month is the one before it. The prose quotes that one.
    complete = rows[-2]["month"]
    growth = round((counts[complete] / counts["2022-11"] - 1) * 100)
    claims = {
        f"from {counts['2022-11']:,} in November 2022": "ChatGPT-month baseline",
        f"to {counts[complete]:,} in July 2026, the last complete month":
            "latest complete month",
        f"{growth}% in three years": "growth since 2022-11",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
