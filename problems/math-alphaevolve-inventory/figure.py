#!/usr/bin/env python3
"""Draw alphaevolve-frame-funnel.png from this folder's problem inventory.

Run: python3 problems/math-alphaevolve-inventory/figure.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402

import matplotlib  # noqa: E402

# The backend has to be fixed before pyplot is imported: an interactive one
# renders text differently and the committed PNG stops matching the CSV.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    """The AlphaEvolve problem set: what it contains, and what a baseline can use.

    Left: the status composition of the problems the paper numbers, from the
    repository's own status.json under the assumed index mapping. Right: how
    many survive each filter needed to compare an AI record step against the
    historical steps on the same quantity. Both read the inventory CSV; the last
    two funnel rows come from the record sample.
    """
    rows = read_csv(HERE / "alphaevolve-inventory.csv")
    counts = Counter(r["status"] or "unclassified" for r in rows)

    fig, (ax_status, ax_funnel) = plt.subplots(
        1, 2, figsize=(13.0, 4.6), gridspec_kw={"width_ratios": [1, 1.25]}
    )

    order = [("world_record", "AlphaEvolve holds the record", "#c1442f"),
             ("matched_optimal", "matched a known optimum", "#8c8c8c"),
             ("worse_than_record", "below the record", "#6f9fd8"),
             ("former_record", "record since surpassed", "#2f6cc1"),
             ("unclassified", "unclassified in status.json", "#cfcfcf")]
    for y, (key, lab, colour) in enumerate(order):
        value = counts.get(key, 0)
        ax_status.barh([y], [value], height=0.62, color=colour, zorder=3)
        ax_status.text(value + 0.4, y, str(value), va="center", fontsize=10,
                       color=colour if key != "unclassified" else "#999",
                       fontweight="bold")
    ax_status.set_yticks(range(len(order)))
    ax_status.set_yticklabels([o[1] for o in order], fontsize=9)
    ax_status.invert_yaxis()
    ax_status.set_xlim(0, max(counts.values()) + 6)
    ax_status.set_xlabel("Problems", fontsize=9.5)
    ax_status.set_title(f"What the set contains ({len(rows)} numbered in the paper)",
                        fontsize=11, loc="left", pad=8)
    ax_status.grid(axis="x", alpha=0.22)
    ax_status.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax_status.spines[spine].set_visible(False)
    live = sum(counts.get(k, 0) for k in
               ("world_record", "worse_than_record", "former_record"))
    ax_status.text(0.98, 0.985, f"{live} of the {len(rows)} have a live numeric record",
                   transform=ax_status.transAxes, ha="right", va="top",
                   fontsize=9, color="#333")

    stages = [
        ("Numbered in the paper", len(rows), "problems 6.1 to 6.65"),
        ("With a live numeric record", live, "the sampling frame"),
        ("Sampled, pre-committed", 12, "SHA-256 of a declared salt"),
        ("Yielded a record sequence", 6, "rest asymptotic or parameterised"),
        ("Both AI and human steps", 2, "the whole head-to-head"),
    ]
    for i, (name, value, note) in enumerate(stages):
        shade = "#c1442f" if value <= 12 else "#8c8c8c"
        ax_funnel.barh([i], [value], height=0.6, color=shade,
                       alpha=0.85 if value <= 12 else 0.45, zorder=3)
        ax_funnel.text(value + 1.4, i, str(value), va="center", fontsize=10,
                       color=shade, fontweight="bold")
        ax_funnel.text(value + 8.0, i, note, va="center", fontsize=8.4, color="#777")
    ax_funnel.set_yticks(range(len(stages)))
    ax_funnel.set_yticklabels([s[0] for s in stages], fontsize=9)
    ax_funnel.invert_yaxis()
    ax_funnel.set_xlim(0, 96)
    ax_funnel.set_xlabel("Problems", fontsize=9.5)
    ax_funnel.set_title("What survives each filter a historical baseline needs",
                        fontsize=11, loc="left", pad=8)
    ax_funnel.grid(axis="x", alpha=0.22)
    ax_funnel.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax_funnel.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(HERE / "alphaevolve-frame-funnel.png", dpi=170)
    plt.close(fig)
    print(f"wrote alphaevolve-frame-funnel ({len(rows)} problems, {live} in frame)")


if __name__ == "__main__":
    main()
