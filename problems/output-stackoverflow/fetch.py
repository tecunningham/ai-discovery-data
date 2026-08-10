#!/usr/bin/env python3
"""Rebuild stackoverflow-questions-monthly.csv from the Stack Exchange API.

Run: python3 problems/output-stackoverflow/fetch.py

One request per month, so a full rebuild is a few hundred calls and takes
several minutes; the sleeps below are what keeps it polite, and the API's own
backoff instruction is obeyed when it sends one.
"""

from __future__ import annotations

import calendar
import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = ("https://api.stackexchange.com/2.3/questions?site=stackoverflow"
       "&fromdate={start}&todate={end}&filter=total")
START = (2019, 1)


def build() -> list[dict]:
    """Surviving questions by creation month, via the Stack Exchange API.

    The API counts questions that exist now, by creation date, so deleted
    questions vanish retroactively and older months are undercounts.
    """
    today = dt.date.today()
    rows = []
    year, month = START
    while (year, month) < (today.year, today.month):  # full months only
        start = int(dt.datetime(year, month, 1,
                                tzinfo=dt.timezone.utc).timestamp())
        last = calendar.monthrange(year, month)[1]
        end = int(dt.datetime(year, month, last, 23, 59, 59,
                              tzinfo=dt.timezone.utc).timestamp())
        payload = json.loads(fetch(URL.format(start=start, end=end)))
        rows.append({"month": f"{year}-{month:02d}",
                     "questions": str(payload["total"])})
        if payload.get("backoff"):
            time.sleep(payload["backoff"])
        time.sleep(0.3)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    print(f"stackoverflow: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"{rows[0]['questions']} → {rows[-1]['questions']} questions")
    return rows


if __name__ == "__main__":
    write_csv(HERE / "stackoverflow-questions-monthly.csv", build())
