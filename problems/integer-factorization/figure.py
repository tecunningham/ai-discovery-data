#!/usr/bin/env python3
"""Draw discovery-integer-factorization.png from the RSA record list.

Run: python3 problems/integer-factorization/figure.py

The line is the running maximum, which is the record series. The open markers
behind it are every published factorization of an RSA number, record or not, so
that a flat line cannot be read as nobody working: the smaller numbers went on
being factored while the record stood still.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib.lines import Line2D  # noqa: E402

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    NEUTRAL,
    NOW,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402

RIGHT = 2029.0
LABELLED = ("RSA-100", "RSA-768", "RSA-250")
# The rate split the sources use: RSA-768 in December 2009 ends the fast era.
MIDPOINT = "RSA-768"


def main() -> None:
    rows = sorted(
        (row for row in read_csv(HERE / "factoring-records.csv")
         if row["domain"] == "integer_factorization"),
        key=lambda row: row["date"],
    )

    records = []
    best = 0
    for row in rows:
        digits = int(row["digits"])
        if digits > best:
            best = digits
            records.append((year_fraction(row["date"]), digits, row["record"]))

    fig, ax = new_chart(
        "Integer factorization records",
        "Largest hard semiprime factored; a scoreboard with instant verification "
        "that stopped moving in 2020",
    )

    ax.scatter([year_fraction(row["date"]) for row in rows],
               [int(row["digits"]) for row in rows],
               s=26, facecolor="none", edgecolor=NEUTRAL, lw=1.0, zorder=2)
    ax.plot([x for x, _, _ in records] + [NOW],
            [d for _, d, _ in records] + [records[-1][1]],
            drawstyle="steps-post", color=HUMAN, lw=2.0, zorder=3)
    ax.scatter([x for x, _, _ in records], [d for _, d, _ in records], s=34,
               color=HUMAN, zorder=4, edgecolor="white", lw=0.5)
    for x, digits, name in records:
        if name in LABELLED:
            ax.annotate(name, (x, digits), textcoords="offset points",
                        xytext=(-5, 9), fontsize=7.6, color=HUMAN, ha="right")

    stalled = NOW - records[-1][0]
    ax.annotate(f"no new record in {stalled:.0f} years",
                (records[-1][0] + stalled / 2, records[-1][1]),
                textcoords="offset points", xytext=(16, 14), fontsize=8.4,
                color=AI, ha="center")

    middle = next(record for record in records if record[2] == MIDPOINT)
    early = (middle[1] - records[0][1]) / (middle[0] - records[0][0])
    late = (records[-1][1] - middle[1]) / (records[-1][0] - middle[0])
    machine_learning = [row for row in rows if row["ai_involved"] != "no"]
    ax.text(0.03, 0.94,
            f"{len(records)} records, {int(records[0][0])}–{int(records[-1][0])}: "
            f"{early:.1f} digits a year to {int(middle[0])},\n"
            f"then {late:.1f} a year, then none. "
            f"{len(machine_learning) or 'None'} of them involved machine "
            "learning;\nevery one is the number field sieve run as a large "
            "parallel computation.",
            transform=ax.transAxes, fontsize=8.2, color="#333333", va="top",
            linespacing=1.5)

    ax.set_xlim(1988, RIGHT)
    ax.set_ylim(80, 300)
    shade_era(ax, RIGHT)
    style(ax, "Digits in the largest number factored")
    ax.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="-", color=HUMAN,
                   label="the record: running maximum"),
            Line2D([], [], marker="o", linestyle="", markerfacecolor="none",
                   markeredgecolor=NEUTRAL,
                   label="every published RSA factorization, record or not"),
        ],
        loc="lower right", bbox_to_anchor=(1.0, 0.02), frameon=False, fontsize=8,
    )
    source_note(
        fig,
        "Source: the RSA Factoring Challenge record list and the record-setters' own "
        "announcements. Rates are computed here from the running maximum.",
    )
    save(
        fig,
        HERE / "discovery-integer-factorization.png",
        "Integer factorization records: the running maximum in decimal digits, "
        "1991-2020, flat thereafter.",
        [
            "https://en.wikipedia.org/wiki/RSA_numbers",
            "https://caramba.loria.fr/rsa250.txt",
        ],
        __file__,
    )


if __name__ == "__main__":
    main()
