#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import AS_OF_DATE  # noqa: E402
from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

MONTH_NAMES = ("January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December")


def month_name(month: str) -> str:
    return f"{MONTH_NAMES[int(month[5:]) - 1]} {month[:4]}"


def as_of_month() -> str:
    """The snapshot month, from the matplotlib-free lib/dates.py."""
    return f"{AS_OF_DATE.year}-{AS_OF_DATE.month:02d}"


def main() -> int:
    rows = read_csv(HERE / "arxiv-by-month.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The final row is the month in progress at fetch time, so the last complete
    # month is the one before it. The prose quotes that one. The rule silently
    # breaks when a fetch lands just after a month boundary, before arXiv opens
    # the new month's row — so it is asserted rather than assumed.
    failures = []
    if rows[-1]["month"] != as_of_month():
        failures.append(
            f"the last row is {rows[-1]['month']}, not the AS_OF_DATE month; "
            "the last-row-is-partial rule no longer holds")
    complete = rows[-2]["month"]
    name = month_name(complete)
    growth = round((counts[complete] / counts["2022-11"] - 1) * 100)

    def mean(months: list[str]) -> int:
        return round(sum(counts[month] for month in months) / len(months))

    window = sorted(month for month in counts
                    if month.startswith(complete[:4]) and month <= complete)
    claims = {
        f"from {counts['2022-11']:,} submissions in November 2022":
            "ChatGPT-month baseline",
        f"to {counts[complete]:,} in {name}, the last complete month":
            "latest complete month",
        f"{growth}% growth": "growth since 2022-11",
        f"a {mean(window):,} submissions/month mean over {window[0]} to "
        f"{window[-1]} against monthly means of "
        f"{mean([f'2025-{i:02d}' for i in range(1, 13)]):,} in 2025 and "
        f"{mean([f'2024-{i:02d}' for i in range(1, 13)]):,} in 2024":
            "2026 rate against 2025 and 2024",
        f"Coverage:** {rows[0]['month']} to {rows[-1]['month']}, monthly, "
        "the last month partial": "coverage field",
    }

    # The by-field and subfield claims, recomputed with the same grouping
    # rule figure.py draws with (restated here textually: importing figure.py
    # would pull matplotlib onto the host path).
    legacy = {"alg-geom": "math.AG", "dg-ga": "math.DG", "funct-an": "math.FA",
              "q-alg": "math.QA", "cmp-lg": "cs.CL"}
    physics = {"astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph",
               "hep-th", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics",
               "quant-ph", "chao-dyn", "patt-sol", "adap-org", "comp-gas",
               "solv-int", "acc-phys", "ao-sci", "atom-ph", "bayes-an",
               "chem-ph", "plasm-ph", "supr-con", "mtrl-th"}
    group_totals: dict[tuple[str, str], int] = {}
    subfield_totals: dict[tuple[str, str], int] = {}
    for row in read_csv(HERE / "arxiv-categories-by-month.csv"):
        category = legacy.get(row["category"], row["category"])
        archive = category.split(".")[0]
        group = "physics" if archive in physics else archive
        key = (group, row["month"])
        group_totals[key] = group_totals.get(key, 0) + int(row["submissions"])
        if archive == "math":
            sub = (category, row["month"])
            subfield_totals[sub] = (subfield_totals.get(sub, 0)
                                    + int(row["submissions"]))
    months = sorted({month for _, month in group_totals
                     if "1991-07" <= month <= complete})
    above = next(
        month for month in months
        if all(group_totals.get(("cs", later), 0)
               > group_totals.get(("physics", later), 0)
               for later in months if later >= month))
    co_2024 = round(sum(subfield_totals.get(("math.CO", f"2024-{i:02d}"), 0)
                        for i in range(1, 13)) / 12)
    math_2024 = sum(group_totals.get(("math", f"2024-{i:02d}"), 0)
                    for i in range(1, 13)) / 12
    math_ratio = group_totals[("math", complete)] / math_2024
    claims.update({
        f"from {group_totals[('cs', '2022-11')]:,} monthly submissions in "
        f"November 2022 to {group_totals[('cs', complete)]:,} in {name}":
            "computer-science growth",
        f"and above physics every month since {month_name(above)}":
            "cs-physics crossover",
        f"physics rose {round((group_totals[('physics', complete)] / group_totals[('physics', '2022-11')] - 1) * 100)}% "
        f"from November 2022 to {name}": "physics growth",
        f"mathematics {round((group_totals[('math', complete)] / group_totals[('math', '2022-11')] - 1) * 100)}%, "
        f"from {group_totals[('math', '2022-11')]:,} to "
        f"{group_totals[('math', complete)]:,}": "mathematics growth",
        f"math.CO reached {subfield_totals[('math.CO', complete)]:,} "
        f"submissions in {name} against a 2024 monthly average of {co_2024}":
            "combinatorics surge",
        f"ran at {math_ratio:.1f} times its 2024 monthly average in {name}":
            "math vs 2024 baseline",
    })
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
