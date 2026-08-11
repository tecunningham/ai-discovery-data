#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

rows = read_csv(HERE / "miplib-solution-releases.csv")
total = lambda field: sum(int(row[field]) for row in rows)
claims = {
    f"{len(rows)} releases": "release count",
    f"{total('better_incumbents')} better incumbents": "incumbent total",
    f"{total('new_optimal_solutions') + total('optimal_status_only')} optimality updates": "optimality total",
    f"{total('first_known_feasible')} first feasible solutions": "first-feasible total",
    "2019-08-26 through 2026-01-26": "coverage dates",
}
raise SystemExit(report(missing(prose(HERE), claims)))
