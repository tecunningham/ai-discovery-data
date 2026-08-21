"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    AI,
    HUMAN,
    NEUTRAL,
    load,
    scatter,
)


def charts(slug: str):
    """Every problem page as a dot: solve date on x, or the right edge if open.

    The event ledger supplies dates, systems and notes for the solved rows;
    the tooltip carries them so the page states what the PNG's corner note
    can only summarise.
    """
    problems = load(slug, "frontiermath-open-problems.csv")
    events = {row["slug"]: row
              for row in load(slug, "frontiermath-open-solutions.csv")}
    tier_rank = {"Breakthrough": 0, "Major advance": 1, "Solid result": 2,
                 "Moderately interesting": 3}
    problems.sort(key=lambda row: (tier_rank.get(row["notability"], 4),
                                   row["title"].lower()))
    values = []
    for row in problems:
        event = events.get(row["slug"], {})
        values.append({
            "problem": row["title"][:64],
            "date": event.get("date") or "2026-08-14",
            "status": row["status"],
            "tier": row["notability"] or "withdrawn",
            "system": event.get("system") or "—",
            "note": (event.get("note") or "")[:220],
            "url": row["source_url"],
        })
    order = [value["problem"] for value in values]
    spec = scatter(
        values, x="date", x_type="temporal", y="problem", y_type="nominal",
        y_title=None, y_sort=order,
        x_title="Solve date (unsolved rows drawn at the read date)",
        tips=[("problem", "nominal", "problem"),
              ("tier", "nominal", "notability"),
              ("status", "nominal", "status"),
              ("date", "temporal", "date"),
              ("system", "nominal", "system"),
              ("note", "nominal", "note")],
        color=("status", {"solved_ai": AI, "solved_human": HUMAN,
                          "unsolved": NEUTRAL}),
        href=True,
        height=max(220, 16 * len(values)),
    )
    return [("Per-problem status and solve dates", spec,
             "Rows are grouped by notability tier, most notable first. "
             "Unsolved problems sit at the right edge; click a point to open "
             "its page, hover for the system and notes.")]
