#!/usr/bin/env python3
"""Rebuild stockfish-ncm-elo.csv from nextchessmove's dev-builds page.

Run: python3 problems/algorithms-stockfish/fetch.py

The page draws its chart from one JavaScript array, one entry per tested
build:

    ["<sha>", "<ISO datetime>", "<commit title>", "<release>" | null,
     [<elo vs Stockfish 15>, <error>], [<elo vs another base>, <error>]]

Every entry becomes a row in upstream's own order, which is test order rather
than strict date order. The release column is the entry's own tag ("17.1"),
empty for an untagged build. Upstream repeats some recent entries verbatim, so
a commit already seen is skipped; it also back-fills and re-measures older
builds, so a refetch can revise rows before the last vendored date as well as
add new ones. Builds tested after lib/dates.py's AS_OF_DATE are dropped, so a
refetch reproduces the committed window.

If the array cannot be found, or yields far fewer rows than are vendored, the
page format has changed: the script leaves the CSV alone and exits
NEEDS_PERSON rather than writing a truncated series.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import AS_OF_DATE  # noqa: E402
from lib.table import read_csv, write_csv  # noqa: E402
from lib.web import NEEDS_PERSON, fetch  # noqa: E402

URL = "https://nextchessmove.com/dev-builds"
CSV = HERE / "stockfish-ncm-elo.csv"
FIELDS = ["date", "release", "elo_vs_sf15", "elo_err"]

STRING = r'"(?:[^"\\]|\\.)*"'
ENTRY = re.compile(
    rf'\["([0-9a-f]{{40}})","(\d{{4}}-\d\d-\d\d)T[\d:]+",(?:{STRING}|null),'
    rf'({STRING}|null),\[(-?\d+(?:\.\d+)?),(\d+(?:\.\d+)?)\]')


def parse(text: str) -> list[dict[str, str]]:
    rows, seen = [], set()
    for sha, day, release, elo, err in ENTRY.findall(text):
        if sha in seen or day > AS_OF_DATE.isoformat():
            continue
        seen.add(sha)
        rows.append({"date": day, "release": json.loads(release) or "",
                     "elo_vs_sf15": elo, "elo_err": err})
    return rows


def main() -> int:
    vendored = read_csv(CSV)
    rows = parse(fetch(URL, refresh=True).decode("utf-8", errors="replace"))
    if len(rows) < 0.9 * len(vendored):
        print(f"⚠️  {CSV.name}: parsed {len(rows)} builds from the dev-builds "
              f"page against {len(vendored)} vendored — the page format may "
              "have changed; check by hand")
        return NEEDS_PERSON
    if rows == vendored:
        print(f"{CSV.name}: {len(rows)} builds through {rows[-1]['date']}, unchanged")
        return 0
    write_csv(CSV, rows, FIELDS)
    print(f"wrote {CSV.name}: {len(rows)} builds through {rows[-1]['date']} "
          f"({len(vendored)} before)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
