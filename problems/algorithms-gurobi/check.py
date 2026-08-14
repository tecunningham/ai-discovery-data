#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def pct(speedup: str) -> str:
    """Render a release ratio as the document does: 1.086 -> 8.6, 1.13 -> 13."""
    text = f"{(float(speedup) - 1) * 100:.1f}"
    return text[:-2] if text.endswith(".0") else text


def main() -> int:
    rows = read_csv(HERE / "gurobi-milp-speedups.csv")
    failures: list[str] = []
    if [row["credit"] for row in rows] != ["vendor"] * len(rows):
        failures.append("a row's credit is not 'vendor'; the page states the "
                        "figures are the vendor's own throughout")
    cumulative = 1.0
    for row in rows:
        cumulative *= float(row["release_speedup"])
    releases = " · ".join(f"{row['release']}: {pct(row['release_speedup'])}% "
                          f"on {row['date']}" for row in rows)
    last, prior = rows[-1], rows[-2]
    if last["date"] >= "2026":
        failures.append("the CSV now holds a 2026 release; the verdict "
                        "clause states none exists")

    claims = {
        f"**releases:** {releases}": "releases fact",
        f"**cumulative:** a factor of {cumulative:.2f} since version 9.5 "
        f"across the {len(rows)} releases".replace("4 releases",
                                                   "four releases"):
            "cumulative fact",
        f"no acceleration — no 2026 release exists (series ends "
        f"{last['date']}); the 2025 release gained "
        f"{pct(last['release_speedup'])}% against "
        f"{pct(prior['release_speedup'])}% in 2024 and a cumulative "
        f"{cumulative:.2f}× over 2022–2025": "verdict clause",
        f"announced {rows[0]['date']} to {last['date']}": "coverage field",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
