#!/usr/bin/env python3
"""Rebuild this folder's snapshot history from the Erdős problems repository.

Run: python3 problems/math-erdos/fetch.py

github.com/teorth/erdosproblems ships data/statistics_history.csv, a per-commit
snapshot of how many problems the database holds, how many carry a solved status,
and how many statements are formalized in Lean. One row per calendar month is
kept, the last snapshot in that month.

Note the confound, which is severe before April 2026: the corpus was still being
catalogued, so `solved` rose partly because already-solved problems were being
added. From 2026-04 the total is fixed at 1217, and after that a rise in `solved`
is a genuine new resolution — which is what catalogue_count_unchanged flags.

Every vendored row, endpoint included, comes from this history. An earlier
version set the final row by hand from the live website's solved headline,
which runs about six above the statistics history; that endpoint was abandoned
as unrebuildable, and the folder README records the discrepancy instead.
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = (
    "https://raw.githubusercontent.com/teorth/erdosproblems/"
    "main/data/statistics_history.csv"
)


def build_history() -> list[dict]:
    text = fetch(URL).decode("utf-8", "replace")
    monthly: dict[str, dict] = {}
    for record in csv.DictReader(io.StringIO(text)):
        date = (record.get("date") or "")[:10]
        if len(date) != 10:
            continue
        try:
            monthly[date[:7]] = {
                "month": date[:7],
                "date": date,
                "total_problems": int(record["total_problems"]),
                "total_solved": int(record["total_solved"]),
                "lean_formalized": int(record["lean_formalized"]),
            }
        except (KeyError, ValueError):
            continue
    rows = [monthly[key] for key in sorted(monthly)]
    # Once the catalogue count stops changing, a rise in `solved` cannot be
    # caused by adding a newly catalogued, already-solved problem. The cohort
    # and statuses remain editable, and status dates are not solution dates.
    final_total = rows[-1]["total_problems"]
    for row in rows:
        row["catalogue_count_unchanged"] = (
            "yes" if row["total_problems"] == final_total else "no")
    unchanged = [row for row in rows if row["catalogue_count_unchanged"] == "yes"]
    print(f"erdos: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"catalogue count unchanged at {final_total} from "
          f"{unchanged[0]['month']}")
    print(f"  solved {rows[0]['total_solved']} → {rows[-1]['total_solved']} overall; "
          f"{unchanged[0]['total_solved']} → {unchanged[-1]['total_solved']} "
          f"(net +{unchanged[-1]['total_solved'] - unchanged[0]['total_solved']}) "
          "while catalogue count unchanged")
    return rows


def main() -> None:
    write_csv(HERE / "erdos-database-history.csv", build_history())


if __name__ == "__main__":
    main()
