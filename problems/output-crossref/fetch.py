#!/usr/bin/env python3
"""Rebuild crossref-dois-by-year.csv from the Crossref REST API.

Run: python3 problems/output-crossref/fetch.py

One rows=0 count per year, so a full rebuild is a couple of dozen requests;
the sleep between them is what keeps it polite.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = ("https://api.crossref.org/works?filter="
       "from-created-date:{year}-01-01,until-created-date:{year}-12-31"
       "&rows=0&mailto=tom.cunningham@metr.org")


def build() -> list[dict]:
    """DOI records by created (deposit) year, one rows=0 count per year.

    Deposit date, not publication date: a year's count includes backfile
    deposits of much older works and excludes works published that year but
    registered later.
    """
    today = dt.date.today()
    rows = []
    for year in range(2010, today.year + 1):
        total = json.loads(fetch(URL.format(year=year)))["message"]["total-results"]
        note = f"year-to-date through {today}" if year == today.year else ""
        rows.append({"year": str(year), "dois_created": str(total), "note": note})
        time.sleep(1.5)
    print(f"crossref: {len(rows)} years, {rows[0]['year']}–{rows[-1]['year']}; "
          f"{int(rows[-1]['dois_created']) / 1e6:.2f}M in the last year")
    return rows


if __name__ == "__main__":
    write_csv(HERE / "crossref-dois-by-year.csv", build())
