#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

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
    if len(awarded) != 4:
        failures.append(f"{len(awarded)} awarded records; the prose narrates four")
    if len(pending) != 1:
        failures.append(f"{len(pending)} pending rows; the prose narrates one")

    baseline = hutter[0]
    ladder = [baseline] + awarded
    steps = [100 * (1 - int(cur["total_bytes"]) / int(prev["total_bytes"]))
             for prev, cur in zip(ladder, ladder[1:])]
    total = 100 * (1 - int(awarded[-1]["total_bytes"]) / int(baseline["total_bytes"]))
    hurdle = int(int(awarded[-1]["total_bytes"]) * 0.99)
    claim = pending[0]
    further = 100 * (1 - int(claim["total_bytes"]) / int(awarded[-1]["total_bytes"]))
    uncapped = ltcb[-1]
    if int(uncapped["total_bytes"]) != min(int(row["total_bytes"]) for row in ltcb):
        failures.append("the last LTCB row is not the series minimum, so the "
                        "'has not moved since' reading no longer holds")

    claims = {
        f"{int(baseline['total_bytes']):,} bytes at the 2019 "
        f"{baseline['program']} baseline": "baseline",
        f"{awarded[0]['program']} by {awarded[0]['author']} on "
        f"{awarded[0]['date']}": "first award",
        f"{awarded[1]['program']} by {awarded[1]['author']} on "
        f"{awarded[1]['date']}": "second award",
        f"{awarded[2]['program']} by {awarded[2]['author']} on "
        f"{awarded[2]['date']}": "third award",
        f"on {awarded[3]['date']} at {int(awarded[3]['total_bytes']):,} bytes":
            "fourth award",
        f"those steps are {steps[0]:.2f}%, {steps[1]:.2f}%, {steps[2]:.2f}% "
        f"and {steps[3]:.2f}%": "step sizes",
        f"down {total:.1f}% from the 2019 baseline": "total improvement",
        f"on {claim['date']} at {int(claim['total_bytes']):,} bytes":
            "pending claim",
        f"a further {further:.2f}%": "pending step",
        f"inside the {hurdle:,} needed to clear the 1% hurdle": "hurdle",
        f"{uncapped['program']} reached {int(uncapped['total_bytes']):,} bytes "
        f"on {uncapped['date']}": "uncapped frontier",
        f"flat since October 2023 at {int(uncapped['total_bytes']) / 1e6:.1f} MB":
            "uncapped corner note",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
