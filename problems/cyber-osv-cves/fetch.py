#!/usr/bin/env python3
"""Rebuild this folder's CSVs from OSV's full database export.

Run: python3 problems/cyber-osv-cves/fetch.py

The export contains multiple advisory records for many vulnerabilities, notably
one record per Linux distribution. This series therefore counts distinct CVE
identifiers, not OSV records. A CVE is included when at least one non-withdrawn
OSV record links it to an affected package, and is dated to the earliest
``published`` date among those records; CVEs first published after
lib/chart.py's AS_OF_DATE are dropped so a refetch reproduces the committed
window.

Severity and finder credits are unioned across a CVE's records. Severity is the
`database_specific.severity` label an ecosystem database assigns (GHSA-style
LOW/MODERATE/HIGH/CRITICAL, with MEDIUM folded into Moderate); many records
carry only a CVSS vector or nothing, and those CVEs stay Unrated rather than
being scored by a calculator this repository would then have to defend. Credits
are OSV `credits` names, classified with lib/credits.py; a CVE with no credit
on any record is uncredited, which is the majority and is its own column.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import Signals, signals  # noqa: E402
from lib.table import write_csv  # noqa: E402

URL = "https://storage.googleapis.com/osv-vulnerabilities/all.zip"
FIRST_YEAR = 2016
CVE = re.compile(r"CVE-\d{4}-\d{4,}")

# Ecosystem severity labels, mildest first. MEDIUM and MODERATE are the same
# rung under two names (GHSA says MODERATE, several distros say MEDIUM).
SEVERITIES = ["Low", "Moderate", "High", "Critical"]
SEVERITY_ALIASES = {"LOW": "Low", "MODERATE": "Moderate", "MEDIUM": "Moderate",
                    "HIGH": "High", "CRITICAL": "Critical"}


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


def severity_rank(label: str) -> int:
    return SEVERITIES.index(label) if label in SEVERITIES else -1


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


def collect(archive_path: Path) -> dict[str, dict]:
    """One merged entry per active, affected CVE across all its OSV records."""
    cves: dict[str, dict] = {}
    linked_records = 0
    cutoff = as_of_date()

    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            record = json.loads(archive.read(name))
            if record.get("withdrawn") or not record.get("affected"):
                continue
            try:
                published = date.fromisoformat((record.get("published") or "")[:10])
            except ValueError:
                continue

            ids = {
                identifier
                for identifier in [
                    record.get("id") or "",
                    *(record.get("aliases") or []),
                ]
                if CVE.fullmatch(identifier)
            }
            if not ids:
                continue
            linked_records += 1
            raw = str((record.get("database_specific") or {})
                      .get("severity") or "").strip().upper()
            severity = SEVERITY_ALIASES.get(raw, "")
            names = [str(credit.get("name") or "").strip()
                     for credit in record.get("credits") or []]
            names = [name for name in names if name]
            for cve in ids:
                entry = cves.setdefault(cve, {
                    "published": published,
                    "severity": "",
                    "credits": [],
                })
                entry["published"] = min(entry["published"], published)
                if severity_rank(severity) > severity_rank(entry["severity"]):
                    entry["severity"] = severity
                for name in names:
                    if name not in entry["credits"]:
                        entry["credits"].append(name)

    kept = {cve: entry for cve, entry in cves.items()
            if entry["published"] <= cutoff}
    print(
        f"osv: {len(kept)} distinct affected CVEs from {linked_records} active "
        f"linked records ({len(cves) - len(kept)} past {cutoff.isoformat()} "
        "dropped)"
    )
    return kept


def banded(entry: dict, year: int) -> Signals:
    """Union the credit signals across every name on a CVE's records."""
    marks = Signals(explicit_ai=False, ai_affiliated=False, fuzz=False)
    for name in entry["credits"]:
        found = signals(name, year)
        marks = Signals(
            explicit_ai=marks.explicit_ai or found.explicit_ai,
            ai_affiliated=marks.ai_affiliated or found.ai_affiliated,
            fuzz=marks.fuzz or found.fuzz,
        )
    return marks


def build_annual(cves: dict[str, dict]) -> list[dict]:
    counts = Counter(entry["published"].year for entry in cves.values())
    latest = max(entry["published"] for entry in cves.values())
    return [
        {
            "year": year,
            "distinct_cves": counts[year],
            "partial_year": "yes" if year == latest.year else "no",
            "data_through": latest.isoformat() if year == latest.year else "",
        }
        for year in range(FIRST_YEAR, latest.year + 1)
    ]


def build_quarterly(cves: dict[str, dict]) -> list[dict]:
    per_quarter = Counter(
        f"{entry['published'].year}-Q{(entry['published'].month + 2) // 3}"
        for entry in cves.values()
        if entry["published"].year >= FIRST_YEAR
    )
    latest = max(entry["published"] for entry in cves.values())
    last_quarter = max(per_quarter)
    return [
        {
            "quarter": quarter,
            "distinct_cves": per_quarter[quarter],
            "partial_quarter": "yes" if quarter == last_quarter else "no",
            "data_through": latest.isoformat() if quarter == last_quarter else "",
        }
        for quarter in sorted(per_quarter)
    ]


def build_severity(cves: dict[str, dict]) -> list[dict]:
    per_year: dict[int, Counter] = defaultdict(Counter)
    for entry in cves.values():
        year = entry["published"].year
        if year < FIRST_YEAR:
            continue
        per_year[year][entry["severity"] or "Unrated"] += 1
    rows = [
        {
            "year": year,
            **{label.lower(): per_year[year][label] for label in SEVERITIES},
            "unrated": per_year[year]["Unrated"],
        }
        for year in sorted(per_year)
    ]
    rated = sum(sum(row[label.lower()] for label in SEVERITIES) for row in rows)
    total = rated + sum(row["unrated"] for row in rows)
    print(f"osv severity: {rated} of {total} CVEs carry an ecosystem "
          f"severity label ({100 * rated / total:.0f}%)")
    return rows


def build_credits(cves: dict[str, dict]) -> list[dict]:
    per_year: dict[int, Counter] = defaultdict(Counter)
    for entry in cves.values():
        year = entry["published"].year
        if year < FIRST_YEAR:
            continue
        bucket = per_year[year]
        bucket["distinct_cves"] += 1
        if not entry["credits"]:
            bucket["uncredited"] += 1
            continue
        bucket[banded(entry, year).band] += 1
    rows = [
        {
            "year": year,
            "distinct_cves": per_year[year]["distinct_cves"],
            "explicit_ai": per_year[year]["explicit_ai"],
            "ai_affiliated": per_year[year]["ai_affiliated"],
            "fuzz": per_year[year]["fuzz"],
            "other_credited": per_year[year]["other"],
            "uncredited": per_year[year]["uncredited"],
        }
        for year in sorted(per_year)
    ]
    credited = sum(row["distinct_cves"] - row["uncredited"] for row in rows)
    total = sum(row["distinct_cves"] for row in rows)
    print(f"osv credits: {credited} of {total} CVEs carry any credit "
          f"({100 * credited / total:.0f}%)")
    return rows


def build_ai_cves(cves: dict[str, dict]) -> list[dict]:
    """One row per AI-marked CVE, with the credit names kept as evidence.

    The same role firefox-ai-cves.csv and msrc-ai-cves.csv play: the annual
    counts collapse CVEs into bands, and this is the only vendored place a
    per-credit claim can be recomputed from.
    """
    out = []
    for cve, entry in sorted(cves.items(),
                             key=lambda item: (item[1]["published"], item[0])):
        year = entry["published"].year
        if year < FIRST_YEAR:
            continue
        marks = banded(entry, year)
        if not marks.any_ai_marker:
            continue
        out.append({
            "cve": cve,
            "date": entry["published"].isoformat(),
            "band": marks.band,
            "credits": " | ".join(entry["credits"]),
        })
    print(f"osv AI-marked distinct CVEs: {len(out)} rows")
    return out


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="osv-export-") as temporary:
        archive_path = Path(temporary) / "all.zip"
        download(archive_path)
        cves = collect(archive_path)
    write_csv(HERE / "osv-cves-by-year.csv", build_annual(cves))
    write_csv(HERE / "osv-cves-by-quarter.csv", build_quarterly(cves))
    write_csv(HERE / "osv-severity-by-year.csv", build_severity(cves))
    write_csv(HERE / "osv-credits-by-year.csv", build_credits(cves))
    write_csv(HERE / "osv-ai-cves.csv", build_ai_cves(cves))


if __name__ == "__main__":
    main()
