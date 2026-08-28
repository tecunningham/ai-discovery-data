#!/usr/bin/env python3
"""Recompute this page's fact lines from the CSVs beside it."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    annual = read_csv(HERE / "curl-by-year.csv")
    quarterly = read_csv(HERE / "curl-by-quarter.csv")
    finders = read_csv(HERE / "curl-finders.csv")
    openssl_finders = read_csv(HERE.parent / "cyber-openssl"
                               / "openssl-finders.csv")
    current = next(row for row in annual if row["partial_year"] == "yes")
    through = current["data_through"]
    pace = annualized(int(current["total"]), through)
    baseline = [row for row in annual if 2014 <= int(row["year"]) <= 2023]
    average = sum(int(row["total"]) for row in baseline) / len(baseline)
    year_2025 = next(row for row in annual if row["year"] == "2025")
    quarters = {row["quarter"]: int(row["total"]) for row in quarterly
                if row["quarter"].startswith(current["year"])}

    # The AI-marked band, split back into its two signals from the finder
    # table, and the Aisle concentration within the affiliation-only part.
    def band(year: str, category: str) -> int:
        return sum(int(row["cves"]) for row in finders
                   if row["year"] == year and row["category"] == category)

    explicit_2026 = band("2026", "explicit_ai")
    affiliated_2026 = band("2026", "ai_affiliated")
    aisle = sum(int(row["cves"]) for row in finders
                if row["year"] == "2026" and "Aisle Research" in row["finder"])
    ai_low_share = round(
        100 * int(current["ai_sev_low"]) / int(current["ai_attributed"]))
    other_low_share = round(
        100 * int(current["other_sev_low"]) / int(current["other_attributed"]))

    # The severity figure's baseline cohorts, recomputed over the same rows
    # figure.py groups so the fact lines and the picture cannot drift apart.
    def cohort_share(rows, numerator, denominator) -> int:
        top = sum(sum(int(row[field]) for field in numerator) for row in rows)
        bottom = sum(int(row[denominator]) for row in rows)
        return round(100 * top / bottom)

    early = [row for row in annual if 2010 <= int(row["year"]) <= 2022]
    recent = [row for row in annual if 2023 <= int(row["year"]) <= 2025]
    early_low = cohort_share(early, ["sev_low"], "total")
    early_severe = cohort_share(early, ["sev_high", "sev_critical"], "total")
    recent_human_low = cohort_share(recent, ["other_sev_low"],
                                    "other_attributed")

    failures: list[str] = []
    if explicit_2026 + affiliated_2026 != int(current["ai_attributed"]):
        failures.append("the finder table's 2026 AI bands do not sum to the "
                        "annual ai_attributed column")
    big_sleep_years = {row["year"] for row in finders
                       if "Big Sleep" in row["finder"]}
    if big_sleep_years != {"2025"}:
        failures.append(f"Big Sleep years are {sorted(big_sleep_years)}, "
                        "expected 2025 only")
    pre_2025_ai = [row["year"] for row in finders
                   if row["category"] in ("explicit_ai", "ai_affiliated")
                   and int(row["year"]) < 2025]
    if pre_2025_ai:
        failures.append(f"AI-marked credits exist before 2025 ({pre_2025_ai});"
                        " the AI attribution section says none do")
    if not (any("Stanislav Fort" in row["finder"] for row in finders)
            and any("Stanislav Fort" in row["finder"]
                    for row in openssl_finders)):
        failures.append("Stanislav Fort is not present in both the curl and "
                        "OpenSSL finder tables")

    claims = {
        f"Coverage:** 2000–2026, partial through {through}": "coverage field",
        f"{current['total']} disclosures through {through} annualize to "
        f"roughly {round(pace)} against {year_2025['total']} in 2025 and a "
        f"{average:.1f}/year mean over 2014–2023": "verdict clause",
        f"**2026 (through {through}):** {current['total']} disclosures; "
        f"{current['ai_attributed']} AI-marked, "
        f"{current['other_attributed']} other": "2026 fact",
        f"**2026 annualized:** roughly {round(pace)} disclosures":
            "annualized fact",
        f"**prior rate:** {year_2025['total']} disclosures in 2025; a "
        f"{average:.1f}/year mean over 2014–2023": "prior-rate fact",
        f"**2026 quarters:** 2026-Q1: {quarters['2026-Q1']} · 2026-Q2: "
        f"{quarters['2026-Q2']}": "quarters fact",
        f"**ai-band severity (2026):** {current['ai_sev_low']} of "
        f"{current['ai_attributed']} AI-marked disclosures rated Low "
        f"({ai_low_share}%), none High or Critical; "
        f"{current['other_sev_low']} of {current['other_attributed']} other "
        f"disclosures rated Low ({other_low_share}%)": "AI severity fact",
        f"**severity drift:** 2010–2022 disclosures were {early_low}% Low "
        f"and {early_severe}% High or Critical; 2023–2025 non-AI disclosures "
        f"were {recent_human_low}% Low": "severity-drift fact",
        f"{int(current['ai_attributed']) - explicit_2026} of the "
        f"{current['ai_attributed']} AI-marked credits of 2026 name only an "
        "employer": "affiliation-only count",
        f"{aisle} credit Aisle Research": "Aisle count",
        "Stanislav Fort of Aisle Research appears in both curl and OpenSSL":
            "cross-project finder",
    }
    if int(current["ai_sev_high"]) or int(current["ai_sev_critical"]):
        failures.append("2026 AI-marked disclosures include High or Critical "
                        "ratings; the severity fact line says none")
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
