#!/usr/bin/env python3
"""Rebuild the OpenSSL CVE ledger and its derived CSVs.

Run:
    python3 problems/cyber-openssl/fetch.py
    python3 problems/cyber-openssl/fetch.py --check

The source is a pinned snapshot of OpenSSL's official release-metadata
repository. Each ``secjson/CVE-*.json`` file is a CVE 5 record containing the
publication date, OpenSSL severity, reporter and remediation credits, affected
versions, and references. Reporter and remediation credits are deliberately not
mixed.

AI method attribution is stricter than a company-name regex. ``explicit_ai`` is
true only when the official reporter wording names an AI system/method or a
separate, CVE-specific source says the finding came from an AI system.
``ai_affiliated`` and ``fuzz`` are independent textual signals.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import tarfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import (  # noqa: E402
    has_ai_affiliation,
    is_fuzz_credit,
    names_ai_method,
)
from lib.table import read_csv, write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

METADATA_COMMIT = "597a9a75044fb94b2823d111fd96ad9607a38189"
SNAPSHOT_DATE = date(2026, 8, 5)
ARCHIVE_URL = (
    "https://github.com/openssl/release-metadata/archive/"
    f"{METADATA_COMMIT}.tar.gz"
)
RAW_ROOT = (
    "https://raw.githubusercontent.com/openssl/release-metadata/"
    f"{METADATA_COMMIT}/secjson"
)

AISLE_2025_URL = (
    "https://aisle.com/blog/"
    "aisle-discovers-three-of-the-four-openssl-vulnerabilities-of-2025"
)
AISLE_JAN_2026_URL = (
    "https://aisle.com/blog/aisle-discovered-12-out-of-12-openssl-vulnerabilities"
)
AISLE_APR_2026_URL = (
    "https://aisle.com/blog/aisle-discovers-20-openssl-zero-days-in-6-months"
)

# These sources enumerate the CVEs, rather than merely saying that the credited
# researcher works at an AI lab.
AI_EVIDENCE = {
    **dict.fromkeys(
        ("CVE-2025-9230", "CVE-2025-9231", "CVE-2025-9232"),
        AISLE_2025_URL,
    ),
    **dict.fromkeys(
        (
            "CVE-2025-11187",
            "CVE-2025-15467",
            "CVE-2025-15468",
            "CVE-2025-15469",
            "CVE-2025-66199",
            "CVE-2025-68160",
            "CVE-2025-69418",
            "CVE-2025-69419",
            "CVE-2025-69420",
            "CVE-2025-69421",
            "CVE-2026-22795",
            "CVE-2026-22796",
        ),
        AISLE_JAN_2026_URL,
    ),
    **dict.fromkeys(
        (
            "CVE-2026-28386",
            "CVE-2026-28387",
            "CVE-2026-28388",
            "CVE-2026-28389",
            "CVE-2026-28390",
        ),
        AISLE_APR_2026_URL,
    ),
}

CVE_FIELDS = [
    "cve",
    "published",
    "severity",
    "reporter",
    "explicit_ai",
    "ai_affiliated",
    "ai_evidence_url",
    "fuzz",
    "affected_versions",
    "source_discovery",
    "source_url",
    "source_sha256",
    "metadata_commit",
]
ANNUAL_FIELDS = [
    "year",
    "total",
    "corroborated_ai",
    "ai_affiliated_unverified",
    "conventional_or_fuzz",
    "unknown",
    "fuzz",
    "comparable_through_aug_05",
    "partial_year",
    "data_through",
]
FINDER_FIELDS = [
    "year",
    "finder",
    "explicit_ai",
    "ai_affiliated",
    "fuzz",
    "ai_evidence_url",
    "cves",
]


def _severity(cna: dict) -> str:
    values = [
        metric.get("other", {}).get("content", {}).get("text", "")
        for metric in cna.get("metrics", [])
    ]
    values = [value.strip().title() for value in values if value.strip()]
    if len(set(values)) != 1:
        raise ValueError(f"expected one OpenSSL severity, got {values!r}")
    return values[0]


def _reporter(cna: dict) -> str:
    values = [
        credit["value"].strip()
        for credit in cna.get("credits", [])
        if credit.get("type", "").lower() in {"finder", "reporter"}
        and credit.get("value", "").strip()
    ]
    return "; ".join(values)


def _affected_versions(cna: dict) -> str:
    ranges = []
    for product in cna.get("affected", []):
        for version in product.get("versions", []):
            if version.get("status") != "affected":
                continue
            lower = version.get("version", "").strip()
            upper = version.get("lessThan", "").strip()
            if lower and upper:
                ranges.append(f"{lower} to <{upper}")
            elif lower:
                ranges.append(lower)
    return "; ".join(dict.fromkeys(ranges))


def _archive_records(raw: bytes) -> list[tuple[str, bytes]]:
    out = []
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if name.parent.name != "secjson" or not name.name.startswith("CVE-"):
                continue
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"could not read {member.name}")
            out.append((name.name, handle.read()))
    if not out:
        raise ValueError("metadata archive contains no secjson CVE records")
    return sorted(out)


def records(raw: bytes | None = None) -> list[dict]:
    """Extract one auditable row per CVE from the pinned official snapshot."""
    source = fetch(ARCHIVE_URL) if raw is None else raw
    rows = []
    for filename, payload in _archive_records(source):
        record = json.loads(payload)
        cna = record["containers"]["cna"]
        cve = record["cveMetadata"]["cveId"]
        if filename != f"{cve}.json":
            raise ValueError(f"{filename} contains {cve}")
        published = cna.get("datePublic", "")[:10]
        if not published:
            raise ValueError(f"{cve} has no datePublic")
        reporter = _reporter(cna)
        year = int(published[:4])
        source_url = f"{RAW_ROOT}/{filename}"
        evidence_url = AI_EVIDENCE.get(cve, "")
        if names_ai_method(reporter, year):
            # The official reporter wording itself can provide method evidence,
            # e.g. "in collaboration with Claude", unlike a bare affiliation.
            evidence_url = evidence_url or source_url
        rows.append(
            {
                "cve": cve,
                "published": published,
                "severity": _severity(cna),
                "reporter": reporter,
                "explicit_ai": "yes" if evidence_url else "no",
                "ai_affiliated": "yes" if has_ai_affiliation(reporter) else "no",
                "ai_evidence_url": evidence_url,
                "fuzz": "yes" if is_fuzz_credit(reporter) else "no",
                "affected_versions": _affected_versions(cna),
                "source_discovery": cna.get("source", {}).get("discovery", ""),
                "source_url": source_url,
                "source_sha256": hashlib.sha256(payload).hexdigest(),
                "metadata_commit": METADATA_COMMIT,
            }
        )
    return sorted(rows, key=lambda row: (row["published"], row["cve"]))


def finder_class(row: dict) -> str:
    """Return the mutually exclusive chart band for a CVE row."""
    if row["explicit_ai"] == "yes":
        return "corroborated_ai"
    if row["ai_affiliated"] == "yes":
        return "ai_affiliated_unverified"
    if row["reporter"]:
        return "conventional_or_fuzz"
    return "unknown"


def build_annual(rows: list[dict]) -> list[dict]:
    per_year: dict[int, Counter] = defaultdict(Counter)
    through = SNAPSHOT_DATE.strftime("%m-%d")
    for row in rows:
        year = int(row["published"][:4])
        bucket = per_year[year]
        bucket["total"] += 1
        bucket[finder_class(row)] += 1
        bucket["fuzz"] += row["fuzz"] == "yes"
        bucket["comparable"] += row["published"][5:] <= through
    latest = max(row["published"] for row in rows)
    latest_year = int(latest[:4])
    return [
        {
            "year": year,
            "total": per_year[year]["total"],
            "corroborated_ai": per_year[year]["corroborated_ai"],
            "ai_affiliated_unverified": per_year[year]["ai_affiliated_unverified"],
            "conventional_or_fuzz": per_year[year]["conventional_or_fuzz"],
            "unknown": per_year[year]["unknown"],
            "fuzz": per_year[year]["fuzz"],
            "comparable_through_aug_05": per_year[year]["comparable"],
            "partial_year": "yes" if year == latest_year else "no",
            "data_through": latest if year == latest_year else "",
        }
        for year in sorted(per_year)
    ]


def build_finders(rows: list[dict]) -> list[dict]:
    """Aggregate identical reporter strings without splitting joint credits."""
    counted: dict[tuple, int] = defaultdict(int)
    for row in rows:
        if not row["reporter"]:
            continue
        key = (
            row["published"][:4],
            row["reporter"],
            row["explicit_ai"],
            row["ai_affiliated"],
            row["fuzz"],
            row["ai_evidence_url"],
        )
        counted[key] += 1
    return [
        {
            "year": year,
            "finder": finder,
            "explicit_ai": explicit_ai,
            "ai_affiliated": ai_affiliated,
            "fuzz": fuzz,
            "ai_evidence_url": evidence_url,
            "cves": count,
        }
        for (
            year,
            finder,
            explicit_ai,
            ai_affiliated,
            fuzz,
            evidence_url,
        ), count in sorted(counted.items(), key=lambda item: (item[0][0], -item[1]))
    ]


def outputs(rows: list[dict]) -> dict[str, tuple[list[dict], list[str]]]:
    return {
        "openssl-cves.csv": (rows, CVE_FIELDS),
        "openssl-by-year.csv": (build_annual(rows), ANNUAL_FIELDS),
        "openssl-finders.csv": (build_finders(rows), FINDER_FIELDS),
    }


def check_vendored(expected: dict[str, tuple[list[dict], list[str]]]) -> int:
    failures = []
    for name, (rows, fields) in expected.items():
        actual = read_csv(HERE / name)
        normalized = [
            {field: str(row.get(field, "")) for field in fields}
            for row in rows
        ]
        if actual != normalized:
            failures.append(name)
    if failures:
        print("pinned metadata differs from " + ", ".join(failures))
        return 1
    print(f"all CSVs match OpenSSL metadata commit {METADATA_COMMIT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="download the pinned snapshot and compare without rewriting",
    )
    args = parser.parse_args()
    rows = records()
    built = outputs(rows)
    if args.check:
        return check_vendored(built)
    for name, (output_rows, fields) in built.items():
        write_csv(HERE / name, output_rows, fields)
    print(
        f"openssl: {len(rows)} CVEs, {rows[0]['published']}–"
        f"{rows[-1]['published']}, metadata {METADATA_COMMIT[:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
