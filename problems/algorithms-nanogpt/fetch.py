#!/usr/bin/env python3
"""Report whether the modded-nanogpt README lists a record past this folder's CSV.

Run: python3 problems/algorithms-nanogpt/fetch.py

This is a staleness probe, not a fetcher: it never writes. Each row carries the
agent and the credited AI system, which the README states in prose that needs
judgment to attribute, so a new record is transcribed by hand.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = ("https://raw.githubusercontent.com/KellerJordan/modded-nanogpt/"
       "master/README.md")


def probe() -> str | None:
    vendored = read_csv(HERE / "nanogpt-records.csv")
    last_n = int(vendored[-1]["record"]) if vendored else 0
    last_minutes = vendored[-1]["minutes"] if vendored else "?"
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    # Record rows look like: "86 | 1.266 minutes | <description> | 05/27/26 | ..."
    rows = re.findall(r"(?m)^(\d+) \| ([\d.]+) minutes \|", text)
    if not rows:
        return ("nanogpt-records.csv: no record-table rows parsed from the "
                "README — its format changed; check by hand")
    newest_n, newest_minutes = max((int(n), m) for n, m in rows)
    if newest_n > last_n:
        return (f"nanogpt-records.csv: README now has record {newest_n} at "
                f"{newest_minutes} min; vendored series ends at record {last_n} "
                f"({last_minutes} min) — update the CSV and this folder's "
                "README.md by hand (authorship needs judgment)")
    return None


def main() -> int:
    message = probe()
    if message:
        print(f"⚠️  {message}")
        return 1
    print("nanogpt-records.csv: README lists no record past the vendored series")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
