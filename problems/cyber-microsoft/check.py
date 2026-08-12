#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "msrc-cves.csv")
    monthly = read_csv(HERE / "msrc-monthly.csv")
    ai_rows = read_csv(HERE / "msrc-ai-cves.csv")
    by_year = {row["year"]: row for row in rows}
    latest = next(row for row in rows if row["partial_year"] == "yes")
    count = {year: int(row["cves"]) for year, row in by_year.items()}

    failures = []
    for row in rows:
        banded = sum(int(row[band]) for band in
                     ("explicit_ai", "ai_affiliated", "fuzz", "other"))
        if banded != int(row["cves"]):
            failures.append(f"{row['year']} bands sum to {banded}, not "
                            f"{row['cves']} CVEs")
        if int(row["year"]) < 2025 and (int(row["explicit_ai"])
                                        or int(row["ai_affiliated"])):
            failures.append(f"{row['year']} has AI-marked CVEs; the prose says "
                            "none exist before 2025")
    monthly_by_year: dict[str, int] = {}
    for row in monthly:
        year = row["month"][:4]
        monthly_by_year[year] = monthly_by_year.get(year, 0) + int(row["cves"])
    if monthly_by_year != count:
        failures.append("monthly CSV totals do not match the annual CSV")

    ai_by_year = {y: [r for r in ai_rows if r["date"].startswith(y)]
                  for y in ("2025", "2026")}
    for year in ai_by_year:
        marked = int(by_year[year]["explicit_ai"]) + int(by_year[year]["ai_affiliated"])
        if len(ai_by_year[year]) != marked:
            failures.append(f"{year} AI CSV has {len(ai_by_year[year])} rows but "
                            f"the annual bands sum to {marked}")

    def team(row_list, test):
        return sum(
            1 for row in row_list
            if any(test(credit) for credit in row["credits"].split(" | "))
        )

    sec_2025 = team(ai_by_year["2025"], lambda c: "SEC-agent" in c)
    enki_2025 = team(ai_by_year["2025"],
                     lambda c: "SEC-agent" in c and "ENKI" in c)
    sec_2026 = team(ai_by_year["2026"], lambda c: "SEC-agent" in c)
    xbow_2026 = team(ai_by_year["2026"], lambda c: "XBOW" in c)
    claude_2026 = len(ai_by_year["2026"]) - sec_2026 - xbow_2026
    ai_2026 = int(latest["explicit_ai"]) + int(latest["ai_affiliated"])
    if sec_2026 + xbow_2026 + claude_2026 != ai_2026:
        failures.append("the 2026 team split double-counts a CVE")

    plateau = [count[str(year)] for year in range(2019, 2024)]
    ratio = annualized(count["2026"], latest["data_through"]) / count["2025"]
    ack_2016 = round(100 * int(by_year["2016"]["acknowledged"]) / count["2016"])
    ack_2026 = round(100 * int(by_year["2026"]["acknowledged"]) / count["2026"])
    months_2016 = sum(1 for row in monthly if row["month"].startswith("2016"))
    month_count = {row["month"]: int(row["cves"]) for row in monthly}
    claims = {
        f"{count['2016']} CVEs across "
        f"{'ten' if months_2016 == 10 else months_2016} documented months of "
        "2016": "2016 count",
        f"{count['2017']} in 2017": "2017 count",
        f"between {min(plateau)} and {max(plateau)} a year from 2019 through "
        "2023": "plateau range",
        f"{round(100 * (count['2024'] / count['2023'] - 1))}% in each of 2024 "
        f"and 2025" if round(100 * (count['2024'] / count['2023'] - 1))
        == round(100 * (count['2025'] / count['2024'] - 1)) else
        "GROWTH RATES DIVERGED; REWRITE THE 2024-2025 SENTENCE": "2024-25 growth",
        f"{count['2024']:,} in 2024": "2024 count",
        f"{count['2025']:,} in 2025": "2025 count",
        f"{count['2026']:,} CVEs through {latest['data_through']}":
            "part-year count",
        f"{count['2026'] / count['2025']:.2f} times the 2025 full year":
            "part-year ratio",
        f"about {ratio:.1f} times 2025": "annualized ratio",
        f"{month_count['2026-06']} CVEs dated June 2026": "June 2026 record",
        f"{month_count['2026-07']} CVEs dated July 2026": "July 2026 record",
        f"{month_count['2026-07'] / month_count['2026-06']:.1f} times the June "
        "record": "July against June",
        f"{by_year['2025']['explicit_ai']} AI-marked CVEs": "2025 AI count",
        f"{ai_2026} AI-marked CVEs, or "
        f"{100 * ai_2026 / count['2026']:.1f}% of the part year":
            "2026 AI share",
        f"{latest['explicit_ai']} name an AI system or method and "
        f"{latest['ai_affiliated']} name only an AI-security employer":
            "2026 AI band split",
        f"never exceeds {max(int(row['fuzz']) for row in rows)} CVEs":
            "fuzz ceiling",
        f"{ack_2016}% of 2016's CVEs carry at least one named credit, rising "
        f"to {ack_2026}% in the 2026 part year": "acknowledgment coverage",
        f"{by_year['2024']['no_customer_action']} CVEs in 2024, "
        f"{by_year['2025']['no_customer_action']} in 2025 and "
        f"{by_year['2026']['no_customer_action']} in the 2026 part year":
            "cloud-CVE counts",
        f"all {sec_2025} credit the SEC-agent team": "2025 team",
        f"{enki_2025} of them jointly with ENKI WhiteHat": "2025 ENKI overlap",
        f"{sec_2026} credit the SEC-agent team, {claude_2026} credit Claude or "
        f"Anthropic": "2026 team split",
        f"{xbow_2026} credit XBOW": "2026 XBOW count",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
