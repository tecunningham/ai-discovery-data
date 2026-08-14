#!/usr/bin/env python3
"""Recompute this page's fact lines and verdict clause from the CSV."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> int:
    rows = read_csv(HERE / "matrix-multiplication-omega.csv")
    first, last = rows[0], rows[-1]
    close_1990 = next(row for row in rows if row["year"] == "1990")
    first_2010 = next(row for row in rows if row["year"] == "2010")
    early = float(first["omega"]) - float(close_1990["omega"])
    late = float(first_2010["omega"]) - float(last["omega"])
    post_2010 = [row for row in rows if int(row["year"]) >= 2010]
    count = lambda year: sum(row["year"] == year for row in rows)  # noqa: E731
    failures: list[str] = []
    non_human = [row["year"] for row in rows if row["credit"] != "human"]
    if non_human:
        failures.append(f"rows dated {non_human} are not credited human; the "
                        "page states every step is human")

    claims = {
        f"**steps:** {len(rows)} recorded steps, {first['year']} to "
        f"{last['year']}, all credited human": "steps fact",
        f"**span:** {first['omega']} ({first['discoverer']}, "
        f"{first['year']}) to {last['omega']} ({last['discoverer']}, "
        f"{last['year']})": "span fact",
        f"**first two decades:** the bound fell {early:.4f} from "
        f"{first['year']} to {close_1990['year']}, closing at "
        f"{close_1990['omega']} ({close_1990['discoverer']}, "
        f"{close_1990['year']})": "first-two-decades fact",
        "**post-2010 steps:** " + " · ".join(
            f"{row['omega']} ({row['discoverer']}, {row['year']})"
            for row in post_2010): "post-2010 fact",
        f"**since 2010:** the "
        f"{'six' if len(post_2010) == 7 else len(post_2010) - 1} steps "
        f"after the 2010 record total {late:.4f} over fourteen years":
            "since-2010 fact",
        f"declining — {count('2026')} new bounds in 2026 and "
        f"{count('2025')} in 2025 against {count('2024')} in 2024; movement "
        f"of {late:.4f} over 2010–{last['year']} against {early:.4f} over "
        f"{first['year']}–{close_1990['year']}": "verdict clause",
        f"Coverage:** {first['year']} to {last['year']}, fifteen recorded "
        "steps": "coverage field",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
