#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {6: "six", 7: "seven", 8: "eight", 14: "fourteen", 15: "fifteen",
         16: "sixteen", 17: "seventeen", 18: "eighteen"}


def main() -> int:
    rows = read_csv(HERE / "matrix-multiplication-omega.csv")
    first, last = rows[0], rows[-1]
    close_1990 = next(row for row in rows if row["year"] == "1990")
    first_2010 = next(row for row in rows if row["year"] == "2010")
    early = float(first["omega"]) - float(close_1990["omega"])
    late = float(first_2010["omega"]) - float(last["omega"])
    post_2010 = [row for row in rows if int(row["year"]) >= 2010]
    span_2010 = int(last["year"]) - int(first_2010["year"])
    count = lambda year: sum(row["year"] == year for row in rows)  # noqa: E731
    failures: list[str] = []
    humans = [row for row in rows if row["credit"] == "human"]
    ais = [row for row in rows if row["credit"] == "ai"]
    if len(humans) + len(ais) != len(rows):
        stray = sorted({row["credit"] for row in rows} - {"human", "ai"})
        failures.append(f"credit values {stray} are neither human nor ai")
    if [row["year"] for row in ais] != ["2026"]:
        failures.append("the page states the 2026 row is the only ai-credited "
                        f"row; the CSV's ai rows are dated "
                        f"{[row['year'] for row in ais]}")

    claims = {
        f"**steps:** {len(rows)} recorded steps, {first['year']} to "
        f"{last['year']}, {len(humans)} credited human and {len(ais)} "
        "credited ai": "steps fact",
        f"**span:** {first['omega']} ({first['discoverer']}, "
        f"{first['year']}) to {last['omega']} ({last['discoverer']}, "
        f"{last['year']})": "span fact",
        f"**first two decades:** the bound fell {early:.4f} from "
        f"{first['year']} to {close_1990['year']}, closing at "
        f"{close_1990['omega']} ({close_1990['discoverer']}, "
        f"{close_1990['year']})": "first-two-decades fact",
        "**post-2010 steps:** " + " · ".join(
            f"{row['omega']} ({row['discoverer']}, {row['year']})"
            for row in post_2010): "post-2010 fact",
        f"**since 2010:** the {WORDS[len(post_2010) - 1]} steps after the "
        f"2010 record total {late:.4f} over {WORDS[span_2010]} years":
            "since-2010 fact",
        f"inconclusive — {count('2026')} new bound in 2026 against "
        f"{count('2025')} in 2025 and {count('2024')} in 2024; movement of "
        f"{late:.4f} over 2010–{last['year']} against {early:.4f} over "
        f"{first['year']}–{close_1990['year']}": "verdict clause",
        f"Coverage:** {first['year']} to {last['year']}, "
        f"{WORDS[len(rows)]} recorded steps": "coverage field",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
