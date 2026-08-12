#!/usr/bin/env python3
"""Rebuild this folder's record ladder from the ecdsa.fail challenge API.

Run: python3 problems/algorithms-ecdsa-circuit/fetch.py

The challenge (an Eigen Labs project) scores a reversible secp256k1
point-addition circuit as average executed Toffoli count times peak qubit
width, validated over 9024 Fiat-Shamir-derived test shots; lower is better.
The API only accepts a submission if it improves on the standing record, so
the accepted submissions ARE the record ladder — one row per record.

Submissions after lib/chart.py's AS_OF_DATE are dropped, so a refetch cannot
push the vendored CSV past the repository's committed snapshot date; bump
AS_OF_DATE and refetch to extend the series.

Whether a record involved an AI tool is not a structured field. Submitters
write free-text notes, some of which name their coding agent ("Work was done
with GPT-5 Codex", "v6 AdaEvolve"); ai_tool_in_note is a regex over that text
and is a lower bound with an empty value where no note was left.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

BENCHMARKS = "https://api.ecdsa.fail/api/benchmarks"
SUBMISSIONS = "https://api.ecdsa.fail/api/benchmarks/{}/submissions"
# The live, open-ended challenge; gpsanant/ecdsafail-2 through -4 were
# short-lived June trial runs that recorded no improvement.
BENCHMARK_NAME = "gpsanant/ecdsafail-challenge"

AI_TOOL = re.compile(
    r"\b(gpt[-\s.0-9a-z]*|claude|codex|gemini|deepseek|grok|copilot|llm|"
    r"adaevolve|alphaevolve|coding agent|aristotle)\b", re.I)


def as_of() -> date:
    text = (HERE.parents[1] / "lib" / "chart.py").read_text(encoding="utf-8")
    match = re.search(
        r"^AS_OF_DATE\s*=\s*date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)",
        text, re.M)
    return date(*(int(part) for part in match.groups()))


def main() -> None:
    benchmarks = json.loads(fetch(BENCHMARKS))["benchmarks"]
    benchmark = next(b for b in benchmarks if b["name"] == BENCHMARK_NAME)
    submissions = json.loads(
        fetch(SUBMISSIONS.format(benchmark["id"])))["submissions"]
    cutoff = as_of()
    rows = []
    for entry in sorted(submissions, key=lambda s: s["createdAt"]):
        if entry["status"] != "accepted" or not entry.get("officialScore"):
            continue
        day = entry["createdAt"][:10]
        if date.fromisoformat(day) > cutoff:
            continue
        metrics = entry.get("officialMetrics") or {}
        note = entry.get("note") or ""
        rows.append({
            "date": day,
            "datetime_utc": entry["createdAt"][:19].replace("T", " "),
            "score": str(int(float(entry["officialScore"]))),
            "toffoli": str(metrics.get("toffoli", "")),
            "qubits": str(metrics.get("qubits", "")),
            "solver": entry.get("solverUsername") or "",
            "ai_tool_in_note": ("" if not note.strip()
                                else "yes" if AI_TOOL.search(note) else "no"),
        })
    write_csv(HERE / "ecdsa-circuit-records.csv", rows)
    first, last = int(rows[0]["score"]), int(rows[-1]["score"])
    flagged = sum(row["ai_tool_in_note"] == "yes" for row in rows)
    print(f"ecdsa: {len(rows)} accepted records, {rows[0]['date']} to "
          f"{rows[-1]['date']}; score {first:.3g} -> {last:.3g} "
          f"({first / last:.1f}x); {flagged} notes name an AI tool")


if __name__ == "__main__":
    main()
