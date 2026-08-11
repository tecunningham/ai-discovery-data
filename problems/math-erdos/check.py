#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {30: "thirty", 34: "thirty-four", 40: "forty", 13: "thirteen"}


def main() -> int:
    rows = read_csv(HERE / "erdos-database-history.csv")
    first, last = rows[0], rows[-1]
    fixed = [row for row in rows if row["catalogue_count_unchanged"] == "yes"]
    start, end = fixed[0], fixed[-1]
    gained = int(end["total_solved"]) - int(start["total_solved"])
    days = (date.fromisoformat(end["date"]) - date.fromisoformat(start["date"])).days
    failures = []
    if gained not in WORDS:
        failures.append(f"no spelled form for a gain of {gained}; extend WORDS")
    claims = {
        f"from {first['total_problems']} problems to": "opening catalogue count",
        f"{int(last['total_problems']):,}, statuses marked solved from "
        f"{first['total_solved']} to {last['total_solved']}": "solved endpoints",
        f"from {first['lean_formalized']} to {last['lean_formalized']}":
            "Lean endpoints",
        f"against those {last['total_solved']} solved statuses": "callout denominator",
        f"from {start['total_solved']} on 30 April to {last['total_solved']} on "
        f"10 August": "fixed-cohort endpoints",
        f"{WORDS.get(gained, gained)} rows in about a hundred days":
            "fixed-cohort gain",
        f"{last['lean_formalized']} against {last['total_solved']}": "crossing",
        f"stocks of {last['total_solved']} and {int(last['total_problems']):,}":
            "callout scale",
        f"{len(rows)} snapshots".replace(str(len(rows)), WORDS.get(len(rows), str(len(rows)))):
            "snapshot count",
    }
    if not 95 <= days <= 110:
        failures.append(f"fixed cohort spans {days} days, not 'about a hundred'")
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
