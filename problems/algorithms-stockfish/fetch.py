#!/usr/bin/env python3
"""Report whether nextchessmove has tested builds past this folder's CSV.

Run: python3 problems/algorithms-stockfish/fetch.py

This is a staleness probe, not a fetcher: it never writes. The series comes out
of a JavaScript data array on the dev-builds page, and the release tags in the
CSV are matched to builds by hand, so an extension is re-extracted rather than
parsed here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://nextchessmove.com/dev-builds"


def probe() -> str | None:
    vendored = read_csv(HERE / "stockfish-ncm-elo.csv")
    last_date = vendored[-1]["date"] if vendored else "?"
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    dates = re.findall(r"\b(20\d\d-\d\d-\d\d)", text)
    newest = max(dates) if dates else None
    if newest and newest > last_date:
        return (f"stockfish-ncm-elo.csv: newest build on the page is {newest}, "
                f"vendored series ends {last_date} — re-extract the dev-builds "
                "data array and re-vendor")
    if not dates:
        return ("stockfish-ncm-elo.csv: could not find dates on the page — "
                "page format may have changed; check by hand")
    return None


def main() -> int:
    message = probe()
    if message:
        print(f"⚠️  {message}")
        return 1
    print("stockfish-ncm-elo.csv: no build on the page past the vendored series")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
