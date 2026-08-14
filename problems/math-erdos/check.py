#!/usr/bin/env python3
"""Recompute this page's fact lines from the three CSVs beside it."""

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
    """Recompute the imputed-years fact lines from the two CSVs."""
    rows = read_csv(HERE / "erdos-solution-years.csv")
    overrides = read_csv(HERE / "erdos-solution-year-overrides.csv")
    dated = [int(row["solution_year"]) for row in rows if row["solution_year"]]
    per_year = {year: sum(value == year for value in dated) for year in set(dated)}
    undated = len(rows) - len(dated)
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
        failures.append(f"2000–2023 mean is {baseline:.2f}, outside the "
                        "range the imputed-mean fact was written for")

    def kind(year: int, name: str) -> int:
        return sum(row["solution_year"] == str(year)
                   and row["reference_kind"] == name for row in rows)

    history = read_csv(HERE / "erdos-database-history.csv")
    first, last = history[0], history[-1]
    first_total = int(first["total_problems"])
    works_2024 = len({row["reference"] for row in rows
                      if row["solution_year"] == "2024"})
    catalogued_2026 = sum(row["solution_year"] == "2026"
                          and int(row["problem"]) <= first_total
                          for row in rows)
    wiki_kind = sum(row["reference_kind"] == "ai_wiki" for row in rows)
    preprint_kind = sum(row["reference_kind"] == "preprint" for row in rows)
    basis_wiki = sum(row["basis"] == "ai_wiki" for row in rows)
    if kind(2025, "published") != 1:
        failures.append(f"2025 published-dated rows are "
                        f"{kind(2025, 'published')}, the 2025 anatomy fact "
                        "says 1")
    return {
        f"**imputed rows:** of the {len(rows)} solved problems, {len(dated)} "
        f"carry an imputed year and {undated} state no dateable resolution":
            "imputed-rows fact",
        f"**imputed span:** {min(dated)} to {max(dated)}": "imputed-span fact",
        f"imputed solution years {min(dated)}–{max(dated)}": "coverage field",
        f"**imputed mean:** {baseline:.1f} dated resolutions per year over "
        "2000–2023": "imputed-mean fact",
        f"**imputed recent:** {per_year.get(2024, 0)} in 2024, "
        f"{per_year.get(2025, 0)} in 2025, and {per_year.get(2026, 0)} in "
        f"2026 through {last['date']}": "imputed-recent fact",
        f"**2024 anatomy:** the {per_year.get(2024, 0)} rows of 2024 trace "
        f"to {works_2024} distinct works, with {kind(2024, 'preprint')} "
        f"dated by arXiv preprints and {kind(2024, 'published')} by "
        "published papers": "2024 anatomy fact",
        f"**2025 anatomy:** {kind(2025, 'preprint')} of the "
        f"{per_year.get(2025, 0)} rows are preprint-dated and "
        f"{kind(2025, 'published')} published": "2025 anatomy fact",
        f"**2026 anatomy:** {kind(2026, 'ai_wiki')} of the "
        f"{per_year.get(2026, 0)} rows are dated only by the AI wiki, "
        f"against {kind(2026, 'preprint')} preprints": "2026 anatomy fact",
        f"**2026 placement:** {catalogued_2026} of the "
        f"{per_year.get(2026, 0)} sat at numbers 1–{first_total}, catalogued "
        f"by the {first['date']} snapshot": "2026 placement fact",
        f"**kind totals:** {preprint_kind} of the {len(dated)} dated rows "
        f"rest on arXiv preprints and {wiki_kind} on wiki entries":
            "kind-totals fact",
        f"**basis against kind:** {basis_wiki} problems rest on the wiki "
        f"alone, {wiki_kind} are wiki-dated": "basis-vs-kind fact",
        f"carries {len(overrides)} hand-checkable rows": "override count",
        f"dated {rule_dated} of the {len(rows)} pages": "rule coverage",
        f"supplied a year for {supplied} pages the rule had missed, "
        f"corrected {corrected}, and withdrew {withdrawn}": "review ledger",
        f"leaving {undated} problems with no dateable resolution":
            "review remainder",
        f"{wiki_kind - basis_wiki} problems whose dates rest on the wiki but "
        "were confirmed in review": "seven-problem split",
        f"{per_year.get(2026, 0)} imputed resolutions in 2026 through "
        f"{last['date']}, against {per_year.get(2025, 0)} in 2025 and a "
        f"{baseline:.1f}/year mean over 2000–2023": "verdict clause",
        f"({len(rows)} rows, against {last['total_solved']} in the same "
        "week's statistics snapshot)": "enumeration count",
    }


def main() -> int:
    rows = read_csv(HERE / "erdos-database-history.csv")
    first, last = rows[0], rows[-1]
    fixed = [row for row in rows if row["catalogue_count_unchanged"] == "yes"]
    start, end = fixed[0], fixed[-1]
    gained = int(end["total_solved"]) - int(start["total_solved"])
    grown = int(last["total_problems"]) - int(first["total_problems"])
    days = (date.fromisoformat(end["date"]) - date.fromisoformat(start["date"])).days
    failures = []
    if gained not in WORDS:
        failures.append(f"no spelled form for a gain of {gained}; extend WORDS")
    if len(rows) not in WORDS:
        failures.append(f"no spelled form for {len(rows)} snapshots; extend WORDS")
    if not 95 <= days <= 110:
        failures.append(f"fixed cohort spans {days} days, not 'about a hundred'")
    claims = {
        f"**snapshots:** {WORDS.get(len(rows), len(rows))}, monthly, "
        f"{first['date']} to {last['date']}": "snapshots fact",
        f"**catalogue:** {first['total_problems']} problems at the first "
        f"snapshot to {int(last['total_problems']):,} at the last; the count "
        f"is unchanged from the {start['date']} snapshot on": "catalogue fact",
        f"**solved statuses:** {first['total_solved']} to "
        f"{last['total_solved']}": "solved fact",
        f"**lean-formalized:** {first['lean_formalized']} to "
        f"{last['lean_formalized']}; {last['lean_formalized']} against "
        f"{last['total_solved']} solved statuses at the last snapshot":
            "lean fact",
        f"**fixed cohort:** solved statuses {start['total_solved']} on 30 "
        f"April to {end['total_solved']} on 10 August, "
        f"{WORDS.get(gained, gained)} rows in about a hundred days":
            "fixed-cohort fact",
        f"**cohort growth:** the catalogue grew by {grown} rows inside the "
        "snapshot window": "growth fact",
        "**ai-standalone stock:** about 13 full AI-standalone resolutions in "
        f"the wiki at its 2026-06-30 freeze, against {last['total_solved']} "
        "solved statuses": "AI-stock fact",
        f"**three counts:** 556 solved rows in the solution-years read, "
        f"{last['total_solved']} in the {last['date']} statistics snapshot, "
        "565 on the site's headline of 8 August": "three-counts fact",
        f"stocks of {last['total_solved']} and "
        f"{int(last['total_problems']):,}": "callout scale",
    }
    claims.update(solution_year_claims(failures))
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
