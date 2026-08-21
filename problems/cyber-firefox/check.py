#!/usr/bin/env python3
"""Recompute this page's fact lines and cross-check the vendored CSVs."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "firefox-by-year.csv")
    ai_cves = read_csv(HERE / "firefox-ai-cves.csv")
    by_year = {row["year"]: row for row in rows}
    latest = next(row for row in rows if row["partial_year"] == "yes")
    unique = {year: int(row["unique_cves"]) for year, row in by_year.items()}
    ratio = {year: int(row["total"]) / int(row["unique_cves"])
             for year, row in by_year.items()}
    ai_marked = (int(latest["unique_explicit_ai"])
                 + int(latest["unique_ai_affiliated"]))
    failures = []
    if ai_marked != int(latest["unique_ai_cves"]):
        failures.append(
            f"the two AI bands sum to {ai_marked} but unique_ai_cves is "
            f"{latest['unique_ai_cves']}"
        )
    # The per-CVE evidence file must agree with the annual bands it itemizes.
    current_ai = [row for row in ai_cves if row["year"] == latest["year"]]
    if len(current_ai) != int(latest["unique_ai_cves"]):
        failures.append(
            f"firefox-ai-cves.csv holds {len(current_ai)} rows for "
            f"{latest['year']} but the annual file counts "
            f"{latest['unique_ai_cves']}"
        )
    team_rows = [row for row in current_ai
                 if "Nicholas Carlini" in row["reporters"]]
    team = len(team_rows)
    # The AI attribution section quotes the team's credit string once for all
    # its rows, which is only honest if the rows really share one string.
    if len({row["reporters"] for row in team_rows}) != 1:
        failures.append("the seven-person team's rows carry differing credit "
                        "strings; the quoted single string is wrong")
    if "using Claude from Anthropic" not in team_rows[0]["reporters"]:
        failures.append("the team credit string no longer names Claude")
    prior_ai = [row["year"] for row in rows
                if int(row["year"]) < 2025 and int(row["unique_ai_cves"])]
    if prior_ai:
        failures.append(f"AI-marked CVEs exist before 2025 ({prior_ai}); the "
                        "ai-marked fact line says none do")
    for row in rows:
        banded = sum(int(row[f"unique_{band}"]) for band in
                     ("explicit_ai", "ai_affiliated", "fuzz", "other"))
        if banded != int(row["unique_cves"]):
            failures.append(f"{row['year']} bands sum to {banded}, not "
                            f"{row['unique_cves']} distinct CVEs")
    # The per-CVE ledger is the file the aggregates summarize, so summing it
    # by year and band must reproduce the annual columns, and its dated rows
    # must reproduce the quarterly totals.
    cves = read_csv(HERE / "firefox-cves.csv")
    quarterly = read_csv(HERE / "firefox-by-quarter.csv")
    per_band: Counter = Counter((row["year"], row["band"]) for row in cves)
    for row in rows:
        for band in ("explicit_ai", "ai_affiliated", "fuzz", "other"):
            if per_band[row["year"], band] != int(row[f"unique_{band}"]):
                failures.append(
                    f"firefox-cves.csv holds {per_band[row['year'], band]} "
                    f"{band} rows for {row['year']} but the annual file "
                    f"counts {row[f'unique_{band}']}"
                )
    undated = sum(not row["date"] for row in cves)
    quarterly_total = sum(int(row["unique_cves"]) for row in quarterly)
    if quarterly_total + undated != len(cves):
        failures.append(
            f"quarterly totals ({quarterly_total}) plus undated ledger rows "
            f"({undated}) do not reproduce the ledger ({len(cves)})"
        )
    quarters = {row["quarter"]: int(row["unique_cves"]) for row in quarterly}
    prior_peak = max(count for quarter, count in quarters.items()
                     if quarter < "2026")
    if min(quarters["2026-Q1"], quarters["2026-Q2"]) <= prior_peak:
        failures.append(
            "the quarters fact line calls 2026-Q1 and 2026-Q2 larger than "
            f"any complete quarter before them, but a prior quarter reached "
            f"{prior_peak}"
        )
    impacts: Counter = Counter(row["impact"] for row in cves)
    ai_rows = [row for row in cves
               if row["band"] in ("explicit_ai", "ai_affiliated")]
    ai_impacts: Counter = Counter(row["impact"] for row in ai_rows)
    fuzz_rows = [row for row in cves if row["band"] == "fuzz"]
    fuzz_high_critical = sum(
        row["impact"] in ("High", "Critical") for row in fuzz_rows)
    ai_2021_2025 = sum(int(by_year[str(y)]["unique_ai_cves"])
                       for y in range(2021, 2026))
    ai_2025 = [row for row in ai_cves if row["year"] == "2025"]
    if len(ai_2025) != 1:
        failures.append(f"firefox-ai-cves.csv holds {len(ai_2025)} rows for "
                        "2025; the AI attribution section describes one")
    by_year_line = " · ".join(
        f"{row['year']}: {row['unique_cves']}"
        for row in rows if row["partial_year"] == "no")

    claims = {
        f"Coverage:** 2016–2026, partial through {latest['data_through']}":
            "coverage field",
        f"{unique['2026']} distinct CVEs through {latest['data_through']} "
        f"against {unique['2025']} in 2025; the part year alone is "
        f"{unique['2026'] / unique['2025']:.1f} times the 2025 full year":
            "verdict clause",
        f"**by-year (distinct CVEs):** {by_year_line}": "by-year fact",
        f"**2026 (through {latest['data_through']}):** {unique['2026']} "
        f"distinct CVEs, {unique['2026'] / unique['2025']:.1f} times the "
        "2025 full year; annualizes to about "
        f"{round(annualized(unique['2026'], latest['data_through']))}":
            "part-year fact",
        f"**2026 quarters:** {quarters['2026-Q1']} distinct CVEs in 2026-Q1 "
        f"and {quarters['2026-Q2']} in 2026-Q2, each larger than any "
        "complete quarter before them": "quarters fact",
        "**prior trend:** distinct CVEs rose "
        f"{round(100 * (unique['2025'] / unique['2021'] - 1))}% from 2021 to "
        f"2025; AI-marked CVEs over those years total {ai_2021_2025}":
            "prior-trend fact",
        f"**ai-marked:** 0 before 2025; {by_year['2025']['unique_ai_cves']} "
        f"in 2025; {ai_marked} in 2026, or "
        f"{round(100 * ai_marked / unique['2026'])}% of the part year — "
        f"{latest['unique_explicit_ai']} name an AI system or method and "
        f"{latest['unique_ai_affiliated']} name only an AI-security employer":
            "ai-marked fact",
        f"**fuzz band:** {by_year['2018']['unique_fuzz']} distinct CVEs in "
        f"2018, {by_year['2022']['unique_fuzz']} in 2022, then "
        f"{by_year['2023']['unique_fuzz']}, {by_year['2024']['unique_fuzz']},"
        f" {by_year['2025']['unique_fuzz']} and "
        f"{by_year['2026']['unique_fuzz']} across 2023–2026; the part year "
        "annualizes to about "
        f"{round(annualized(int(latest['unique_fuzz']), latest['data_through']))}":
            "fuzz fact",
        f"**mentions per distinct CVE:** {ratio['2016']:.1f} in 2016, "
        f"{ratio['2025']:.1f} in 2025, {ratio['2026']:.1f} in 2026":
            "mentions-per-CVE fact",
        "**impact mix (all finders):** "
        f"{round(100 * (impacts['High'] + impacts['Critical']) / len(cves))}%"
        " of distinct CVEs are rated High or Critical and "
        f"{round(100 * impacts['Low'] / len(cves))}% Low":
            "all-finder impact fact",
        f"**impact mix (AI-marked):** of the {len(ai_rows)} AI-marked CVEs, "
        f"{ai_impacts['High']} are High, {ai_impacts['Moderate']} Moderate "
        f"and {ai_impacts['Low']} Low, with "
        f"{ai_impacts['Critical'] or 'none'} Critical — "
        f"{round(100 * (ai_impacts['Low'] + ai_impacts['Moderate']) / len(ai_rows))}%"
        " Low or Moderate against "
        f"{round(100 * (impacts['Low'] + impacts['Moderate']) / len(cves))}% "
        "across all finders": "AI-marked impact fact",
        f"**impact mix (fuzz):** {fuzz_high_critical} of the "
        f"{len(fuzz_rows)} fuzz-credited CVEs are High or Critical":
            "fuzz impact fact",
        f"Of the {len(current_ai)} AI-marked distinct CVEs in "
        f"{latest['year']}, {team} are credited to a single seven-person "
        "team": "team concentration",
        f"CVE-2026-2763 and {team - 1} further CVEs": "team quote locator",
        f"Those {team} CVEs are roughly "
        f"{round(100 * team / unique[latest['year']])}% of everything "
        f"Firefox disclosed in {latest['year']}": "team share of the year",
        f"The single AI-marked CVE of 2025 is {ai_2025[0]['cve']}"
        if len(ai_2025) == 1 else "2025 ROW COUNT CHANGED": "2025 AI CVE",
    }
    if undated:
        claims[f"{undated} of the ledger's {len(cves):,} rows have no "
               "parseable announcement date"] = "undated remainder"
    if impacts["Unrated"]:
        claims[f"{impacts['Unrated']} of the {len(cves):,} ledger rows "
               "carries an Unrated impact"] = "unrated remainder"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
