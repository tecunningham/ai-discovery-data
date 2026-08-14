#!/usr/bin/env python3
"""Recompute this page's fact lines from the inventory CSV."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "alphaevolve-inventory.csv")
    counts = Counter(row["status"] or "unclassified" for row in rows)
    live = sum(counts[key] for key in
               ("world_record", "worse_than_record", "former_record"))
    cited = [int(row["n_cited_years"]) for row in rows if row["n_cited_years"]]
    spans = sorted(int(row["latest_cited_year"]) - int(row["earliest_cited_year"])
                   for row in rows
                   if row["n_cited_years"] and int(row["n_cited_years"]) >= 2)
    earliest = min(int(row["earliest_cited_year"]) for row in rows
                   if row["earliest_cited_year"])
    latest = max(int(row["latest_cited_year"]) for row in rows
                 if row["latest_cited_year"])

    failures = []
    heavy = sum(row["n_citations"] in ("13", "14") for row in rows)
    if heavy != 3:
        failures.append(f"{heavy} rows carry 13 or 14 parsed references; the "
                        "prose says three")
    # The two extraction sanity anchors the document names: their cited years
    # must keep matching the independently known attributions.
    sofa = next(row for row in rows if "sofa" in row["title"].lower())
    if not {"1992", "2024"} <= set(sofa["cited_years"].split(";")):
        failures.append("the moving-sofa row no longer returns 1992 and 2024")
    sidon = next(row for row in rows if row["problem"] == "6.2")
    if not {"2010", "2017"} <= set(sidon["cited_years"].split(";")):
        failures.append("the Sidon autoconvolution row (6.2) no longer returns "
                        "2010 and 2017")

    claims = {
        f"the {len(rows)} problems the paper numbers 6.1 to 6.65": "frame size",
        f"cited works span {earliest}–{latest}": "coverage span",
        f"**status composition:** {counts['world_record']} where AlphaEvolve "
        f"holds the record, {counts['matched_optimal']} where it matched a "
        f"known optimum, {counts['worse_than_record']} where it came in below "
        f"the record, {counts['former_record']} where its result has since "
        f"been surpassed, and {counts['unclassified']} unclassified":
            "status composition fact",
        f"**live records:** {live} of the {len(rows)} problems have a live "
        "numeric record (the first, third and fourth groups above)":
            "live-record fact",
        f"**funnel:** {len(rows)} numbered in the paper · {live} with a live "
        "numeric record · 12 drawn as the pre-committed sample · 6 that "
        "yielded a dated scalar record sequence · 2 carrying both AI and "
        "human steps": "funnel fact",
        f"**citation depth:** of the {len(rows)} problems, "
        f"{sum(value >= 1 for value in cited)} cite at least one dated "
        f"reference, {sum(value >= 2 for value in cited)} cite at least two, "
        f"and {sum(value >= 4 for value in cited)} cite at least four":
            "citation-depth fact",
        f"**cited-year spans:** among problems citing two or more dated works "
        f"the median span between earliest and latest cited year is "
        f"{spans[len(spans) // 2]} years": "median-span fact",
        f"baseline — {len(rows)} problems inventoried, {live} with a live "
        "numeric record; built 2026-07-26": "verdict clause",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
