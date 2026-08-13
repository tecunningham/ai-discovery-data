#!/usr/bin/env python3
"""Draw this folder's three figures from the AlphaEvolve record transcription.

Run: python3 problems/math-alphaevolve-records/figure.py

discovery-math-alphaevolve-related-records.png plots the five groups' steps;
alphaevolve-record-steps.png compares AI and human steps across the frame;
cumulative-math-alphaevolve-records.png pools the five groups' record steps
into one line, for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from lib.chart import (  # noqa: E402
    NEUTRAL,
    NOW,
    new_chart,
    record_marker,
    save,
    shade_era,
    source_note,
    stable_jitter,
    style,
)
from lib.cumulative import events_chart  # noqa: E402
from lib.table import read_csv  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

RECORDS = HERE / "alphaevolve-records.csv"


def cumulative() -> None:
    # The same five groups and record filter as related_groups(), pooled into
    # one line for the collection-wide cumulative index.
    selected = {"6.5", "6.7", "6.48", "6.49", "6.50"}
    rows = [
        row
        for row in read_csv(RECORDS)
        if row["problem"] in selected and row["year"] and row.get("is_record", "yes") == "yes"
    ]
    rows.sort(key=lambda row: (int(row["year"]), row["quantity"], int(row["step"])))
    events_chart(
        HERE / "cumulative-math-alphaevolve-records.png",
        title="AlphaEvolve-adjacent construction records: cumulative steps",
        ylabel="Record steps to date",
        dates=[row["year"] for row in rows],
        source_label="alphaevolve-records.csv",
        source_url="https://github.com/google-deepmind/alphaevolve_repository_of_problems",
        built_by=__file__,
    )


def related_groups() -> None:
    selected = {"6.5", "6.7", "6.48", "6.49", "6.50"}
    rows = [
        row
        for row in read_csv(RECORDS)
        if row["problem"] in selected and row["year"] and row.get("is_record", "yes") == "yes"
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["problem"]].append(row)
    fig, ax = new_chart(
        "Finite construction records around AlphaEvolve",
        "Cumulative record steps by problem group; values have incompatible units, so this plots discoveries rather than levels",
    )
    labels = {
        "6.5": "minimum-overlap type",
        "6.7": "difference basis",
        "6.48": "triangle packing",
        "6.49": "convex packing",
        "6.50": "max-min packing",
    }
    line_styles = ["-", "--", ":", "-.", (0, (3, 1, 1, 1))]
    for index, problem in enumerate(sorted(grouped)):
        local = sorted(grouped[problem], key=lambda row: (int(row["year"]), row["quantity"], int(row["step"])))
        xs = [int(row["year"]) for row in local]
        ys = list(range(1, len(local) + 1))
        ax.plot(
            xs + [NOW],
            ys + [ys[-1]],
            drawstyle="steps-post",
            color=NEUTRAL,
            linestyle=line_styles[index],
            linewidth=1.5,
            label=labels[problem],
        )
        for x, y, row in zip(xs, ys, local):
            record_marker(ax, x, y, row, size=45)
    right = 2030
    ax.set_xlim(min(int(row["year"]) for row in rows) - 5, right)
    shade_era(ax, right)
    style(ax, "Cumulative record steps in group")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(frameon=False, fontsize=7.3, ncol=2)
    ax.text(
        0.02,
        0.93,
        "Red points are AI-set records; blue points are human.\n"
        "The difference-basis step followed a supplied Singer-code hint.",
        transform=ax.transAxes,
        fontsize=8.3,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: alphaevolve-records.csv. Multiple quantities within a group are counted separately.")
    save(
        fig,
        HERE / "discovery-math-alphaevolve-related-records.png",
        "Cumulative record steps in selected finite construction and packing problems.",
        sorted({row["ref"] for row in rows if row["ref"]}),
        __file__,
    )


def record_steps() -> None:
    """AI record steps against human steps on the same quantities.

    A pre-committed sample of twelve AlphaEvolve problems plus the 2026-07-28
    extension that completes the record-status frame. Three sequence panels show
    representative head-to-heads (the richest contested quantity, the
    leapfrogging case, and the kissing number whose record has since moved to a
    collective agent platform); the right panel pools every record step in the
    frame. Steps flagged is_record=no (AlphaEvolve improving a cited value that
    was not the actual record) are excluded from the pool.
    """
    series: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in read_csv(RECORDS):
        series[(row["problem"], row["quantity"])].append(row)

    colours = {
        "ai_evolution": "#c1442f",
        "ai_guided_search": "#e0a020",
        "ai_agents": "#9467bd",
        "human_analytic": "#2f6cc1",
        "human_search": "#6f9fd8",
        "community_table": "#8c8c8c",
    }
    pretty = {
        "ai_evolution": "AlphaEvolve",
        "ai_guided_search": "AI-guided search",
        "ai_agents": "agent platform",
        "human_analytic": "human, by hand",
        "human_search": "human, computer search",
        "community_table": "records webpage",
    }

    fig, (ax_a, ax_b, ax_d, ax_c) = plt.subplots(
        1, 4, figsize=(18.4, 4.8), gridspec_kw={"width_ratios": [1, 1, 1, 1.15]}
    )

    def draw_sequence(ax, key, title):
        rows = series[key]
        xs = list(range(len(rows)))
        ys = [float(r["value"]) for r in rows]
        ax.plot(xs, ys, color="#bbb", lw=1.3, zorder=1)
        for x, y, row in zip(xs, ys, rows):
            ax.scatter([x], [y], s=78, color=colours.get(row["agent"], "#999"),
                       zorder=3, edgecolor="white", linewidth=0.9)
            ax.annotate(f"{row['year']}", (x, y), textcoords="offset points",
                        xytext=(0, -15), ha="center", fontsize=7.6, color="#666")
        ax.set_xticks(xs)
        ax.set_xticklabels([str(i) for i in xs], fontsize=8)
        ax.set_xlabel("Record step", fontsize=9.5)
        ax.set_title(title, fontsize=10.5, loc="left", pad=8)
        ax.grid(axis="y", alpha=0.22)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        pad = (max(ys) - min(ys)) * 0.22 or 0.01
        ax.set_ylim(min(ys) - pad, max(ys) + pad)

    draw_sequence(ax_a, ("6.44", "C_6.44"),
                  "6.44  sums and differences\nlower bound, higher is better")
    ax_a.set_ylabel("Best known value", fontsize=9.5)
    draw_sequence(ax_b, ("6.3", "C_6.3"),
                  "6.3  autoconvolution constant\nlower bound, higher is better")
    draw_sequence(ax_d, ("6.8", "K(11)"),
                  "6.8  kissing number, dimension 11\nlower bound, higher is better")

    # --- right: pooled step sizes over the whole frame ----------------------
    steps = [r for rows in series.values() for r in rows
             if r["relative_gain_pct"] and r.get("is_record", "yes") == "yes"]
    comparable_quantities = sum(
        any(row["agent"].startswith("ai_") for row in rows)
        and any(row["agent"].startswith("human_") for row in rows)
        for rows in (
            [row for row in local
             if row["relative_gain_pct"] and row.get("is_record", "yes") == "yes"]
            for local in series.values()
        )
    )
    order = ["ai_evolution", "ai_guided_search", "ai_agents",
             "human_search", "human_analytic"]
    for y, agent in enumerate(order):
        gains = [float(r["relative_gain_pct"]) for r in steps if r["agent"] == agent]
        if not gains:
            continue
        jitter = [stable_jitter(f"{agent}{i}") for i in range(len(gains))]
        ax_c.scatter(gains, [y + j for j in jitter], s=66,
                     color=colours[agent], alpha=0.85, zorder=3,
                     edgecolor="white", linewidth=0.7)
        median = sorted(gains)[len(gains) // 2]
        ax_c.plot([median, median], [y - 0.26, y + 0.26], color=colours[agent],
                  lw=2.4, zorder=4)
        ax_c.text(median, y + 0.34, f"median {median:+.2f}%", fontsize=8,
                  color=colours[agent], ha="center")
    ax_c.set_yticks(range(len(order)))
    ax_c.set_yticklabels([pretty[a] for a in order], fontsize=9.5)
    ax_c.set_ylim(-1.1, len(order) - 0.25)
    ax_c.set_xscale("symlog", linthresh=0.01)
    ax_c.set_xlabel("Relative improvement of the bound per record step (%)", fontsize=9.5)
    ax_c.set_title("Every record step in the frame, by who made it",
                   fontsize=10.5, loc="left", pad=8)
    ax_c.grid(axis="x", alpha=0.22)
    ax_c.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax_c.spines[spine].set_visible(False)
    ax_c.text(0.014, -0.8, "← the eighth-decimal gain on 6.30, and the\n"
                           "    +0.002% step that took 6.44 in 2025",
              fontsize=7.8, color="#888", va="center", linespacing=1.4)
    ax_a.legend(
        handles=[Line2D([], [], marker="o", ls="", color=colours[a], label=pretty[a])
                 for a in ("ai_evolution", "human_search", "human_analytic")],
        fontsize=8, frameon=False, loc="lower right",
    )
    ax_d.legend(
        handles=[Line2D([], [], marker="o", ls="", color=colours[a], label=pretty[a])
                 for a in ("ai_agents", "ai_guided_search")],
        fontsize=8, frameon=False, loc="lower right",
    )

    fig.suptitle(
        "AI record steps against human steps on the same quantity: the "
        "pre-committed 12-problem sample plus the 2026-07-28 frame completion\n"
        "Left three: representative contested sequences. Right: every record "
        f"step with a computable size, {comparable_quantities} quantities "
        "carrying both AI and non-AI steps.",
        fontsize=11.5, x=0.006, ha="left", y=0.995,
    )
    # tight_layout picks the margins this grid needs; save() then reapplies
    # exactly those, so the shared helper adds its renderer guard and PNG
    # provenance without changing the layout.
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    pars = fig.subplotpars
    save(
        fig,
        HERE / "alphaevolve-record-steps.png",
        "AI record steps against human steps on the same AlphaEvolve "
        "quantities: three contested sequences and every computable step size.",
        ["https://github.com/google-deepmind/alphaevolve_repository_of_problems",
         "https://arxiv.org/abs/2511.02864"],
        __file__,
        adjust={"left": pars.left, "right": pars.right, "top": pars.top,
                "bottom": pars.bottom, "wspace": pars.wspace,
                "hspace": pars.hspace},
    )


def main() -> None:
    related_groups()
    record_steps()
    cumulative()


if __name__ == "__main__":
    main()
