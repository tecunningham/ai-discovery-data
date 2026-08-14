#!/usr/bin/env python3
"""Recompute this page's fact lines from the two-ladder slice and its parent."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

# Each printed step size must round-trip from the CSV's relative_gain_pct at
# the precision shown, keyed by (problem, step).
PRINTED_GAINS = {
    ("6.44", "4"): "0.28", ("6.44", "5"): "0.91",
    ("6.44", "1"): "2.6", ("6.44", "2"): "0.79", ("6.44", "3"): "2.5",
    ("6.44", "6"): "1.26", ("6.44", "7"): "0.002",
    ("6.3", "1"): "0.78", ("6.3", "3"): "6.6", ("6.3", "2"): "0.60",
}


def decimals(printed: str) -> int:
    return len(printed.split(".")[1]) if "." in printed else 0


def main() -> int:
    rows = read_csv(HERE / "sums-autoconvolution-records.csv")
    ladders = {problem: sorted(
        (row for row in rows if row["problem"] == problem),
        key=lambda row: int(row["step"]))
        for problem in ("6.44", "6.3")}
    by_year = Counter(int(row["year"]) for row in rows)
    ai = [row for row in rows if row["agent"].startswith("ai_")]

    failures: list[str] = []
    if any(row["is_record"] != "yes" for row in rows):
        failures.append("a non-record row appeared in the slice; every fact "
                        "line counts all rows as record steps")
    if {row["year"] for row in ai} != {"2025"} or len(ai) != 4 or any(
            sum(row["agent"].startswith("ai_") for row in ladder) != 2
            for ladder in ladders.values()):
        failures.append("the AI steps are no longer two per ladder, all "
                        "2025")
    for (problem, step), printed in PRINTED_GAINS.items():
        gain = next(float(row["relative_gain_pct"]) for row in rows
                    if row["problem"] == problem and row["step"] == step)
        if round(gain, decimals(printed)) != float(printed):
            failures.append(f"the printed gain {printed}% for problem "
                            f"{problem} step {step} does not round from the "
                            f"CSV's {gain}")
    # The slice is generated from the parent transcription; the two must
    # agree row for row on the shared columns.
    parent = read_csv(HERE.parent / "math-alphaevolve-records"
                      / "alphaevolve-records.csv")
    parent_slice = [(row["problem"], row["step"], row["value"], row["agent"])
                    for row in parent if row["problem"] in ("6.44", "6.3")]
    own = [(row["problem"], row["step"], row["value"], row["agent"])
           for row in rows]
    if sorted(parent_slice) != sorted(own):
        failures.append("the slice has drifted from the parent "
                        "transcription in math-alphaevolve-records")
    medians = {}
    pooled = [row for row in parent if row["relative_gain_pct"]
              and row["is_record"] == "yes"]
    for agent in ("ai_evolution", "human_search", "human_analytic"):
        gains = sorted(float(row["relative_gain_pct"]) for row in pooled
                       if row["agent"] == agent)
        medians[agent] = f"{gains[len(gains) // 2]:+.2f}%"

    def chain(problem: str) -> str:
        return " → ".join(row["value"] for row in ladders[problem])

    claims = {
        f"**steps:** {len(rows)} record steps: {len(ladders['6.44'])} on "
        f"$C_{{6.44}}$ ({ladders['6.44'][0]['year']}–"
        f"{ladders['6.44'][-1]['year']}) and {len(ladders['6.3'])} on "
        f"$C_{{6.3}}$ ({ladders['6.3'][0]['year']}–"
        f"{ladders['6.3'][-1]['year']})": "steps fact",
        "**by-year:** " + " · ".join(f"{year}: {by_year[year]}"
                                     for year in sorted(by_year)):
            "by-year fact",
        f"**ai steps:** {len(ai)} of {len(rows)}, all AlphaEvolve, all in "
        "2025, two on each ladder": "ai-steps fact",
        f"**c-6.44 ladder:** {chain('6.44')}".replace(
            "1.14465 →", "1.14465 (all 2007, Gyarmati, Hennecart and Ruzsa) "
            "→").replace(
            "1.1584 →", "1.1584 (2025, AlphaEvolve) →")
        + " (2025, human)": "c-6.44 ladder fact",
        f"**c-6.3 ladder:** {ladders['6.3'][0]['value']} (2010) → "
        f"{ladders['6.3'][1]['value']} (2025, AlphaEvolve) → "
        f"{ladders['6.3'][2]['value']} (2025, Boyer and Li) → "
        f"{ladders['6.3'][3]['value']} (2025, AlphaEvolve)":
            "c-6.3 ladder fact",
        "**step sizes, c-6.44:** AI "
        f"+{PRINTED_GAINS[('6.44', '4')]}% and "
        f"+{PRINTED_GAINS[('6.44', '5')]}%; human "
        f"+{PRINTED_GAINS[('6.44', '1')]}%, "
        f"+{PRINTED_GAINS[('6.44', '2')]}% and "
        f"+{PRINTED_GAINS[('6.44', '3')]}% in 2007, "
        f"+{PRINTED_GAINS[('6.44', '6')]}% and "
        f"+{PRINTED_GAINS[('6.44', '7')]}% in 2025": "c-6.44 sizes fact",
        "**step sizes, c-6.3:** AI "
        f"+{PRINTED_GAINS[('6.3', '1')]}% and "
        f"+{PRINTED_GAINS[('6.3', '3')]}%; human "
        f"+{PRINTED_GAINS[('6.3', '2')]}%": "c-6.3 sizes fact",
        f"**parent-frame medians:** {medians['ai_evolution']} per "
        f"AlphaEvolve step against {medians['human_search']} for human "
        f"computer search and {medians['human_analytic']} for human work by "
        "hand": "parent-medians fact",
        f"{by_year[2026]} record steps in 2026 against {by_year[2025]} in "
        f"2025; the other {by_year[2007] + by_year[2010]} fall in 2007 and "
        "2010": "verdict clause",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
