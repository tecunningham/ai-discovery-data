#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {5: "five", 6: "six", 7: "seven", 15: "fifteen", 16: "sixteen"}


def main() -> int:
    rows = read_csv(HERE / "crossref-dois-by-year.csv")
    counts = {row["year"]: int(row["dois_created"]) for row in rows}
    # 2026 is a part year, so the complete series ends the year before and the
    # falls are counted over complete years only.
    complete = [row for row in rows if not row["note"]]
    values = [(row["year"], int(row["dois_created"])) for row in complete]
    falls = sum(1 for before, after in zip(values, values[1:])
                if after[1] < before[1])
    first, last = values[0], values[-1]
    current = next(row for row in rows if row["note"])
    # The note reads "year-to-date through YYYY-MM-DD"; the date is its last
    # word, and the annualization scales by days elapsed at that date.
    through = current["note"].split()[-1]
    pace = annualized(int(current["dois_created"]), through)
    mean = sum(value for _, value in values) / len(values)
    claims = {
        f"from {first[1] / 1e6:.2f} million records in {first[0]} to "
        f"{last[1] / 1e6:.2f} million in {last[0]}, up\n"
        f"{round(100 * (last[1] / first[1] - 1))}%".replace("\n", " "):
            "span fact",
        f"{WORDS[falls]} of the {WORDS[len(values) - 1]} year-on-year "
        f"changes over {first[0]}–{last[0]} are falls": "count of falls",
        f"deposits fell to {counts['2024'] / 1e6:.2f} million from "
        f"{counts['2023'] / 1e6:.2f} million in 2023, then rose to "
        f"{counts['2025'] / 1e6:.2f} million in 2025": "2024 dip",
        f"{int(current['dois_created']):,} records through {through}, "
        f"annualizing to roughly {pace / 1e6:.1f} million":
            "year-to-date fact",
        f"{current['year']} annualizes to roughly {pace / 1e6:.1f} million "
        f"records against {counts['2025'] / 1e6:.2f} million in 2025 and an "
        f"{mean / 1e6:.2f} million/year mean over {first[0]}–{last[0]}":
            "verdict clause",
        f"Coverage:** {first[0]} to {current['year']}, annual, the last "
        f"year partial through {through}": "coverage field",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
