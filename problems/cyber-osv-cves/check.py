#!/usr/bin/env python3
"""Recompute this page's fact lines from the CSVs beside it."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import by_year_line, annualized, missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    annual = read_csv(HERE / "osv-cves-by-year.csv")
    counts = {row["year"]: int(row["distinct_cves"]) for row in annual}
    current = next(row for row in annual if row["partial_year"] == "yes")
    through = current["data_through"]
    pace = annualized(counts[current["year"]], through)
    quarters = read_csv(HERE / "osv-cves-by-quarter.csv")
    peak = max(quarters, key=lambda row: int(row["distinct_cves"]))
    severity = read_csv(HERE / "osv-severity-by-year.csv")
    rated = sum(int(row[label]) for row in severity
                for label in ("low", "moderate", "high", "critical"))
    total = rated + sum(int(row["unrated"]) for row in severity)
    credits = read_csv(HERE / "osv-credits-by-year.csv")
    credited = sum(int(row["distinct_cves"]) - int(row["uncredited"])
                   for row in credits)
    ai_rows = read_csv(HERE / "osv-ai-cves.csv")
    explicit = [row for row in ai_rows if row["band"] == "explicit_ai"]
    affiliated = [row for row in ai_rows if row["band"] == "ai_affiliated"]
    aisle = sum("Aisle Research" in row["credits"] for row in affiliated)
    ant = sum("AntAISecurityLab" in row["credits"] for row in affiliated)
    year_line = by_year_line(annual, "distinct_cves", thousands=True)

    failures: list[str] = []
    if len(explicit) + len(affiliated) != len(ai_rows):
        failures.append("the AI ledger holds bands other than explicit_ai "
                        "and ai_affiliated")
    # The peak-quarter fact compares one quarter against whole prior years.
    pre_2022_max = max(count for year, count in counts.items()
                       if year < "2022")
    if int(peak["distinct_cves"]) <= pre_2022_max:
        failures.append(
            f"the peak quarter ({peak['distinct_cves']}) no longer exceeds "
            f"every full year before 2022 (max {pre_2022_max})")

    claims = {
        f"Coverage:** 2016–2026, partial through {through}":
            "coverage field",
        f"{counts['2026']:,} distinct CVEs through {through} annualize to "
        f"about {round(pace, -2):,.0f}, {pace / counts['2025']:.1f} times "
        f"2025's {counts['2025']:,}": "verdict clause",
        f"**by-year:** {year_line}": "by-year fact",
        f"**2026 (through {through}):** {counts['2026']:,} distinct CVEs; "
        f"annualizes to about {round(pace, -2):,.0f}, or "
        f"{pace / counts['2025']:.1f} times the 2025 count":
            "part-year fact",
        f"**peak quarter:** {peak['quarter']} alone holds "
        f"{int(peak['distinct_cves']):,} distinct CVEs, more than any full "
        "year before 2022": "peak-quarter fact",
        f"**severity coverage:** {rated:,} of the {total:,} CVEs "
        f"({100 * rated / total:.0f}%) carry an ecosystem severity label":
            "severity-coverage fact",
        f"**credit coverage:** {credited:,} CVEs "
        f"({100 * credited / total:.1f}%) carry any credit":
            "credit-coverage fact",
        f"**ai-marked:** {len(ai_rows)} CVEs — {len(explicit)} whose "
        f"credits state an AI method and {len(affiliated)} carrying an "
        "AI-lab affiliation only": "ai-marked fact",
        f"The AI-marked ledger holds {len(ai_rows)} CVEs. {len(explicit)} "
        "carry credits stating an AI method": "AI register lead",
        f"The other {len(affiliated)} carry an AI-lab affiliation with no "
        f"method stated: {aisle} name Aisle Research, {ant} name "
        "AntAISecurityLab hackerone handles": "affiliation split",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
