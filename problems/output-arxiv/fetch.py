#!/usr/bin/env python3
"""Rebuild arxiv-monthly.csv from arXiv's own statistics download.

Run: python3 problems/output-arxiv/fetch.py
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

URL = "https://arxiv.org/stats/get_monthly_submissions"


def build() -> list[dict]:
    """Monthly submissions.

    The raw download carries a historical_delta column, nonzero only for
    1991–1997 corrections, which is dropped here.
    """
    raw = fetch(URL).decode("utf-8")
    rows = [{"month": row["month"], "submissions": row["submissions"]}
            for row in csv.DictReader(io.StringIO(raw))]
    print(f"arxiv: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"{rows[-1]['submissions']} in the last month")
    return rows


if __name__ == "__main__":
    write_csv(HERE / "arxiv-monthly.csv", build())
