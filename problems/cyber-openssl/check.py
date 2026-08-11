#!/usr/bin/env python3
"""Check CVE-level provenance and every derived OpenSSL claim offline."""

from __future__ import annotations

import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from fetch import (  # noqa: E402
    ANNUAL_FIELDS,
    FINDER_FIELDS,
    METADATA_COMMIT,
    build_annual,
    build_finders,
)
from lib.table import read_csv  # noqa: E402


def normalized(rows: list[dict], fields: list[str]) -> list[dict[str, str]]:
    return [{field: str(row.get(field, "")) for field in fields} for row in rows]


def main() -> int:
    cves = read_csv(HERE / "openssl-cves.csv")
    annual = read_csv(HERE / "openssl-vulnerabilities.csv")
    finders = read_csv(HERE / "openssl-finders.csv")
    prose = re.sub(r"\s+", " ", (HERE / "README.md").read_text(encoding="utf-8"))
    failures: list[str] = []

    identifiers = [row["cve"] for row in cves]
    if len(identifiers) != len(set(identifiers)):
        duplicates = sorted(cve for cve, count in Counter(identifiers).items() if count > 1)
        failures.append(f"duplicate CVEs: {', '.join(duplicates)}")
    for row in cves:
        cve = row["cve"]
        try:
            date.fromisoformat(row["published"])
        except ValueError:
            failures.append(f"{cve} has invalid or missing publication date")
        for field in ("explicit_ai", "ai_affiliated", "fuzz"):
            if row[field] not in {"yes", "no"}:
                failures.append(f"{cve} has invalid {field}: {row[field]!r}")
        if row["explicit_ai"] == "yes" and not row["ai_evidence_url"].startswith("https://"):
            failures.append(f"{cve} is explicit_ai without an evidence URL")
        if row["explicit_ai"] == "no" and row["ai_evidence_url"]:
            failures.append(f"{cve} has AI evidence but explicit_ai=no")
        if row["metadata_commit"] != METADATA_COMMIT:
            failures.append(f"{cve} does not name the pinned metadata commit")
        if METADATA_COMMIT not in row["source_url"]:
            failures.append(f"{cve} source URL is not pinned")
        if not re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]):
            failures.append(f"{cve} has no source-record SHA-256")

    expected_annual = normalized(build_annual(cves), ANNUAL_FIELDS)
    if annual != expected_annual:
        failures.append("annual rows do not equal the CVE-level aggregation")
    expected_finders = normalized(build_finders(cves), FINDER_FIELDS)
    if finders != expected_finders:
        failures.append("finder rows do not equal the CVE-level aggregation")

    for row in annual:
        categories = sum(
            int(row[field])
            for field in (
                "corroborated_ai",
                "ai_affiliated_unverified",
                "conventional_or_fuzz",
                "unknown",
            )
        )
        if categories != int(row["total"]):
            failures.append(f"{row['year']} provenance bands do not sum to total")
    if sum(int(row["total"]) for row in annual) != len(cves):
        failures.append("annual totals do not sum to the CVE ledger")
    if sum(int(row["cves"]) for row in finders) != sum(
        bool(row["reporter"]) for row in cves
    ):
        failures.append("reporter aggregation does not match credited CVE rows")

    current = next(row for row in annual if row["year"] == "2026")
    claims = {
        "The largest pre-2026 totals were 35 in 2016 and 32 in 2015":
            "historical full-year peaks",
        f"{current['total']} by 5 August 2026": "current record",
        f"{current['total']} versus 27": "same-period comparison",
        f"{current['corroborated_ai']} have finding-level evidence of AI use":
            "corroborated AI count",
        f"{current['ai_affiliated_unverified']} more name an AI-security affiliation":
            "affiliation-only count",
        "12, 1, 7, 18 and 1 CVEs": "publication batches",
        "| Corroborated AI | 0 | 2 | 1 | 15 |": "corroborated severity row",
        "| AI-affiliated, method unverified | 0 | 0 | 3 | 6 |":
            "affiliation-only severity row",
        "| Conventional/fuzzing | 0 | 0 | 3 | 9 |":
            "conventional severity row",
    }
    for phrase, label in claims.items():
        if phrase not in prose:
            failures.append(f"README lacks recomputed {label}: {phrase!r}")

    for failure in failures:
        print(failure)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
