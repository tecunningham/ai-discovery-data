#!/usr/bin/env python3
"""Rebuild this folder's two CSVs from Mozilla's security-advisory repository.

Run: python3 problems/cyber-firefox/fetch.py

Mozilla publishes one YAML file per advisory under announce/, with a `reporter`
string against each CVE, which makes Firefox a fixed codebase with named finders.
Counts are by the advisory's `announced` year. Pre-2016 advisories do not list
CVEs in this structure, so the series starts there. Two views come out of the
repository: annual counts split by credit, and one row per reporter per year.

The plotted unit is the distinct CVE. Mozilla repeats one CVE across the Firefox,
Firefox ESR and Thunderbird advisories of a release, so a mention count moves
with Mozilla's packaging as well as with discovery; mention counts are kept as a
sensitivity column rather than as the headline.

AI attribution is by explicit marker in the reporter string (see lib/credits.py),
which separates a named AI method from a bare AI-company affiliation and carries
error in both directions. Fuzz is an independent signal, not a rival category.

Requires PyYAML.
"""

from __future__ import annotations

import io
import re
import sys
import tarfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import Signals, band, classify, signals  # noqa: E402
from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

# codeload's /tar.gz/<branch> form 404s for this repo; the archive URL works.
URL = (
    "https://github.com/mozilla/foundation-security-advisories/"
    "archive/refs/heads/master.tar.gz"
)


def records() -> list[dict]:
    """One record per CVE named in an advisory, carrying its year and reporter."""
    import yaml

    rows = []
    with tarfile.open(fileobj=io.BytesIO(fetch(URL)), mode="r:gz") as tar:
        for member in tar.getmembers():
            if "/announce/" not in member.name or not member.name.endswith(".yml"):
                continue
            handle = tar.extractfile(member)
            if handle is None:
                continue
            text = handle.read().decode("utf-8", "replace")
            announced = re.search(r"^announced:\s*.*?(20\d{2})", text, re.M | re.S)
            if announced:
                year = int(announced.group(1))
            else:
                fallback = re.search(r"mfsa(20\d{2})", member.name)
                if not fallback:
                    continue
                year = int(fallback.group(1))
            try:
                parsed = yaml.safe_load(text) or {}
            except Exception:
                continue
            announced_text = str(parsed.get("announced") or "")
            try:
                announced_date = datetime.strptime(
                    announced_text, "%B %d, %Y"
                ).date().isoformat()
            except ValueError:
                announced_date = ""
            for key, value in (parsed.get("advisories") or {}).items():
                if not str(key).startswith("CVE"):
                    continue
                reporter = (
                    str(value.get("reporter", "")) if isinstance(value, dict) else ""
                )
                rows.append({
                    "year": year,
                    "announced": announced_date,
                    "cve": str(key),
                    "reporter": reporter,
                })
    return rows


def build_annual(rows: list[dict]) -> list[dict]:
    """Annual counts of distinct CVEs by band, with mention counts alongside.

    A CVE repeated across a release's advisories is one discovery, so the band
    columns count distinct CVE IDs. Where the same CVE carries different reporter
    strings in different advisories, its signals are unioned across that year's
    mentions before the display precedence is applied — otherwise which advisory
    happened to be read last would decide the band.
    """
    per_year: dict[int, Counter] = defaultdict(Counter)
    unique_cves: dict[int, set[str]] = defaultdict(set)
    unique_ai_cves: dict[int, set[str]] = defaultdict(set)
    cve_signals: dict[tuple[int, str], Signals] = {}
    ai_reporters: Counter = Counter()
    for record in rows:
        year = record["year"]
        bucket = per_year[year]
        bucket["total"] += 1
        unique_cves[year].add(record["cve"])
        marks = signals(record["reporter"], year)
        key = (year, record["cve"])
        seen = cve_signals.get(key)
        cve_signals[key] = marks if seen is None else Signals(
            explicit_ai=seen.explicit_ai or marks.explicit_ai,
            ai_affiliated=seen.ai_affiliated or marks.ai_affiliated,
            fuzz=seen.fuzz or marks.fuzz,
        )
        bucket[f"mention_{marks.band}"] += 1
        category = classify(record["reporter"], year)
        bucket[f"{category}_attributed"] += 1
        if category == "ai":
            ai_reporters[record["reporter"][:90]] += 1
            unique_ai_cves[year].add(record["cve"])
    unique_bands: dict[int, Counter] = defaultdict(Counter)
    for (year, _cve), marks in cve_signals.items():
        unique_bands[year][marks.band] += 1
    this_year = datetime.now(timezone.utc).year
    latest = max(
        (record["announced"] for record in rows if record["announced"]),
        default="",
    )
    annual = [
        {
            "year": year,
            "unique_cves": len(unique_cves[year]),
            "unique_explicit_ai": unique_bands[year]["explicit_ai"],
            "unique_ai_affiliated": unique_bands[year]["ai_affiliated"],
            "unique_fuzz": unique_bands[year]["fuzz"],
            "unique_other": unique_bands[year]["other"],
            "total": per_year[year]["total"],
            "mentions_explicit_ai": per_year[year]["mention_explicit_ai"],
            "mentions_ai_affiliated": per_year[year]["mention_ai_affiliated"],
            "mentions_fuzz": per_year[year]["mention_fuzz"],
            "mentions_other": per_year[year]["mention_other"],
            "ai_attributed": per_year[year]["ai_attributed"],
            "unique_ai_cves": len(unique_ai_cves[year]),
            "fuzz_attributed": per_year[year]["fuzz_attributed"],
            "other_attributed": per_year[year]["other_attributed"],
            "partial_year": "yes" if year == this_year else "no",
            "data_through": latest if year == this_year else "",
        }
        for year in sorted(per_year)
        if per_year[year]["total"]
    ]
    print(
        f"firefox: {sum(r['unique_cves'] for r in annual)} distinct CVEs across "
        f"{sum(r['total'] for r in annual)} advisory-CVE mentions, "
        f"{annual[0]['year']}–{annual[-1]['year']}"
    )
    print(
        "  AI-attributed reporter strings: "
        + "; ".join(f"{c}x {n[:52]}" for n, c in ai_reporters.most_common(4))
    )
    return annual


def build_finders(rows: list[dict]) -> list[dict]:
    """One row per reporter per year.

    Reporter strings stay verbatim, the multi-person ones included, because
    splitting them on commas would invent individual attributions.
    """
    counted: dict[tuple, int] = defaultdict(int)
    for record in rows:
        finder = record["reporter"].strip()
        if finder:
            counted[
                (record["year"], finder, band(finder, record["year"]))
            ] += 1
    out = [
        {"year": year, "finder": finder, "category": category, "cves": count}
        for (year, finder, category), count in sorted(
            counted.items(), key=lambda item: (item[0][0], -item[1])
        )
    ]
    ai = [row for row in out if row["category"] in ("explicit_ai", "ai_affiliated")]
    explicit = [row for row in ai if row["category"] == "explicit_ai"]
    print(f"firefox finders: {len(out)} year-finder rows, {len(ai)} AI-marked "
          f"({len(explicit)} naming a method)")
    if ai:
        top = max(ai, key=lambda row: row["cves"])
        print(f"  top AI finder {top['cves']} advisory-CVE mentions — "
              f"{top['finder'][:56]}")
    return out


def main() -> None:
    rows = records()
    write_csv(HERE / "firefox-advisories.csv", build_annual(rows))
    write_csv(HERE / "firefox-finders.csv", build_finders(rows))


if __name__ == "__main__":
    main()
