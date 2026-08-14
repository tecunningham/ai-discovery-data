#!/usr/bin/env python3
"""Recompute this page's fact lines from the record list beside it."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The date the record was last confirmed unmoved, stated in the Coverage line.
AS_OF = date(2026, 8, 10)


def rate(start: dict[str, str], end: dict[str, str]) -> float:
    days = (date.fromisoformat(end["date"])
            - date.fromisoformat(start["date"])).days
    return (int(end["digits"]) - int(start["digits"])) / (days / 365.25)


def main() -> int:
    rows = read_csv(HERE / "factoring-records.csv")
    fact = sorted((row for row in rows
                   if row["domain"] == "integer_factorization"),
                  key=lambda row: row["date"])
    dlps = [row for row in rows if row["domain"] == "discrete_logarithm"]
    shas = [row for row in rows if row["domain"] == "hash_collision"]
    records: list[dict[str, str]] = []
    maximum = 0
    for row in fact:
        if int(row["digits"]) > maximum:
            maximum = int(row["digits"])
            records.append(row)
    first, last = records[0], records[-1]
    split = next(row for row in records if row["record"] == "RSA-768")
    standing = (AS_OF - date.fromisoformat(last["date"])).days / 365.25
    dated = [row["date"][:4] for row in records]
    mean = len(records) / (2025 - 1991 + 1)
    rsa240 = next(row for row in fact if row["record"] == "RSA-240")

    failures: list[str] = []
    if any(row["ai_involved"] != "no" for row in rows):
        failures.append("an ai_involved cell is not 'no'; the AI attribution "
                        "section rests on that column")
    if len(dlps) != 1 or len(shas) != 1:
        failures.append("the context rows are no longer one discrete "
                        "logarithm and one hash collision")
    dlp, sha = dlps[0], shas[0]
    if dlp["date"] != rsa240["date"] or dlp["who"] != rsa240["who"]:
        failures.append("the discrete-logarithm row no longer matches "
                        "RSA-240's date and team; the context-rows fact "
                        "states they are the same")

    claims = {
        f"**rows:** {len(rows)} rows: {len(fact)} RSA factorizations, "
        f"{len(dlps)} discrete-logarithm record, {len(shas)} hash collision":
            "rows fact",
        f"**records:** {len(records)} running-maximum records, "
        f"{first['record']} ({first['digits']} digits, {first['date']}) to "
        f"{last['record']} ({last['digits']} digits, {last['date']})":
            "records fact",
        f"**rate split:** {rate(first, split):.1f} digits/year from "
        f"{first['record']} ({first['date']}) to {split['record']} "
        f"({split['digits']} digits, {split['date']}), then "
        f"{rate(split, last):.1f} digits/year to {last['record']} "
        f"({last['date']})": "rate-split fact",
        f"**standing:** the {last['digits']}-digit record is unmoved from "
        f"{last['date']} to {AS_OF.isoformat()}, {standing:.1f} years":
            "standing fact",
        f"**non-records:** {len(fact) - len(records)} of the {len(fact)} "
        "factorizations set no new maximum": "non-records fact",
        f"**ai-involved:** `no` on all {len(rows)} rows": "AI fact",
        f"**context rows:** the discrete-logarithm record is dated "
        f"{dlp['date']}, the same date and team as RSA-240; the SHA-1 "
        f"collision is dated {sha['date']} with method \"{sha['method']}\"":
            "context-rows fact",
        f"{dated.count('2026')} records in 2026 against "
        f"{dated.count('2025')} in 2025 and a {mean:.1f}/year mean over "
        f"1991–2025; the standing record is {last['digits']} digits, set "
        f"{last['date']}": "verdict clause",
        f"Coverage:** {first['date'][:7]} to {last['date'][:7]}, confirmed "
        f"unmoved as of {AS_OF.isoformat()}": "coverage field",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
