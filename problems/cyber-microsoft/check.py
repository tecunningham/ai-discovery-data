#!/usr/bin/env python3
"""Recompute this page's fact lines and cross-check the vendored CSVs."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "msrc-cves.csv")
    monthly = read_csv(HERE / "msrc-by-month.csv")
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
            failures.append(f"{row['year']} has AI-marked CVEs; the ai-marked "
                            "fact line says none exist before 2025")
    monthly_by_year: dict[str, int] = {}
    for row in monthly:
        year = row["month"][:4]
        monthly_by_year[year] = monthly_by_year.get(year, 0) + int(row["cves"])
    if monthly_by_year != count:
        failures.append("monthly CSV totals do not match the annual CSV")

    ai_by_year = {y: [r for r in ai_rows if r["date"].startswith(y)]
                  for y in ("2025", "2026")}
    for year in ai_by_year:
        marked = (int(by_year[year]["explicit_ai"])
                  + int(by_year[year]["ai_affiliated"]))
        if len(ai_by_year[year]) != marked:
            failures.append(f"{year} AI CSV has {len(ai_by_year[year])} rows "
                            f"but the annual bands sum to {marked}")

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
    claude_2026 = team(ai_by_year["2026"],
                       lambda c: "Claude" in c or "Anthropic" in c)
    other_2026 = (len(ai_by_year["2026"])
                  - sec_2026 - xbow_2026 - claude_2026)
    ai_2026 = int(latest["explicit_ai"]) + int(latest["ai_affiliated"])
    if sec_2026 + xbow_2026 + claude_2026 + other_2026 != ai_2026:
        failures.append("the 2026 team split double-counts a CVE")
    if sec_2025 != len(ai_by_year["2025"]):
        failures.append("not every 2025 AI-marked CVE carries a SEC-agent "
                        "credit; the 'All ... of 2025' sentence is wrong")
    # The OpenAI remainder bullet states a date and a shared credit string;
    # both are claims about every row in that remainder.
    remainder = [row for row in ai_by_year["2026"]
                 if not any(k in row["credits"]
                            for k in ("SEC-agent", "XBOW", "Claude",
                                      "Anthropic"))]
    if any(row["date"] != "2026-08-11"
           or "Thomas Neil James Shadwell (zemnmez) with OpenAI"
           not in row["credits"] for row in remainder):
        failures.append("the OpenAI remainder rows no longer share the "
                        "quoted credit string and 2026-08-11 date")
    warp = [row for row in ai_by_year["2026"] if "WARP" in row["credits"]]
    if len(warp) != 1 or warp[0]["cve"] != "CVE-2026-33096":
        failures.append("the WARP & MORSE co-credit no longer sits on "
                        "CVE-2026-33096 alone")

    plateau = [count[str(year)] for year in range(2019, 2024)]
    ratio = annualized(count["2026"], latest["data_through"]) / count["2025"]
    ack_2016 = round(100 * int(by_year["2016"]["acknowledged"])
                     / count["2016"])
    ack_2026 = round(100 * int(by_year["2026"]["acknowledged"])
                     / count["2026"])
    months_2016 = sum(1 for row in monthly if row["month"].startswith("2016"))
    month_count = {row["month"]: int(row["cves"]) for row in monthly}
    by_year_line = " · ".join(
        f"{row['year']}: {int(row['cves']):,}" for row in rows
        if row["partial_year"] == "no")
    claims = {
        f"Coverage:** 2016–2026, partial through {latest['data_through']}":
            "coverage field",
        f"{count['2026']:,} CVEs through {latest['data_through']} against "
        f"{count['2025']:,} in 2025; the part year annualizes to about "
        f"{ratio:.1f} times 2025": "verdict clause",
        f"**by-year:** {by_year_line}": "by-year fact",
        f"**2016 span:** {count['2016']} CVEs across "
        f"{'ten' if months_2016 == 10 else months_2016} documented months":
            "2016 span fact",
        f"**plateau and growth:** between {min(plateau)} and {max(plateau)} "
        "a year from 2019 through 2023; "
        + (f"{round(100 * (count['2024'] / count['2023'] - 1))}% growth in "
           "each of 2024 and 2025"
           if round(100 * (count['2024'] / count['2023'] - 1))
           == round(100 * (count['2025'] / count['2024'] - 1)) else
           "GROWTH RATES DIVERGED; REWRITE THE PLATEAU FACT LINE"):
            "plateau fact",
        f"**2026 (through {latest['data_through']}):** {count['2026']:,} "
        f"CVEs, {count['2026'] / count['2025']:.2f} times the 2025 full "
        f"year; annualizes to about {ratio:.1f} times 2025":
            "part-year fact",
        f"**record months:** {month_count['2026-06']} CVEs dated June 2026, "
        f"then {month_count['2026-07']} CVEs dated July 2026, "
        f"{month_count['2026-07'] / month_count['2026-06']:.1f} times the "
        "June figure": "record-months fact",
        f"**ai-marked:** 0 before 2025; "
        f"{int(by_year['2025']['explicit_ai']) + int(by_year['2025']['ai_affiliated'])} "
        f"in 2025; {ai_2026} in 2026, or "
        f"{100 * ai_2026 / count['2026']:.1f}% of the part year — "
        f"{latest['explicit_ai']} name an AI system or method and "
        f"{latest['ai_affiliated']} name only an AI-security employer":
            "ai-marked fact",
        "**fuzz band:** never exceeds "
        f"{max(int(row['fuzz']) for row in rows)} CVEs in any year":
            "fuzz fact",
        f"**acknowledgments:** {ack_2016}% of 2016's CVEs carry at least one "
        f"named credit, rising to {ack_2026}% in the 2026 part year":
            "acknowledgment fact",
        f"**no-customer-action CVEs:** "
        f"{by_year['2024']['no_customer_action']} in 2024, "
        f"{by_year['2025']['no_customer_action']} in 2025 and "
        f"{by_year['2026']['no_customer_action']} in the 2026 part year":
            "cloud-CVE fact",
        f"All {sec_2025} AI-marked CVEs of 2025 carry a SEC-agent credit, "
        f"{enki_2025} of them jointly with ENKI WhiteHat": "2025 team",
        f"{sec_2026} of 2026's {ai_2026} AI-marked CVEs carry one":
            "2026 SEC-agent count",
        f"{claude_2026} of 2026's AI-marked CVEs credit Claude or Anthropic":
            "2026 Claude count",
        f'{xbow_2026} CVEs credit "XBOW"': "2026 XBOW count",
        (f"The remaining {other_2026} CVEs, both dated 2026-08-11"
         if other_2026 == 2 else
         "OPENAI REMAINDER IS NOT TWO; REWRITE THE OPENAI BULLET"):
            "2026 OpenAI remainder",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
