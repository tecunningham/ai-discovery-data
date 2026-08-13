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
    claims = {
        f"from {counts['2016']:,} in 2016": "2016 count",
        f"{counts['2020']:,} in 2020": "2020 count",
        f"{counts['2022']:,} in 2022": "2022 count",
        f"{counts['2024']:,} in 2024": "2024 count",
        f"{counts['2025']:,} in 2025": "2025 count",
        f"{counts['2026']:,} through": "part-year count",
        f"about {round(pace, -2):,.0f}": "annualized pace",
        f"{pace / counts['2025']:.1f} times the\n2025 count".replace("\n", " "):
            "pace against 2025",
        f"{peak['quarter']} alone holds {int(peak['distinct_cves']):,}":
            "peak quarter",
        f"{rated:,} of the {total:,} CVEs ({100 * rated / total:.0f}%)":
            "severity label coverage",
        f"{credited:,} CVEs ({100 * credited / total:.1f}%) carry any credit":
            "credit coverage",
        f"{len(ai_rows)} AI-marked": "AI-marked ledger size",
    }
    return report(missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
