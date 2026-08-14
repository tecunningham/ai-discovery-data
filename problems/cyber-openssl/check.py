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
from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def normalized(rows: list[dict], fields: list[str]) -> list[dict[str, str]]:
    return [{field: str(row.get(field, "")) for field in fields}
            for row in rows]


def main() -> int:
    cves = read_csv(HERE / "openssl-cves.csv")
    annual = read_csv(HERE / "openssl-vulnerabilities.csv")
    finders = read_csv(HERE / "openssl-finders.csv")
    failures: list[str] = []

    identifiers = [row["cve"] for row in cves]
    if len(identifiers) != len(set(identifiers)):
        duplicates = sorted(cve for cve, count in
                            Counter(identifiers).items() if count > 1)
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
        if (row["explicit_ai"] == "yes"
                and not row["ai_evidence_url"].startswith("https://")):
            failures.append(f"{cve} is explicit_ai without an evidence URL")
        if row["explicit_ai"] == "no" and row["ai_evidence_url"]:
            failures.append(f"{cve} has AI evidence but explicit_ai=no")
        if row["metadata_commit"] != METADATA_COMMIT:
            failures.append(f"{cve} does not name the pinned metadata commit")
        if METADATA_COMMIT not in row["source_url"]:
            failures.append(f"{cve} source URL is not pinned")
        if not re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]):
            failures.append(f"{cve} has no source-record SHA-256")
        if (int(row["published"][:4]) < 2025
                and (row["explicit_ai"] == "yes"
                     or row["ai_affiliated"] == "yes")):
            failures.append(f"{cve} carries an AI marker before 2025; the "
                            "AI attribution section says none do")

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
            failures.append(f"{row['year']} provenance bands do not sum to "
                            "total")
    if sum(int(row["total"]) for row in annual) != len(cves):
        failures.append("annual totals do not sum to the CVE ledger")
    if sum(int(row["cves"]) for row in finders) != sum(
        bool(row["reporter"]) for row in cves
    ):
        failures.append("reporter aggregation does not match credited CVE "
                        "rows")

    # The severity table and chart cohorts, recomputed from the same ledger.
    rated = [row for row in cves if int(row["published"][:4]) >= 2015]
    baseline = [row for row in rated if row["published"][:4] != "2026"]
    this_year = [row for row in rated if row["published"][:4] == "2026"]

    def low_share(subset) -> int:
        return round(100 * sum(row["severity"] == "Low" for row in subset)
                     / len(subset))

    conventional = [row for row in this_year
                    if row["explicit_ai"] == "no"
                    and row["ai_affiliated"] == "no"]
    affiliated = [row for row in this_year
                  if row["explicit_ai"] == "no"
                  and row["ai_affiliated"] == "yes"]
    corroborated = [row for row in this_year if row["explicit_ai"] == "yes"]
    severe = round(100 * sum(row["severity"] in ("High", "Critical")
                             for row in baseline) / len(baseline))
    baseline_low = round(100 * sum(row["severity"] == "Low"
                                   for row in baseline) / len(baseline))
    if baseline_low != 50:
        failures.append(f"the 2015–2025 Low share is {baseline_low}%, so "
                        "'half of all rated CVEs were Low' is wrong")
    if not (sum(r["severity"] == "High" for r in corroborated) == 2
            and sum(r["severity"] == "High" for r in this_year) == 2
            and not any(r["severity"] == "Critical" for r in this_year)):
        failures.append("the corroborated set no longer holds exactly the "
                        "two High-severity CVEs of 2026")

    def table_row(label: str, subset) -> str:
        cells = " | ".join(str(sum(r["severity"] == s for r in subset))
                           for s in ("Critical", "High", "Moderate", "Low"))
        return f"| {label} | {cells} |"

    uncredited = [row for row in this_year if not row["reporter"]]

    # The corroborated register: Aisle's enumerations grouped by publication
    # date, plus the single reporter-text method credit.
    aisle = [row for row in cves if row["explicit_ai"] == "yes"
             and "aisle.com" in row["ai_evidence_url"]]
    aisle_by_date = Counter(row["published"] for row in aisle)
    named = [row for row in cves if row["explicit_ai"] == "yes"
             and "aisle.com" not in row["ai_evidence_url"]]
    if len(named) != 1 or named[0]["cve"] != "CVE-2026-45447":
        failures.append("the reporter-text method credit is no longer "
                        "CVE-2026-45447 alone")
    all_corroborated = [row for row in cves if row["explicit_ai"] == "yes"]
    corr_2026 = sum(row["published"].startswith("2026")
                    for row in all_corroborated)
    corr_2025 = sum(row["published"].startswith("2025")
                    for row in all_corroborated)

    # 2026 batches, recomputed from the ledger's publication dates.
    batches = sorted(Counter(row["published"] for row in cves
                             if row["published"].startswith("2026")).items())

    def day_month(iso: str) -> str:
        return f"{int(iso[8:10])} {MONTHS[int(iso[5:7]) - 1]}"

    batch_dates = ", ".join(day_month(d) for d, _ in batches[:-1])
    batch_dates += f" and {day_month(batches[-1][0])}"
    batch_counts = ", ".join(str(c) for _, c in batches[:-1])
    batch_counts += f" and {batches[-1][1]} CVEs"

    current = next(row for row in annual if row["year"] == "2026")
    year_2025 = next(row for row in annual if row["year"] == "2025")
    full_years = sorted((row for row in annual if row["year"] != "2026"),
                        key=lambda row: int(row["total"]), reverse=True)
    peak_1, peak_2 = full_years[0], full_years[1]
    comparable = sorted((row for row in annual if row["year"] != "2026"),
                        key=lambda row: int(row["comparable_through_aug_05"]),
                        reverse=True)[:3]
    ai_or_affiliated = (int(current["corroborated_ai"])
                        + int(current["ai_affiliated_unverified"]))

    claims = {
        f"Coverage:** 2002–2026, partial through {current['data_through']}":
            "coverage field",
        f"{current['total']} CVEs by {current['data_through']} against "
        f"{year_2025['total']} in all of 2025; the largest prior full years "
        f"were {peak_1['total']} in {peak_1['year']} and "
        f"{peak_2['total']} in {peak_2['year']}": "verdict clause",
        f"**2026 (through {current['data_through']}):** {current['total']} "
        f"CVEs; {current['corroborated_ai']} corroborated AI, "
        f"{current['ai_affiliated_unverified']} AI-affiliated with method "
        f"unverified, {current['conventional_or_fuzz']} with conventional "
        f"or fuzzing credits, {current['unknown']} uncredited": "2026 fact",
        f"**prior full-year peaks:** {peak_1['total']} in {peak_1['year']} "
        f"and {peak_2['total']} in {peak_2['year']}": "peaks fact",
        "**same-period comparison (1 January to 5 August):** "
        f"{current['comparable_through_aug_05']} in 2026 versus "
        f"{comparable[0]['comparable_through_aug_05']} in "
        f"{comparable[0]['year']}, "
        f"{comparable[1]['comparable_through_aug_05']} in "
        f"{comparable[1]['year']} and "
        f"{comparable[2]['comparable_through_aug_05']} in "
        f"{comparable[2]['year']}, the three largest prior same-period "
        "counts": "same-period fact",
        f"**2025:** {year_2025['total']} CVEs; "
        f"{year_2025['corroborated_ai']} corroborated AI": "2025 fact",
        f"{ai_or_affiliated} of {current['total']}, or "
        f"{round(100 * ai_or_affiliated / int(current['total']))}%, of the "
        "2026 CVEs carry an AI-lab affiliation or an explicit AI method "
        "marker": "AI-or-affiliation share",
        "**2026 publication batches:** coordinated publications on "
        f"{batch_dates} contained {batch_counts}": "batches fact",
        table_row("Corroborated AI", corroborated):
            "corroborated severity row",
        table_row("AI-affiliated, method unverified", affiliated):
            "affiliation-only severity row",
        table_row("Conventional/fuzzing", conventional):
            "conventional severity row",
        table_row("No reporter credit", uncredited):
            "uncredited severity row",
        "**baseline severity (2015–2025):** half of all rated CVEs were "
        f"Low and {severe}% were High or Critical": "baseline severity fact",
        f"**2026 Low shares by cohort:** {low_share(conventional)}% for "
        f"conventional or fuzzing credits, {low_share(affiliated)}% for "
        f"affiliation-only credits, and {low_share(corroborated)}% for the "
        "corroborated-AI set": "2026 cohort severity fact",
        f"**corroborated set:** {len(all_corroborated)} CVEs. {len(aisle)} "
        "are enumerated by Aisle's CVE-level accounts — "
        f"{aisle_by_date['2025-09-30']} published 2025-09-30"
        f" [@aisleopenssl2025], {aisle_by_date['2026-01-27']} on 2026-01-27 "
        f"[@aisleopenssljan2026] and {aisle_by_date['2026-04-07']} on "
        "2026-04-07 [@aisleopensslapr2026]": "corroborated register",
        f"**published by year:** {corr_2026} of the {len(all_corroborated)} "
        f"corroborated CVEs were published in 2026, {corr_2025} in 2025":
            "corroborated by year",
        f"**affiliation-only:** {current['ai_affiliated_unverified']} "
        "further 2026 CVEs name Aisle or Anthropic": "affiliation register",
    }
    failures += missing(prose(HERE), claims)
    return report(failures)


if __name__ == "__main__":
    raise SystemExit(main())
