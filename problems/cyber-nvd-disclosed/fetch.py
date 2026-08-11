#!/usr/bin/env python3
"""Rebuild this folder's two CSVs from the NVD API.

Run: python3 problems/cyber-nvd-disclosed/fetch.py

Every CVE published in the US National Vulnerability Database, counted by
publication year and by quarter. This is the aggregate the press reporting on the
2026 numbers rests on, vendored so its arithmetic can be checked.

NVD caps a query window at 120 days and rate-limits unkeyed callers to five
requests per thirty seconds, so each year is fetched as four quarterly windows
with a pause between calls, and `totalResults` is read rather than the records
themselves. lib/web.py backs off on the HTML error pages the API returns over
quota, and caches replies for the day.

The exploited-vulnerability counterweight is a separate folder, so this fetcher
touches only NVD; see ../cyber-kev-exploited/fetch.py for the CISA feed.
"""

from __future__ import annotations

import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch_json  # noqa: E402

API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
FIRST_YEAR = 2016


def build(first_year: int = FIRST_YEAR) -> tuple[list[dict], list[dict]]:
    snapshot = datetime.now(timezone.utc)
    today = snapshot.date()
    per_year: dict[int, int] = {}
    per_quarter: dict[str, int] = {}
    for year in range(first_year, today.year + 1):
        edges = [
            f"{year}-01-01",
            f"{year}-04-01",
            f"{year}-07-01",
            f"{year}-10-01",
            f"{year + 1}-01-01",
        ]
        total = 0
        for start, end in zip(edges, edges[1:]):
            start_at = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
            if start_at > snapshot:
                break
            # NVD treats both endpoints as inclusive. End one millisecond before
            # the next quarter so a boundary timestamp cannot be counted twice.
            end_at = min(
                datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
                - timedelta(milliseconds=1),
                snapshot,
            )
            params = urllib.parse.urlencode(
                {
                    "resultsPerPage": 1,
                    "pubStartDate": start_at.isoformat(timespec="milliseconds"),
                    "pubEndDate": end_at.isoformat(timespec="milliseconds"),
                }
            )
            count = int(fetch_json(f"{API}?{params}").get("totalResults", 0))
            total += count
            quarter = (datetime.fromisoformat(start).month - 1) // 3 + 1
            per_quarter[f"{year}-Q{quarter}"] = count
            time.sleep(8.0)  # unkeyed NVD allows 5 requests per 30 seconds
        per_year[year] = total
        print(f"  NVD {year}: {total}")

    rows = [
        {
            "year": year,
            "nvd_published": per_year[year],
            "partial_year": "yes" if year == today.year else "no",
            "data_through": today.isoformat() if year == today.year else "",
        }
        for year in sorted(per_year)
    ]
    # The final quarter is incomplete; flag it rather than letting it read as a dip.
    current_q = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
    qrows = [
        {
            "quarter": quarter,
            "nvd_published": per_quarter[quarter],
            "partial_quarter": "yes" if quarter == current_q else "no",
            "data_through": today.isoformat() if quarter == current_q else "",
        }
        for quarter in sorted(per_quarter)
    ]
    print(
        f"  quarterly: {len(qrows)} quarters, {qrows[0]['quarter']}–{qrows[-1]['quarter']}"
        f" (final one partial through {today.isoformat()})"
    )
    return rows, qrows


def main() -> None:
    rows, qrows = build()
    write_csv(HERE / "nvd-by-year.csv", rows)
    write_csv(HERE / "nvd-by-quarter.csv", qrows)


if __name__ == "__main__":
    main()
