#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {5: "five", 6: "six", 7: "seven", 15: "fifteen", 16: "sixteen"}


def main() -> int:
    rows = read_csv(HERE / "crossref-dois-by-year.csv")
    counts = {row["year"]: int(row["dois_created"]) for row in rows}
    # 2026 is a part year, so the complete series ends the year before and the
    # falls are counted over complete years only.
    complete = [row for row in rows if not row["note"]]
    values = [(row["year"], int(row["dois_created"])) for row in complete]
    falls = sum(1 for before, after in zip(values, values[1:]) if after[1] < before[1])
    first, last = values[0], values[-1]
    claims = {
        f"from {first[1] / 1e6:.2f} million records in {first[0]}": "opening deposits",
        f"to {last[1] / 1e6:.2f} million in {last[0]}": "closing deposits",
        f"up\n{round(100 * (last[1] / first[1] - 1))}%".replace("\n", " "):
            "growth over the window",
        f"{WORDS[falls]} of those {WORDS[len(values) - 1]} year-on-year changes are falls":
            "count of falls",
        f"{counts['2024'] / 1e6:.2f} million from {counts['2023'] / 1e6:.2f} million":
            "2024 dip",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
