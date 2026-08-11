#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402

rows = read_csv(HERE / "cvrplib-x-frontier.csv")
counts = Counter(row["event_type"] for row in rows)
years = {row["recorded_date"][:4] for row in rows}
claims = {
    f"{counts['objective_improvement']} better-objective events": "objective count",
    f"{counts['optimality_proof']} optimality-proof events": "proof count",
    f"{len(rows)} event rows": "row count",
    "2024 has no event": "empty 2024",
    f"{min(years)}–{max(years)}": "coverage",
}
raise SystemExit(report(missing(prose(HERE), claims)))
