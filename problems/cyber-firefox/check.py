#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "firefox-advisories.csv")
    ai_cves = read_csv(HERE / "firefox-ai-cves.csv")
    by_year = {row["year"]: row for row in rows}
    latest = next(row for row in rows if row["partial_year"] == "yes")
    unique = {year: int(row["unique_cves"]) for year, row in by_year.items()}
    ratio = {year: int(row["total"]) / int(row["unique_cves"])
             for year, row in by_year.items()}
    ai_marked = int(latest["unique_explicit_ai"]) + int(latest["unique_ai_affiliated"])
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
    team = sum("Nicholas Carlini" in row["reporters"] for row in current_ai)
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
    quarterly = read_csv(HERE / "firefox-quarterly.csv")
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
    impacts: Counter = Counter(row["impact"] for row in cves)
    ai_rows = [row for row in cves
               if row["band"] in ("explicit_ai", "ai_affiliated")]
    ai_impacts: Counter = Counter(row["impact"] for row in ai_rows)
    fuzz_rows = [row for row in cves if row["band"] == "fuzz"]
    fuzz_high_critical = sum(
        row["impact"] in ("High", "Critical") for row in fuzz_rows)
    claims = {
        f"{unique['2016']} in 2016, {unique['2017']} in 2017": "early counts",
        f"{unique['2025']} in 2025": "2025 count",
        f"{unique['2026']} through the latest advisory": "part-year count",
        f"{unique['2026'] / unique['2025']:.1f} times the {int(latest['year']) - 1} "
        "full year": "part-year against 2025",
        f"{ai_marked} AI-marked distinct CVEs, or "
        f"{round(100 * ai_marked / unique['2026'])}%": "AI share",
        f"{latest['unique_explicit_ai']} whose credit names an AI system\nor method "
        f"and {latest['unique_ai_affiliated']} that name only".replace("\n", " "):
            "AI band split",
        f"{by_year['2018']['unique_fuzz']} distinct CVEs in 2018, "
        f"{by_year['2022']['unique_fuzz']} in 2022, then\n"
        f"{by_year['2023']['unique_fuzz']}, {by_year['2024']['unique_fuzz']}, "
        f"{by_year['2025']['unique_fuzz']} and {by_year['2026']['unique_fuzz']}"
        .replace("\n", " "): "fuzz band",
        "annualizes to about "
        f"{round(annualized(int(latest['unique_fuzz']), latest['data_through']))}":
            "fuzz annualization",
        f"Of the {len(current_ai)} AI-marked distinct CVEs in {latest['year']}, "
        f"{team} are credited to a single seven-person team": "per-team split",
        f"roughly {round(100 * team / unique[latest['year']])}% of everything "
        f"Firefox disclosed in {latest['year']}": "team share of the year",
        f"rose {round(100 * (unique['2025'] / unique['2021'] - 1))}% from 2021 to 2025":
            "2021-2025 growth",
        f"{ratio['2016']:.1f} in 2016, {ratio['2025']:.1f} in 2025, "
        f"{ratio['2026']:.1f} in 2026": "mentions-per-CVE ratios",
        f"{quarters['2026-Q1']} distinct CVEs in 2026-Q1 and "
        f"{quarters['2026-Q2']} in 2026-Q2": "2026 quarterly surge",
        f"{round(100 * (impacts['High'] + impacts['Critical']) / len(cves))}% "
        "of distinct CVEs are rated High or Critical and "
        f"{round(100 * impacts['Low'] / len(cves))}% Low": "all-finder impact mix",
        f"of the {len(ai_rows)} AI-marked CVEs, {ai_impacts['High']} are High, "
        f"{ai_impacts['Moderate']} Moderate and {ai_impacts['Low']} Low, with "
        f"{ai_impacts['Critical'] or 'none'} Critical": "AI-marked impact mix",
        f"{round(100 * (ai_impacts['Low'] + ai_impacts['Moderate']) / len(ai_rows))}% "
        "Low or Moderate against "
        f"{round(100 * (impacts['Low'] + impacts['Moderate']) / len(cves))}% "
        "across all finders": "AI against all-finder depth",
        f"{fuzz_high_critical} of its {len(fuzz_rows)} CVEs are High or "
        "Critical": "fuzz impact mix",
    }
    # The undated and unrated remainders are stated only while they exist; the
    # figure drops their ink the same way, so the claims are conditional too.
    if undated:
        claims[f"{undated} of its {len(cves):,} rows have no parseable "
               "announcement date"] = "undated remainder"
    if impacts["Unrated"]:
        claims[f"{impacts['Unrated']} of the {len(cves):,} ledger rows "
               "carries it"] = "unrated remainder"
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
