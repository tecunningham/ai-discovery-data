#!/usr/bin/env python3
"""Report whether the Hutter Prize has awarded a record past this folder's CSV.

Run: python3 problems/algorithms-enwik9/fetch.py

This is a staleness probe, not a fetcher: it never writes. Both upstreams are
prose pages with an HTML table, and an entry records authorship, the award
status and the caveats that separate the capped prize from the uncapped
leaderboard — judgment no parser should guess at. So the check is only whether
the standing awarded record still appears on the prize page, and an update is
made by hand.

The enwik8 slice has no probe of its own: that series was retired in 2020 and
the prize page carries only the live enwik9 records.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

# the prize site's TLS certificate is expired; it is read over plain HTTP
URL = "http://prize.hutter1.net/"


def probe() -> str | None:
    vendored = [row for row in read_csv(HERE / "enwik9-records.csv")
                if row["series"] == "hutter_enwik9" and row["award"] == "yes"]
    record = vendored[-1]["total_bytes"] if vendored else "?"
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    # the page groups digits with apostrophes
    pretty = f"{int(record):,}".replace(",", "'")
    if record not in text.replace("'", "").replace(",", "") and pretty not in text:
        return (f"enwik9-records.csv: vendored record {record} bytes no longer "
                "on the prize page — a new record was likely awarded; update the CSV "
                "and this folder's README.md by hand")
    return None


def main() -> int:
    message = probe()
    if message:
        print(f"⚠️  {message}")
        return 1
    print("enwik9-records.csv: standing awarded record still on the prize page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
