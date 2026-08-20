#!/usr/bin/env python3
"""Draw this folder's three PNGs from its three CSVs.

Run: make figure PROBLEM=math-elliptic-rank
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib.lines import Line2D  # noqa: E402

from lib.chart import (  # noqa: E402
    AI,
    AI_SOFT,
    HUMAN,
    NEUTRAL,
    NOW,
    VENDOR,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
)
from lib.cumulative import staircase_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

RECORDS = "elliptic-curve-rank-records.csv"
EXACT = "elliptic-curve-rank-exact.csv"
BOARD = "elliptic-rank-leaderboard.csv"

DUJELLA = "https://web.math.pmf.unizg.hr/~duje/tors/rankhist.html"
LEADERBOARD = "https://elliptic-rank.icarm.cloud/database.json"

# A record credited to an AI on the finder's own unverified word is drawn in the
# collection's soft red rather than its AI red: the same family, visibly weaker
# evidence. The credit_evidence column, not the credit column, picks the colour.
CREDIT_COLOURS = {("human", "published"): HUMAN,
                  ("ai", "published"): AI,
                  ("ai", "self-reported"): AI_SOFT}

# discoverer -> (label, offset, alignment). The latest record wins when a name
# appears more than once, as with Mestre and Nagao.
LABELS = {
    "Billing": ("Billing", (6, 4), "left"),
    "Mestre": ("Mestre", (7, -3), "left"),
    "Martin–McMillen": ("Martin–McMillen", (5, -12), "left"),
    "Elkies": ("Elkies", (6, -10), "left"),
    "ranksunbounded": ("ranksunbounded\n(AI-credited)", (-9, -52), "right"),
}


def colour_of(row: dict[str, str]) -> str:
    return CREDIT_COLOURS[(row["credit"], row["credit_evidence"])]


def legend_handles():
    dot = lambda colour, label: Line2D(  # noqa: E731
        [], [], marker="o", linestyle="", color=colour, label=label)
    return [
        dot(HUMAN, "human-credited record"),
        dot(AI_SOFT, "AI-credited, self-reported"),
        Line2D([], [], color=VENDOR, linestyle="--",
               label="rank known exactly"),
    ]


def cumulative() -> None:
    records = read_csv(HERE / RECORDS)
    exact = read_csv(HERE / EXACT)
    staircase_chart(
        HERE / "cumulative-math-elliptic-rank.png",
        title="Elliptic-curve rank records: standing record",
        subtitle="Largest rank exhibited for a curve over Q; higher is better",
        ylabel="Record rank",
        series=[
            ("rank at least", [float(row["year"]) for row in records],
             [float(row["rank"]) for row in records]),
            ("rank known exactly", [float(row["year"]) for row in exact],
             [float(row["rank"]) for row in exact]),
        ],
        source_label=f"{RECORDS} and {EXACT}, from Dujella's rank tables",
        source_url=DUJELLA,
        built_by=__file__,
        note="The 2026 step is AI-credited on the finder's own account.",
    )


def frontier() -> None:
    records = read_csv(HERE / RECORDS)
    exact = read_csv(HERE / EXACT)
    years = [int(row["year"]) for row in records]
    ranks = [int(row["rank"]) for row in records]
    fig, ax = new_chart(
        "Elliptic-curve rank records",
        "Largest rank exhibited for an elliptic curve over Q; higher is better",
    )
    ax.plot(years + [NOW], ranks + [ranks[-1]], drawstyle="steps-post",
            color=HUMAN, linewidth=2)
    ax.plot([int(row["year"]) for row in exact] + [NOW],
            [int(row["rank"]) for row in exact] + [int(exact[-1]["rank"])],
            drawstyle="steps-post", color=VENDOR, linestyle="--", linewidth=1.4)
    for key, colour in CREDIT_COLOURS.items():
        pts = [(int(row["year"]), int(row["rank"])) for row in records
               if (row["credit"], row["credit_evidence"]) == key]
        if pts:
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], color=colour,
                       s=45, edgecolor="white", linewidth=0.6, zorder=4)
    for target, (label, offset, align) in LABELS.items():
        row = next(row for row in reversed(records)
                   if row["discoverer"] == target)
        ax.annotate(label, (int(row["year"]), int(row["rank"])),
                    xytext=offset, textcoords="offset points", ha=align,
                    fontsize=7.5, color=colour_of(row))
    right = 2032
    ax.set_xlim(1932, right)
    ax.set_ylim(0, 34)
    shade_era(ax, right)
    style(ax, "Record rank")
    ax.legend(handles=legend_handles(), frameon=False, fontsize=8, loc="upper left")
    # Counted at plot time, so a refetch that adds a record cannot leave the
    # annotation asserting a stale count.
    late = [year for year in years if year > 2000]
    early = [year for year in years if 1974 <= year <= 2000]
    ai_years = [row["year"] for row in records if row["credit"] == "ai"]
    ax.text(
        0.98,
        0.06,
        f"{len(early)} record steps over 1974–2000, {len(late)} since;\n"
        f"{len(ai_years)} AI-credited step ({', '.join(ai_years)}) "
        "in the series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, f"Source: {RECORDS} and {EXACT}, transcribed from "
                     "Dujella's rank-records tables.")
    save(fig, HERE / "discovery-math-elliptic-rank.png",
         "Record rank of an elliptic curve over Q from 1938 to 2026.",
         sorted({row["source_url"] for row in records + exact}), __file__)


def board() -> None:
    """The second frontier: how small a curve of each rank anyone has found."""
    rows = [row for row in read_csv(HERE / BOARD) if row["log_conductor"]]
    ranks = [int(row["rank"]) for row in rows]
    sizes = [float(row["log_conductor"]) for row in rows]
    best: dict[int, float] = {}
    for rank, size in zip(ranks, sizes):
        best[rank] = min(size, best.get(rank, size))
    fig, ax = new_chart(
        "Small curves of high rank",
        "Every curve on the ICARM leaderboard; smaller conductor is better",
    )
    ax.scatter(ranks, sizes, s=18, color=NEUTRAL, alpha=0.75,
               edgecolor="white", linewidth=0.4, zorder=3)
    ordered = sorted(best)
    ax.plot(ordered, [best[rank] for rank in ordered], color=HUMAN,
            linewidth=1.6, zorder=4)
    ax.scatter(ordered, [best[rank] for rank in ordered], s=32, color=HUMAN,
               edgecolor="white", linewidth=0.6, zorder=5)
    # Which board curve carries the AI credit is decided by the record CSV, not
    # by the board: the board records who submitted a curve, never how it was
    # found. Highlight the board's curve at each AI-credited record rank.
    credited = {int(row["rank"]) for row in read_csv(HERE / RECORDS)
                if row["credit"] == "ai"}
    for row in rows:
        if int(row["rank"]) not in credited:
            continue
        rank, size = int(row["rank"]), float(row["log_conductor"])
        ax.scatter([rank], [size], s=70, color=AI_SOFT, edgecolor="white",
                   linewidth=0.8, zorder=6)
        ax.annotate(f"curve #{row['curve_id']} (AI-credited)", (rank, size),
                    xytext=(-9, 11), textcoords="offset points", ha="right",
                    fontsize=7.5, color=AI_SOFT)
    # Headroom above the top record so the AI-credited label sits clear
    # of the rising record line rather than crossing it.
    ax.set_ylim(-18, 400)
    style(ax, "log conductor", xlabel="Rank (proved lower bound)")
    ax.legend(handles=[
        Line2D([], [], marker="o", linestyle="", color=NEUTRAL,
               label="submitted curve"),
        Line2D([], [], marker="o", color=HUMAN, label="smallest at that rank"),
        Line2D([], [], marker="o", linestyle="", color=AI_SOFT,
               label="AI-credited, self-reported"),
    ], frameon=False, fontsize=8, loc="upper left")
    ax.text(
        0.98,
        0.06,
        f"{len(rows)} curves with a recorded conductor,\n"
        f"covering ranks {min(ranks)} to {max(ranks)}.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, f"Source: {BOARD}, from the ICARM Elliptic Curve Rank "
                     "Leaderboard; rank bounds certified by 2-descent.")
    save(fig, HERE / "leaderboard-math-elliptic-rank.png",
         "Conductor against proved rank for every curve on the ICARM "
         "leaderboard.", [LEADERBOARD], __file__)


if __name__ == "__main__":
    frontier()
    board()
    cumulative()
