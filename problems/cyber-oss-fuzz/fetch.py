#!/usr/bin/env python3
"""Rebuild this folder's CSV from OSV's OSS-Fuzz archive.

Run: python3 problems/cyber-oss-fuzz/fetch.py

This is the automated-but-not-AI baseline: a decade of continuous fuzzing over
hundreds of open-source projects, every finding published as a dated OSV record.

The year is taken from the OSV *id* (OSV-YYYY-N), not from `published`, because
records predating 2020 were backfilled into OSV in 2021 and their published dates
all land in that year. The two agree from 2020 onward, so the series is reported
from 2020 and the earlier records are dropped and counted.
"""

from __future__ import annotations

import io
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://osv-vulnerabilities.storage.googleapis.com/OSS-Fuzz/all.zip"


def build_annual() -> list[dict]:
    by_id: Counter = Counter()
    with zipfile.ZipFile(io.BytesIO(fetch(URL))) as archive:
        for name in archive.namelist():
            match = re.match(r"OSV-(\d{4})-", name)
            if match:
                by_id[match.group(1)] += 1
    this_year = datetime.now(timezone.utc).year
    rows = [
        {
            "year": int(year),
            "discoveries": by_id[year],
            "partial_year": "yes" if int(year) == this_year else "no",
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


def main() -> None:
    write_csv(HERE / "ossfuzz-discoveries.csv", build_annual())


if __name__ == "__main__":
    main()
