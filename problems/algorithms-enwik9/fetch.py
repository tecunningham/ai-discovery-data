#!/usr/bin/env python3
"""Report whether the Hutter Prize has awarded a record past this folder's CSV.

Run: python3 problems/algorithms-enwik9/fetch.py

This is a staleness probe, not a fetcher: it never writes. Both upstreams are
prose pages with an HTML table, and an entry records authorship, the award
status and the caveats that separate the capped prize from the uncapped
leaderboard — judgment no parser should guess at. So the check is only whether
the prize page's record table lists an enwik9 total below the CSV's standing
awarded record, and an update is made by hand. The table keeps every past
record, so finding the vendored figure on the page proves nothing; the probe
compares against the smallest total the table lists instead.

The retired enwik8 chronology is kept as a compact context table in README.md;
it has no probe because the prize page carries only the live enwik9 records.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402
from lib.web import NEEDS_PERSON, fetch  # noqa: E402

# the prize site's TLS certificate is expired; it is read over plain HTTP
URL = "http://prize.hutter1.net/"


def table_totals(page: str) -> list[int]:
    """Every enwik9 total in the prize page's record table, in bytes.

    The table runs from its "Author (enwik9)" header to the enwik8 section and
    groups digits with apostrophes; the target row's "<" bound is skipped.
    """
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    start = text.find("(enwik9)")
    end = text.find("enwik8", start)
    if start < 0 or end < 0:
        raise SystemExit("prize page: could not find the enwik9 record table")
    return [int(match.group(1).replace("'", ""))
            for match in re.finditer(r"(?<![<\d'])(\d{2,3}'\d{3}'\d{3})",
                                     text[start:end])]


def probe() -> str | None:
    vendored = [row for row in read_csv(HERE / "enwik9-records.csv")
                if row["series"] == "hutter_enwik9" and row["award"] == "yes"]
    record = int(vendored[-1]["total_bytes"])
    totals = table_totals(fetch(URL, refresh=True).decode("utf-8", errors="replace"))
    if record not in totals:
        return (f"enwik9-records.csv: vendored record {record:,} bytes is not in "
                "the prize page's record table; check the CSV by hand")
    if min(totals) < record:
        return (f"enwik9-records.csv: the prize page lists {min(totals):,} bytes, "
                f"below the vendored record {record:,}; a new record was likely "
                "awarded; update the CSV and this folder's README.md by hand")
    return None


def main() -> int:
    message = probe()
    if message:
        print(f"⚠️  {message}")
        return NEEDS_PERSON
    print("enwik9-records.csv: standing awarded record still on the prize page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
