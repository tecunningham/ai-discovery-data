#!/usr/bin/env python3
"""Recompute this page's fact lines from the record transcription."""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

SELECTED = ("6.5", "6.7", "6.48", "6.49", "6.50")
GROUP_LABELS = {
    "6.5": "minimum-overlap",
    "6.7": "difference basis",
    "6.48": "triangle packing",
    "6.49": "convex packing",
    "6.50": "max-min packing",
}
# The page prints each AI step's relative gain at the precision shown; each
# printed string must round-trip from the CSV's relative_gain_pct.
AI_STEP_PRINTED = {
    "C_6.48(11,tri)": "1.44",
    "C_6.49(13)": "0.98",
    "C_6.49(14)": "0.47",
    "C_6.7": "0.69",
    "r2_6.50(3,14)": "0.052",
    "r2_6.50(2,16)": "0.0057",
    "C_6.5_upper": "0.00075",
}
MEDIAN_LABELS = (
    ("ai_evolution", "AlphaEvolve"),
    ("ai_guided_search", "AI-guided search"),
    ("ai_agents", "agent platform"),
    ("human_search", "human computer search"),
    ("human_analytic", "human by hand"),
)


def decimals(printed: str) -> int:
    return len(printed.split(".")[1]) if "." in printed else 0


def main() -> int:
    rows = read_csv(HERE / "alphaevolve-records.csv")
    selected = [row for row in rows if row["problem"] in SELECTED
                and row["year"] and row["is_record"] == "yes"]
    years = sorted(int(row["year"]) for row in selected)
    by_year = Counter(years)
    ai = [row for row in selected if row["agent"].startswith("ai_")]
    pre = [year for year in years if year <= 2024]

    failures: list[str] = []
    if {row["year"] for row in ai} != {"2025"}:
        failures.append("the AI steps in the five groups are no longer all "
                        "dated 2025")
    for quantity, printed in AI_STEP_PRINTED.items():
        gain = next(float(row["relative_gain_pct"]) for row in ai
                    if row["quantity"] == quantity)
        if round(gain, decimals(printed)) != float(printed):
            failures.append(f"the printed AI gain {printed}% for {quantity} "
                            f"does not round from the CSV's {gain}")
    overlap = sorted((row for row in selected if row["problem"] == "6.5"),
                     key=lambda row: int(row["step"]))
    if [overlap[-2]["value"], overlap[-1]["value"]] != \
            ["0.380926853433087", "0.380924"]:
        failures.append("the minimum-overlap levels fact no longer matches "
                        "the last two 6.5 rows")
    # Cross-CSV consistency with the sampling frame this page states.
    frame = read_csv(HERE.parent / "math-alphaevolve-inventory"
                     / "alphaevolve-inventory.csv")
    frame_live = sum(row["status"] in ("world_record", "worse_than_record",
                                       "former_record") for row in frame)
    if (len(frame), frame_live) != (65, 31):
        failures.append("the inventory frame no longer counts 65 problems "
                        "with 31 live records; the Definition states both")

    groups: dict[str, list[int]] = defaultdict(list)
    for row in selected:
        groups[row["problem"]].append(int(row["year"]))
    by_group = " · ".join(
        f"{GROUP_LABELS[problem]} {len(groups[problem])} steps "
        f"({min(groups[problem])}–{max(groups[problem])})"
        for problem in SELECTED)

    pooled = [row for row in rows if row["relative_gain_pct"]
              and row["is_record"] == "yes"]
    medians = []
    for agent, label in MEDIAN_LABELS:
        gains = sorted(float(row["relative_gain_pct"]) for row in pooled
                       if row["agent"] == agent)
        medians.append(f"{label} {gains[len(gains) // 2]:+.2f}% over "
                       f"{len(gains)}" + (" steps" if agent == "ai_evolution"
                                          else ""))

    claims = {
        f"**steps:** {len(selected)} record steps across the five groups, "
        f"{years[0]}–{years[-1]}; {len(ai)} AI-set, all in 2025":
            "steps fact",
        "**by-year:** " + " · ".join(f"{year}: {by_year[year]}"
                                     for year in sorted(by_year)):
            "by-year fact",
        f"**by-group:** {by_group}": "by-group fact",
        "**ai-step sizes:** "
        f"+{AI_STEP_PRINTED['C_6.48(11,tri)']}% on triangle packing · "
        f"+{AI_STEP_PRINTED['C_6.49(13)']}% and "
        f"+{AI_STEP_PRINTED['C_6.49(14)']}% on convex packing · "
        f"+{AI_STEP_PRINTED['C_6.7']}% on difference basis · "
        f"+{AI_STEP_PRINTED['r2_6.50(3,14)']}% and "
        f"+{AI_STEP_PRINTED['r2_6.50(2,16)']}% on the two max-min slices · "
        f"+{AI_STEP_PRINTED['C_6.5_upper']}% on minimum-overlap":
            "ai-step sizes fact",
        "**minimum-overlap levels:** the 2025 AI step moves the upper bound "
        f"from {overlap[-2]['value']} (Haugland, {overlap[-2]['year']}) to "
        f"{overlap[-1]['value']}": "minimum-overlap levels fact",
        "**pooled step-size medians (whole file):** " + " · ".join(medians):
            "pooled-medians fact",
        f"{by_year[2026]} record step in 2026 against {by_year[2025]} in "
        f"2025 and a {len(pre) / (2024 - years[0] + 1):.1f}/year mean over "
        f"{years[0]}–2024": "verdict clause",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
