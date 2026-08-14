#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def by_year(rows: list[dict[str, str]], event_type: str) -> str:
    counts = Counter(row["recorded_date"][:4] for row in rows
                     if row["event_type"] == event_type)
    return " · ".join(f"{year}: {counts[year]}" for year in sorted(counts))


def main() -> int:
    rows = read_csv(HERE / "cvrplib-x-frontier.csv")
    counts = Counter(row["event_type"] for row in rows)
    years = Counter(row["recorded_date"][:4] for row in rows)
    objectives = [row for row in rows
                  if row["event_type"] == "objective_improvement"]
    pre_2021 = sum(1 for row in objectives if row["recorded_date"] < "2022")
    last_pre_2026 = max(row["recorded_date"] for row in objectives
                        if row["recorded_date"] < "2026")
    proved = {row["instance"] for row in rows
              if row["event_type"] == "optimality_proof"}
    failures = []
    if years["2024"]:
        failures.append(f"{years['2024']} rows dated 2024; the page states "
                        "2024 has no event for an X instance")

    claims = {
        f"**events:** {len(rows)} event rows: "
        f"{counts['objective_improvement']} better-objective events and "
        f"{counts['optimality_proof']} optimality-proof events over "
        f"{min(years)}–{max(years)}": "events fact",
        f"**objectives by-year:** {by_year(rows, 'objective_improvement')}":
            "objectives by-year fact",
        f"**proofs by-year:** {by_year(rows, 'optimality_proof')}":
            "proofs by-year fact",
        "2024 has no event": "empty 2024",
        f"posted {last_pre_2026}": "last pre-2026 objective",
        f"the {counts['optimality_proof']} optimality-proof events cover "
        f"{len(proved)} distinct instances": "proved-instances fact",
        f"declining — {years['2026']} events in 2026 against "
        f"{years['2025']} in 2025; {pre_2021} of the "
        f"{counts['objective_improvement']} better-objective events were "
        "posted 2015–2021": "verdict clause",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
