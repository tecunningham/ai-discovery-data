"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    HUMAN,
    NEUTRAL,
    load,
    num,
    record_steps,
    scatter,
)


def charts(slug: str):
    """Two Dujella frontiers on one chart, then the ICARM board's own cut."""
    def steps(name, sign):
        return [{"year": num(r["year"]), "rank": num(r["rank"]),
                 "frontier": f"rank {sign}",
                 "discoverer": r["discoverer"],
                 "credit": r.get("credit", "human"),
                 "url": r["source_url"]}
                for r in load(slug, name)]

    values = (steps("elliptic-curve-rank-records.csv", "at least")
              + steps("elliptic-curve-rank-exact.csv", "known exactly"))
    frontier = record_steps(
        values, x="year", x_type="quantitative", y="rank",
        y_title="Record rank", x_title="Year", href=True,
        color=("frontier", {"rank at least": HUMAN,
                            "rank known exactly": NEUTRAL}),
        tips=[("year", "quantitative", "year"),
              ("rank", "quantitative", "rank"),
              ("discoverer", "nominal", "discoverer"),
              ("frontier", "nominal", "frontier"),
              ("credit", "nominal", "credit")])
    frontier["layer"][0]["encoding"]["x"]["scale"] = {"zero": False}

    board = [{"rank": num(r["rank"]),
              "log_conductor": num(r["log_conductor"]),
              "naive_height": num(r["naive_height"]),
              "curve": f"#{r['curve_id']}",
              "submitter": r["submitter"], "date": r["date"]}
             for r in load(slug, "elliptic-rank-leaderboard.csv")
             if r["log_conductor"]]
    small = scatter(board, x="rank", x_type="quantitative",
                    y="log_conductor", y_type="quantitative",
                    y_title="log conductor", x_title="Rank (proved lower bound)",
                    tips=[("curve", "nominal", "curve"),
                          ("rank", "quantitative", "rank"),
                          ("log_conductor", "quantitative", "log conductor"),
                          ("naive_height", "quantitative", "naive height"),
                          ("submitter", "nominal", "submitted by"),
                          ("date", "nominal", "submitted")])
    return [
        ("Record rank over time", frontier,
         "Click a step for the curve and its independent points on Dujella's "
         "subpage."),
        ("Small curves of high rank", small,
         "Every curve on the ICARM leaderboard; its rank bound was certified "
         "by 2-descent before it was recorded."),
    ]
