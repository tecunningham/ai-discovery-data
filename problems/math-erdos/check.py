#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

WORDS = {30: "thirty", 34: "thirty-four", 40: "forty", 13: "thirteen"}


def solution_year_claims(failures: list[str]) -> dict[str, str]:
    """Recompute the imputed-years prose from the two CSVs beside it."""
    rows = read_csv(HERE / "erdos-solution-years.csv")
    overrides = read_csv(HERE / "erdos-solution-year-overrides.csv")
    dated = [int(row["solution_year"]) for row in rows if row["solution_year"]]
    per_year = {year: sum(value == year for value in dated) for year in set(dated)}
    undated = len(rows) - len(dated)
    wiki = [row for row in rows if row["basis"] == "ai_wiki"]
    wiki_2026 = sum(row["solution_year"] == "2026" for row in wiki)
    supplied = sum(1 for row in overrides
                   if not row["rule_year"] and row["solution_year"])
    corrected = sum(1 for row in overrides
                    if row["rule_year"] and row["solution_year"])
    withdrawn = sum(1 for row in overrides
                    if row["rule_year"] and not row["solution_year"])
    rule_dated = (sum(row["basis"] in ("solving_citation", "ai_wiki")
                      for row in rows) + corrected + withdrawn)
    if len(overrides) != supplied + corrected + withdrawn:
        failures.append("overrides rows do not split into "
                        "supplied + corrected + withdrawn")
    baseline = sum(per_year.get(year, 0) for year in range(2000, 2024)) / 24
    if not 5.4 <= baseline <= 6.4:
        failures.append(f"2000–2023 mean is {baseline:.2f}, not 'near six'")
    return {
        f"Of the {len(rows)} solved problems, {len(dated)} carry":
            "imputed coverage",
        f"{undated} state no dateable resolution": "undated count",
        f"runs {min(dated)} to {max(dated)}": "imputed span",
        f"imputed solution years {min(dated)}–{max(dated)}": "coverage field",
        f"{per_year.get(2024, 0)} in 2024, {per_year.get(2025, 0)} in 2025, "
        f"and {per_year.get(2026, 0)} in 2026": "recent years",
        f"{wiki_2026} of its {per_year.get(2026, 0)} rows": "2026 wiki share",
        f"carries {len(overrides)} hand-checkable rows": "override count",
        f"dated {rule_dated} of the {len(rows)} pages": "rule coverage",
        f"supplied a year for {supplied} pages the rule had missed, "
        f"corrected {corrected}, and withdrew {withdrawn}": "review ledger",
        f"for {len(wiki)} problems it is a wiki entry": "wiki-only count",
    }


def main() -> int:
    rows = read_csv(HERE / "erdos-database-history.csv")
    first, last = rows[0], rows[-1]
    fixed = [row for row in rows if row["catalogue_count_unchanged"] == "yes"]
    start, end = fixed[0], fixed[-1]
    gained = int(end["total_solved"]) - int(start["total_solved"])
    days = (date.fromisoformat(end["date"]) - date.fromisoformat(start["date"])).days
    failures = []
    if gained not in WORDS:
        failures.append(f"no spelled form for a gain of {gained}; extend WORDS")
    claims = {
        f"from {first['total_problems']} problems to": "opening catalogue count",
        f"{int(last['total_problems']):,}, statuses marked solved from "
        f"{first['total_solved']} to {last['total_solved']}": "solved endpoints",
        f"from {first['lean_formalized']} to {last['lean_formalized']}":
            "Lean endpoints",
        f"against those {last['total_solved']} solved statuses": "callout denominator",
        f"from {start['total_solved']} on 30 April to {last['total_solved']} on "
        f"10 August": "fixed-cohort endpoints",
        f"{WORDS.get(gained, gained)} rows in about a hundred days":
            "fixed-cohort gain",
        f"{last['lean_formalized']} against {last['total_solved']}": "crossing",
        f"stocks of {last['total_solved']} and {int(last['total_problems']):,}":
            "callout scale",
        f"{len(rows)} snapshots".replace(str(len(rows)), WORDS.get(len(rows), str(len(rows)))):
            "snapshot count",
    }
    if not 95 <= days <= 110:
        failures.append(f"fixed cohort spans {days} days, not 'about a hundred'")
    claims.update(solution_year_claims(failures))
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
