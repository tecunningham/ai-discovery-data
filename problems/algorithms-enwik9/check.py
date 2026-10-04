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
    rows = read_csv(HERE / "enwik9-records.csv")
    hutter = [row for row in rows if row["series"] == "hutter_enwik9"]
    ltcb = [row for row in rows if row["series"] == "ltcb_enwik9"]
    awarded = [row for row in hutter if row["award"] == "yes"]
    pending = [row for row in hutter if row["award"] == "pending"]
    failures = []
    if len(awarded) != 7:
        failures.append(f"{len(awarded)} awarded records; the page states seven")
    if len(pending) != 1:
        failures.append(f"{len(pending)} pending rows; the page states one")

    baseline = hutter[0]
    ladder = [baseline] + awarded
    steps = [100 * (1 - int(cur["total_bytes"]) / int(prev["total_bytes"]))
             for prev, cur in zip(ladder, ladder[1:])]
    early = [row for row in awarded if row["date"] < "2025"]
    recent = [row for row in awarded if row["date"].startswith("2026")]
    drop_early = 100 * (1 - int(early[-1]["total_bytes"]) / int(baseline["total_bytes"]))
    drop_2026 = 100 * (1 - int(recent[-1]["total_bytes"]) / int(early[-1]["total_bytes"]))
    total = 100 * (1 - int(awarded[-1]["total_bytes"]) / int(baseline["total_bytes"]))
    hurdle = int(int(awarded[-1]["total_bytes"]) * 0.99)
    claim = pending[0]
    further = 100 * (1 - int(claim["total_bytes"]) / int(awarded[-1]["total_bytes"]))
    awards_2025 = sum(row["date"].startswith("2025") for row in awarded)
    uncapped = ltcb[-1]
    if int(uncapped["total_bytes"]) != min(int(row["total_bytes"]) for row in ltcb):
        failures.append("the last LTCB row is not the series minimum, so the "
                        "standing-frontier reading no longer holds")
    nncp = [row for row in ltcb if row["program"] == "nncp v3.2"][0]

    def award(row):
        return f"{row['program']} by {row['author']} on {row['date']}"

    claims = {
        f"**baseline:** {int(baseline['total_bytes']):,} bytes at the 2019 "
        f"{baseline['program']} baseline": "baseline fact",
        **{award(row): f"award {n}" for n, row in enumerate(awarded, 1)},
        f"at {int(early[-1]['total_bytes']):,} bytes": "last pre-2026 award",
        f"at {int(recent[-1]['total_bytes']):,} bytes": "standing record",
        "the steps are " + ", ".join(f"{x:.2f}%" for x in steps[:-1])
        + f" and {steps[-1]:.2f}%": "step sizes",
        f"the four awards of 2021–2024 take the total down {drop_early:.1f}%":
            "2019-2024 improvement",
        f"the three awards of 2026 take it down a further {drop_2026:.1f}%":
            "2026 improvement",
        f"{total:.1f}% below the 2019 baseline": "total improvement",
        f"on {claim['date']} at {int(claim['total_bytes']):,} bytes":
            "pending claim",
        f"a further {further:.2f}%": "pending step",
        f"inside the {hurdle:,} needed to clear the 1% hurdle": "hurdle",
        f"nncp v3.2 reached {int(nncp['total_bytes']):,} bytes on "
        f"{nncp['date']}": "nncp frontier",
        f"{uncapped['program']} reached {int(uncapped['total_bytes']):,} "
        f"bytes on {uncapped['date']}": "uncapped frontier",
        f"accelerating — {len(recent)} awarded records in 2026 against "
        f"{awards_2025} in 2025 and {len(early)} over 2021–2024; the 2026 "
        f"awards cut the record {drop_2026:.1f}% against {drop_early:.1f}% "
        "over 2019–2024": "verdict clause",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
