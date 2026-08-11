#!/usr/bin/env python3
"""Rebuild this folder's CSV from OSV's full database export.

Run: python3 problems/cyber-osv-cves/fetch.py

The export contains multiple advisory records for many vulnerabilities, notably
one record per Linux distribution. This series therefore counts distinct CVE
identifiers, not OSV records. A CVE is included when at least one non-withdrawn
OSV record links it to an affected package, and is dated to the earliest
``published`` date among those records.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402

URL = "https://storage.googleapis.com/osv-vulnerabilities/all.zip"
FIRST_YEAR = 2016
CVE = re.compile(r"CVE-\d{4}-\d{4,}")


def download(path: Path) -> None:
    """Stream the large official export to disk instead of holding it in RAM."""
    result = subprocess.run(
        [
            "curl",
            "--fail",
            "--silent",
            "--show-error",
            "--location",
            "--retry",
            "4",
            "--max-time",
            "300",
            "--output",
            str(path),
            URL,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip()
        raise SystemExit(
            f"failed to fetch {URL}" + (f": {detail}" if detail else "")
        )


def build_annual(archive_path: Path) -> list[dict]:
    """Count each active, affected CVE once at its earliest OSV publication."""
    first_published: dict[str, date] = {}
    linked_records = 0

    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            record = json.loads(archive.read(name))
            if record.get("withdrawn") or not record.get("affected"):
                continue
            try:
                published = date.fromisoformat((record.get("published") or "")[:10])
            except ValueError:
                continue

            cves = {
                identifier
                for identifier in [
                    record.get("id") or "",
                    *(record.get("aliases") or []),
                ]
                if CVE.fullmatch(identifier)
            }
            if not cves:
                continue
            linked_records += 1
            for cve in cves:
                current = first_published.get(cve)
                if current is None or published < current:
                    first_published[cve] = published

    counts = Counter(day.year for day in first_published.values())
    latest = max(first_published.values())
    rows = [
        {
            "year": year,
            "distinct_cves": counts[year],
            "partial_year": "yes" if year == latest.year else "no",
            "data_through": latest.isoformat() if year == latest.year else "",
        }
        for year in range(FIRST_YEAR, latest.year + 1)
    ]
    print(
        f"osv: {len(first_published)} distinct affected CVEs from "
        f"{linked_records} active linked records; charting {FIRST_YEAR}–{latest.year}"
    )
    return rows


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="osv-export-") as temporary:
        archive_path = Path(temporary) / "all.zip"
        download(archive_path)
        write_csv(HERE / "osv-cves-by-year.csv", build_annual(archive_path))


if __name__ == "__main__":
    main()
