#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's prose."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.prose import missing, prose, report  # noqa: E402
from lib.table import read_csv  # noqa: E402


def sci(score: int) -> str:
    """Render a score as the document does: 1.08 × 10¹⁰."""
    exponent = len(str(score)) - 1
    mantissa = score / 10 ** exponent
    superscript = str(exponent).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{mantissa:.2f} × 10{superscript}"


def main() -> int:
    rows = read_csv(HERE / "ecdsa-circuit-records.csv")
    first, last = rows[0], rows[-1]
    first_score, last_score = int(first["score"]), int(last["score"])
    days = (date.fromisoformat(last["date"])
            - date.fromisoformat(first["date"])).days
    solvers = len({row["solver"] for row in rows})
    named = sum(row["ai_tool_in_note"] == "yes" for row in rows)
    blank = sum(row["ai_tool_in_note"] == "" for row in rows)
    no_tool = sum(row["ai_tool_in_note"] == "no" for row in rows)

    # Largest single-step drop, and the step before it.
    biggest = max(range(1, len(rows)),
                  key=lambda i: int(rows[i - 1]["score"]) - int(rows[i]["score"]))
    before = int(rows[biggest - 1]["score"])
    after = int(rows[biggest]["score"])

    failures = []
    if sci(first_score) != "1.08 × 10¹⁰":
        failures.append(f"starting score renders {sci(first_score)}")

    claims = {
        f"from the challenge's starting circuit at {sci(first_score)} to":
            "starting score",
        f"{sci(last_score)} over {days} days": "final score and span",
        f"about {first_score / last_score:.1f}× lower": "improvement factor",
        f"across {len(rows)} accepted records from {solvers} distinct solvers":
            "record and solver counts",
        f"on 31 May, cut the score from {sci(before)} to {sci(after)}":
            "largest step",
        f"{named} of the {len(rows)} notes name one": "AI-tool share",
        f"blank where no note was left ({blank} rows)": "blank-note count",
        f'"no" where a note exists but names no tool ({no_tool} rows)':
            "no-tool count",
        f"Of {len(rows)} accepted records, {named} carry notes naming an AI tool":
            "LLM-section counts",
    }
    return report(failures + missing(prose(HERE), claims))


if __name__ == "__main__":
    raise SystemExit(main())
