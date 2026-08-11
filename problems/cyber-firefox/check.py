#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "firefox-advisories.csv")
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
    for row in rows:
        banded = sum(int(row[f"unique_{band}"]) for band in
                     ("explicit_ai", "ai_affiliated", "fuzz", "other"))
        if banded != int(row["unique_cves"]):
            failures.append(f"{row['year']} bands sum to {banded}, not "
                            f"{row['unique_cves']} distinct CVEs")
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
        f"rose {round(100 * (unique['2025'] / unique['2021'] - 1))}% from 2021 to 2025":
            "2021-2025 growth",
        f"{ratio['2016']:.1f} in 2016, {ratio['2025']:.1f} in 2025, "
        f"{ratio['2026']:.1f} in 2026": "mentions-per-CVE ratios",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
