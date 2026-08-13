#!/usr/bin/env python3
"""Draw discovery-algorithms-ecdsa-circuit.png and
cumulative-algorithms-ecdsa-circuit.png from this folder's record table.

Run: python3 problems/algorithms-ecdsa-circuit/figure.py

The whole series sits inside the agent era, so the usual year axis would
compress it to a sliver; this plots calendar days in 2026 instead, with the
month ticks the other figures put on a year axis.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AI,
    NEUTRAL,
    new_chart,
    save,
    source_note,
    style,
    year_fraction,
)
from lib.cumulative import staircase_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import LogFormatterSciNotation, NullFormatter  # noqa: E402

# Reference points from the challenge README: the textbook circuit it ships
# with, and Google's published low-qubit Pareto point, the best prior circuit.
BASELINE_SCORE = 10_753_444_395
GOOGLE_PARETO = 3_000_000_000


def day_offset(value: str, origin: date) -> int:
    return (date.fromisoformat(value) - origin).days


def cumulative() -> None:
    rows = read_csv(HERE / "ecdsa-circuit-records.csv")
    staircase_chart(
        HERE / "cumulative-algorithms-ecdsa-circuit.png",
        title="ECDSA.fail circuit score: standing record",
        subtitle="Average Toffoli count × peak qubits for a validated "
                 "reversible circuit; lower is better",
        ylabel="Best validated score (lower is better)",
        series=[("", [year_fraction(row["date"]) for row in rows],
                 [float(row["score"]) for row in rows])],
        ylog=True,
        source_label="ecdsa.fail challenge API (Eigen Labs); one accepted "
                     "submission per record, vendored as "
                     "ecdsa-circuit-records.csv",
        source_url="https://ecdsa.fail/",
        built_by=__file__,
        note="Lower is better; score = Toffoli count × peak qubit width.",
    )


def main() -> None:
    rows = read_csv(HERE / "ecdsa-circuit-records.csv")
    origin = date.fromisoformat(rows[0]["date"])
    xs = [day_offset(row["date"], origin) for row in rows]
    ys = [int(row["score"]) for row in rows]
    fig, ax = new_chart(
        "ECDSA.fail: leanest secp256k1 point-addition circuit",
        "Average Toffoli count × peak qubits for a validated reversible "
        "circuit; lower is better",
    )
    right = max(xs) + 3
    ax.axhline(BASELINE_SCORE, color=NEUTRAL, linewidth=1.0, linestyle="--")
    ax.text(1, BASELINE_SCORE * 1.03, "challenge starting circuit",
            fontsize=7.5, color="#777777", va="bottom")
    ax.axhline(GOOGLE_PARETO, color=NEUTRAL, linewidth=1.0, linestyle=":")
    ax.text(right, GOOGLE_PARETO * 1.03,
            "Google's published low-qubit point", fontsize=7.5,
            color="#777777", va="bottom", ha="right")

    ax.plot(xs, ys, drawstyle="steps-post", color=NEUTRAL, linewidth=1.3,
            zorder=2)
    for x, y, row in zip(xs, ys, rows):
        named = row["ai_tool_in_note"] == "yes"
        ax.scatter([x], [y], s=20, color=AI if named else NEUTRAL,
                   edgecolor="white", linewidth=0.4,
                   zorder=4 if named else 3)

    ax.set_xlim(-2, right)
    ax.set_yscale("log")
    ax.set_ylim(ys[-1] * 0.8, BASELINE_SCORE * 1.35)
    ax.yaxis.set_major_formatter(LogFormatterSciNotation())
    ax.yaxis.set_minor_formatter(NullFormatter())

    # Month ticks, since a day count is not a reading a person does by eye.
    # The origin gets its own tick, and a month-first within a few days of it
    # is dropped so the two labels do not overprint.
    ticks = [(0, origin.strftime("%b %-d"))]
    for month in (6, 7, 8):
        first = date(2026, month, 1)
        offset = (first - origin).days
        if 5 <= offset <= right:
            ticks.append((offset, first.strftime("%b %-d")))
    ax.set_xticks([tick for tick, _ in ticks])
    ax.set_xticklabels([label for _, label in ticks])
    style(ax, "Score (Toffoli × qubits, log scale)", "2026")

    named = sum(1 for row in rows if row["ai_tool_in_note"] == "yes")
    solvers = len({row["solver"] for row in rows})
    ax.legend(handles=[
        Line2D([], [], marker="o", linestyle="", color=AI,
               label="note names an AI tool"),
        Line2D([], [], marker="o", linestyle="", color=NEUTRAL,
               label="no such note"),
    ], frameon=False, fontsize=8, loc="upper right")
    ax.text(
        0.33, 0.70,
        f"{len(rows)} record steps in {max(xs)} days, "
        f"{ys[0] / ys[-1]:.1f}× lower;\n{solvers} solvers, "
        f"{named} notes name an AI tool.",
        transform=ax.transAxes, fontsize=8.5, va="top")
    source_note(fig, "Source: ecdsa.fail challenge API (Eigen Labs); one "
                     "accepted submission per record, vendored as "
                     "ecdsa-circuit-records.csv.")
    save(
        fig,
        HERE / "discovery-algorithms-ecdsa-circuit.png",
        "Record ladder for the ecdsa.fail secp256k1 point-addition circuit "
        "challenge.",
        ["https://ecdsa.fail/"],
        __file__,
    )


if __name__ == "__main__":
    main()
    cumulative()
