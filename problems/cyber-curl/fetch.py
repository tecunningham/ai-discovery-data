#!/usr/bin/env python3
"""Rebuild this folder's three CSVs from curl's own vulnerability record.

Run: python3 problems/cyber-curl/fetch.py

https://curl.se/docs/vuln.json is the project's OSV-format record of every CVE,
carrying a `published` date, a `credits` list naming finders, and a severity.
Three views come out of it: annual counts with the severity mix, quarterly counts
without it, and one row per finder per year.

Quarterly exists because curl publishes in batches at releases, so a quarter is
about the finest grain at which the series is not just release timing. Severity
is left off it: at three to twelve issues a quarter the mix is sampling noise.

AI attribution is by explicit marker in a finder credit (see lib/credits.py) and
is therefore a floor. curl is matched against the narrower CURL_AI list.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import CURL_AI, SEVERITIES, classify  # noqa: E402
from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://curl.se/docs/vuln.json"


def entries() -> list[dict]:
    return [
        entry
        for entry in json.loads(fetch(URL))
        if (entry.get("published") or "")[:4].isdigit()
    ]


def finders(entry: dict) -> list[str]:
    return [c["name"] for c in entry.get("credits", []) if c.get("type") == "FINDER"]


def build_annual(records: list[dict]) -> list[dict]:
    per_year: dict[int, Counter] = defaultdict(Counter)
    latest = ""
    for entry in records:
        published = entry["published"]
        year = int(published[:4])
        latest = max(latest, published[:10])
        is_ai = any(CURL_AI.search(name) for name in finders(entry))
        severity = (entry.get("database_specific") or {}).get("severity", "unknown")
        bucket = per_year[year]
        bucket["total"] += 1
        bucket["ai_attributed" if is_ai else "other_attributed"] += 1
        bucket[f"sev_{severity}"] += 1
        bucket[("ai_sev_" if is_ai else "other_sev_") + severity] += 1

    rows = []
    for year in sorted(per_year):
        bucket = per_year[year]
        row = {
            "year": year,
            "total": bucket["total"],
            "ai_attributed": bucket["ai_attributed"],
            "other_attributed": bucket["other_attributed"],
        }
        for severity in SEVERITIES:
            row[f"sev_{severity.lower()}"] = bucket[f"sev_{severity}"]
            row[f"ai_sev_{severity.lower()}"] = bucket[f"ai_sev_{severity}"]
            row[f"other_sev_{severity.lower()}"] = bucket[f"other_sev_{severity}"]
        row["partial_year"] = "yes" if year == int(latest[:4]) else "no"
        row["data_through"] = latest if year == int(latest[:4]) else ""
        rows.append(row)
    print(
        f"curl: {sum(r['total'] for r in rows)} CVEs, "
        f"{rows[0]['year']}–{rows[-1]['year']}, latest {latest}"
    )
    print(
        "  AI-attributed by year: "
        + ", ".join(
            f"{r['year']}:{r['ai_attributed']}/{r['total']}"
            for r in rows
            if r["ai_attributed"]
        )
    )
    return rows


def build_quarterly(records: list[dict]) -> list[dict]:
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for entry in records:
        published = entry["published"]
        year, month = int(published[:4]), int(published[5:7])
        bucket = per_quarter[f"{year}-Q{(month - 1) // 3 + 1}"]
        bucket["total"] += 1
        is_ai = any(CURL_AI.search(name) for name in finders(entry))
        bucket["ai_attributed" if is_ai else "other_attributed"] += 1
    rows = [
        {
            "quarter": quarter,
            "total": per_quarter[quarter]["total"],
            "ai_attributed": per_quarter[quarter]["ai_attributed"],
            "other_attributed": per_quarter[quarter]["other_attributed"],
        }
        for quarter in sorted(per_quarter)
    ]
    print(
        f"curl quarterly: {len(rows)} non-empty quarters, "
        f"{rows[0]['quarter']}–{rows[-1]['quarter']}"
    )
    return rows


def build_finders(records: list[dict]) -> list[dict]:
    """One row per finder per year.

    Finder strings stay verbatim, multi-person credit lines included, because
    splitting them on commas would invent individual attributions.
    """
    counted: dict[tuple, int] = defaultdict(int)
    for entry in records:
        year = int(entry["published"][:4])
        for name in finders(entry):
            counted[(year, name, classify(name))] += 1
    rows = [
        {"year": year, "finder": name, "category": category, "cves": count}
        for (year, name, category), count in sorted(
            counted.items(), key=lambda item: (item[0][0], -item[1])
        )
    ]
    ai = [row for row in rows if row["category"] == "ai"]
    print(f"curl finders: {len(rows)} year-finder rows, {len(ai)} AI-credited")
    if ai:
        top = max(ai, key=lambda row: row["cves"])
        print(f"  top AI finder {top['cves']} CVEs — {top['finder'][:56]}")
    return rows


def main() -> None:
    records = entries()
    write_csv(HERE / "curl-vulnerabilities.csv", build_annual(records))
    write_csv(HERE / "curl-vulnerabilities-quarterly.csv", build_quarterly(records))
    write_csv(HERE / "curl-finders.csv", build_finders(records))


if __name__ == "__main__":
    main()
