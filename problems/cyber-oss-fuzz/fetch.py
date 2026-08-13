#!/usr/bin/env python3
"""Rebuild this folder's CSV from OSV's OSS-Fuzz archive.

Run: python3 problems/cyber-oss-fuzz/fetch.py

This is the automated-but-not-AI baseline: a decade of continuous fuzzing over
hundreds of open-source projects, every finding published as a dated OSV record.

The year is taken from the OSV *id* (OSV-YYYY-N), not from `published`, because
records predating 2020 were backfilled into OSV in 2021 and their published dates
all land in that year. The two agree from 2020 onward, so the series is reported
from 2020 and the earlier records are dropped and counted; the quarterly view
buckets the same records by their published date, which is trustworthy in that
range. Records published after lib/chart.py's AS_OF_DATE are dropped, so a
refetch reproduces the committed window.
"""

from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://osv-vulnerabilities.storage.googleapis.com/OSS-Fuzz/all.zip"


def as_of_date() -> date:
    """The repository's committed snapshot date, read from lib/chart.py.

    Parsed rather than imported so a fetch does not pull in matplotlib; the
    same regex tools/check.py uses to enforce the date against every CSV.
    """
    text = (HERE.parents[1] / "lib/chart.py").read_text(encoding="utf-8")
    match = re.search(
        r"^AS_OF_DATE\s*=\s*date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)", text, re.M
    )
    if not match:
        raise SystemExit("lib/chart.py has no parseable AS_OF_DATE")
    return date(*(int(part) for part in match.groups()))


def collect() -> tuple[Counter, Counter, int]:
    """Record counts by id-year and by published quarter, through the snapshot."""
    cutoff = as_of_date()
    by_id: Counter = Counter()
    by_quarter: Counter = Counter()
    dropped_late = 0
    with zipfile.ZipFile(io.BytesIO(fetch(URL))) as archive:
        for name in archive.namelist():
            match = re.match(r"OSV-(\d{4})-", name)
            if not match:
                continue
            record = json.loads(archive.read(name))
            try:
                published = date.fromisoformat(
                    (record.get("published") or "")[:10])
            except ValueError:
                published = None
            if published and published > cutoff:
                dropped_late += 1
                continue
            by_id[match.group(1)] += 1
            if int(match.group(1)) >= 2020 and published:
                by_quarter[
                    f"{published.year}-Q{(published.month + 2) // 3}"
                ] += 1
    return by_id, by_quarter, dropped_late


def build_annual(by_id: Counter, cutoff: date) -> list[dict]:
    rows = [
        {
            "year": int(year),
            "discoveries": by_id[year],
            "partial_year": "yes" if int(year) == cutoff.year else "no",
            "data_through": cutoff.isoformat() if int(year) == cutoff.year else "",
        }
        for year in sorted(by_id)
        if int(year) >= 2020
    ]
    dropped = sum(count for year, count in by_id.items() if int(year) < 2020)
    print(
        f"oss-fuzz: {sum(r['discoveries'] for r in rows)} records 2020 onward "
        f"({dropped} earlier ones dropped as backfilled)"
    )
    return rows


def build_quarterly(by_quarter: Counter, cutoff: date) -> list[dict]:
    last = max(by_quarter)
    return [
        {
            "quarter": quarter,
            "discoveries": by_quarter[quarter],
            "partial_quarter": "yes" if quarter == last else "no",
            "data_through": cutoff.isoformat() if quarter == last else "",
        }
        for quarter in sorted(by_quarter)
    ]


def main() -> None:
    by_id, by_quarter, dropped_late = collect()
    if dropped_late:
        print(f"oss-fuzz: {dropped_late} records past the snapshot date dropped")
    cutoff = as_of_date()
    write_csv(HERE / "ossfuzz-discoveries.csv", build_annual(by_id, cutoff))
    write_csv(HERE / "ossfuzz-by-quarter.csv", build_quarterly(by_quarter, cutoff))


if __name__ == "__main__":
    main()
