#!/usr/bin/env python3
"""Rebuild this folder's two CSVs from OpenSSL's own vulnerability index.

Run: python3 problems/cyber-openssl/fetch.py

OpenSSL publishes no machine-readable feed — the JSON and XML endpoints that once
existed both 404 — so this parses the HTML index at
https://openssl-library.org/news/vulnerabilities/, which lists a severity, a
publication date and a "Found by" credit per CVE. Two views come out of it:
annual counts split by credit, and one row per finder per year.

The parse is deliberately tolerant: severity is optional, because the older
entries do not all carry one, and any record without a parseable date is dropped
and counted so the coverage is visible.

AI attribution is by explicit marker in the credit (see lib/credits.py) and is
therefore a floor. OpenSSL is matched against ADVISORY_AI.
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import classify  # noqa: E402
from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://openssl-library.org/news/vulnerabilities/"

GAP = r"[|\s]+"
PATTERN = re.compile(
    r"(CVE-\d{4}-\d{4,7})"
    + r"(?:" + GAP + r"Severity" + GAP + r"([A-Za-z]+))?"
    + GAP + r"Published at" + GAP + r"(\d{1,2} [A-Z][a-z]+ \d{4})"
    + r"(?:" + GAP + r"Title" + GAP + r"[^|]{0,200})?"
    + r"(?:" + GAP + r"Found by" + GAP + r"([^|]{0,160}))?"
)


def records() -> tuple[list[dict], int]:
    """One record per dated CVE, plus the count of CVEs named anywhere on the page.

    Tags are replaced by a pipe rather than removed, so the pattern above can use
    the pipe as a field separator without depending on the page's markup.
    """
    text = html.unescape(re.sub(r"<[^>]+>", "|", fetch(URL).decode("utf-8", "replace")))
    seen: set = set()
    rows = []
    for match in PATTERN.finditer(text):
        cve = match.group(1)
        if cve in seen:
            continue
        seen.add(cve)
        rows.append(
            {
                "cve": cve,
                "year": int(match.group(3).split()[-1]),
                "finder": (match.group(4) or "").strip(),
            }
        )
    named = len(set(re.findall(r"CVE-\d{4}-\d{4,7}", text)))
    return rows, named


def build_annual(rows: list[dict], named: int) -> list[dict]:
    per_year: dict[int, Counter] = defaultdict(Counter)
    ai_names: Counter = Counter()
    for record in rows:
        bucket = per_year[record["year"]]
        bucket["total"] += 1
        category = classify(record["finder"])
        bucket[f"{category}_attributed"] += 1
        if category == "ai":
            ai_names[record["finder"][:70]] += 1
    this_year = datetime.now(timezone.utc).year
    annual = [
        {
            "year": year,
            "total": per_year[year]["total"],
            "ai_attributed": per_year[year]["ai_attributed"],
            "fuzz_attributed": per_year[year]["fuzz_attributed"],
            "other_attributed": per_year[year]["other_attributed"],
            "partial_year": "yes" if year == this_year else "no",
        }
        for year in sorted(per_year)
    ]
    print(
        f"openssl: {len(rows)} CVEs parsed with dates of {named} named on the "
        f"page, {annual[0]['year']}–{annual[-1]['year']}"
    )
    print(
        "  AI-credited finders: "
        + "; ".join(f"{c}x {n[:44]}" for n, c in ai_names.most_common(4))
    )
    return annual


def build_finders(rows: list[dict]) -> list[dict]:
    """One row per finder per year.

    Credit lines stay verbatim, multi-person ones included, because splitting
    them on commas would invent individual attributions.
    """
    counted: dict[tuple, int] = defaultdict(int)
    for record in rows:
        finder = record["finder"]
        if finder:
            counted[(record["year"], finder, classify(finder))] += 1
    out = [
        {"year": year, "finder": finder, "category": category, "cves": count}
        for (year, finder, category), count in sorted(
            counted.items(), key=lambda item: (item[0][0], -item[1])
        )
    ]
    ai = [row for row in out if row["category"] == "ai"]
    print(f"openssl finders: {len(out)} year-finder rows, {len(ai)} AI-credited")
    if ai:
        top = max(ai, key=lambda row: row["cves"])
        print(f"  top AI finder {top['cves']} CVEs — {top['finder'][:56]}")
    return out


def main() -> None:
    rows, named = records()
    write_csv(HERE / "openssl-vulnerabilities.csv", build_annual(rows, named))
    write_csv(HERE / "openssl-finders.csv", build_finders(rows))


if __name__ == "__main__":
    main()
