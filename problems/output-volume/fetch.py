#!/usr/bin/env python3
"""Rebuild four of this folder's five volume series from their own sources.

Run: python3 problems/output-volume/fetch.py

Each series comes from the publisher of the thing being counted: arXiv's own
statistics download, the Crossref REST API, the Stack Exchange API, and the
per-economy CSVs GitHub publishes as its Innovation Graph. Crossref and Stack
Exchange are one request per period, so a full rebuild is a few hundred calls
and takes several minutes; the sleeps below are what keeps it polite.

pypi-projects-over-time.csv is not rebuilt here. PyPI publishes current totals
only, so its history was assembled by hand from dated Wayback captures of the
front-page counter, each row carrying the capture URL it came from. There is
nothing to refetch.
"""

from __future__ import annotations

import calendar
import csv
import datetime as dt
import io
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

ARXIV_URL = "https://arxiv.org/stats/get_monthly_submissions"
CROSSREF_URL = ("https://api.crossref.org/works?filter="
                "from-created-date:{year}-01-01,until-created-date:{year}-12-31"
                "&rows=0&mailto=tom.cunningham@metr.org")
STACKEXCHANGE_URL = ("https://api.stackexchange.com/2.3/questions?site=stackoverflow"
                     "&fromdate={start}&todate={end}&filter=total")
INNOVATIONGRAPH_URL = ("https://raw.githubusercontent.com/github/innovationgraph/"
                       "main/data/{metric}.csv")


def build_arxiv() -> list[dict]:
    """Monthly submissions, from arXiv's own stats download.

    The raw download carries a historical_delta column, nonzero only for
    1991–1997 corrections, which is dropped here.
    """
    raw = fetch(ARXIV_URL).decode("utf-8")
    rows = [{"month": r["month"], "submissions": r["submissions"]}
            for r in csv.DictReader(io.StringIO(raw))]
    print(f"arxiv: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"{rows[-1]['submissions']} in the last month")
    return rows


def build_crossref() -> list[dict]:
    """DOI records by created (deposit) year, one rows=0 count per year.

    Deposit date, not publication date: a year's count includes backfile
    deposits of much older works and excludes works published that year but
    registered later.
    """
    today = dt.date.today()
    rows = []
    for year in range(2010, today.year + 1):
        total = json.loads(fetch(CROSSREF_URL.format(year=year)))["message"]["total-results"]
        note = f"YTD through {today}" if year == today.year else ""
        rows.append({"year": str(year), "dois_created": str(total), "note": note})
        time.sleep(1.5)
    print(f"crossref: {len(rows)} years, {rows[0]['year']}–{rows[-1]['year']}; "
          f"{int(rows[-1]['dois_created']) / 1e6:.2f}M in the last year")
    return rows


def build_stackoverflow() -> list[dict]:
    """Surviving questions by creation month, via the Stack Exchange API.

    The API counts questions that exist now, by creation date, so deleted
    questions vanish retroactively and older months are undercounts.
    """
    today = dt.date.today()
    rows = []
    year, month = 2019, 1
    while (year, month) < (today.year, today.month):  # full months only
        start = int(dt.datetime(year, month, 1,
                                tzinfo=dt.timezone.utc).timestamp())
        last = calendar.monthrange(year, month)[1]
        end = int(dt.datetime(year, month, last, 23, 59, 59,
                              tzinfo=dt.timezone.utc).timestamp())
        payload = json.loads(fetch(STACKEXCHANGE_URL.format(start=start, end=end)))
        rows.append({"month": f"{year}-{month:02d}",
                     "questions": str(payload["total"])})
        if payload.get("backoff"):
            time.sleep(payload["backoff"])
        time.sleep(0.3)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    print(f"stackoverflow: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"{rows[0]['questions']} → {rows[-1]['questions']} questions")
    return rows


def build_github() -> list[dict]:
    """Innovation Graph quarterly totals, summed over economies.

    GitHub publishes per-economy files rather than a global total. The EU row
    is an aggregate of member states and would double-count, so it is dropped;
    economies below the dataset's 100-developer reporting threshold are absent
    from the files altogether, so the sum slightly undercounts.
    """
    sums: dict[str, dict[str, int]] = {}
    for metric in ("git_pushes", "repositories", "developers"):
        raw = fetch(INNOVATIONGRAPH_URL.format(metric=metric)).decode("utf-8")
        for record in csv.DictReader(io.StringIO(raw)):
            if record.get("iso2") == "EU":
                continue
            quarter = f"{record['year']}-Q{record['quarter']}"
            sums.setdefault(quarter, {})
            sums[quarter][metric] = sums[quarter].get(metric, 0) + int(record[metric])
    note = ("sum over economies in github/innovationgraph data (EU aggregate row "
            "excluded); economies below 100-developer reporting threshold not included")
    rows = [{"quarter": quarter,
             "git_pushes": str(values.get("git_pushes", "")),
             "repositories": str(values.get("repositories", "")),
             "developers": str(values.get("developers", "")),
             "note": note}
            for quarter, values in sorted(sums.items())]
    print(f"github: {len(rows)} quarters, {rows[0]['quarter']}–{rows[-1]['quarter']}; "
          f"{int(rows[-1]['git_pushes']) / 1e6:.1f}M pushes in the last quarter")
    return rows


def main() -> None:
    write_csv(HERE / "arxiv-monthly.csv", build_arxiv())
    write_csv(HERE / "crossref-dois-by-year.csv", build_crossref())
    write_csv(HERE / "stackoverflow-questions-monthly.csv", build_stackoverflow())
    write_csv(HERE / "github-innovationgraph-global.csv", build_github())


if __name__ == "__main__":
    main()
