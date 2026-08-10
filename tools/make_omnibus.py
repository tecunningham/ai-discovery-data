#!/usr/bin/env python3
"""Multi-series figures: comparisons that put several series in one frame.

Run: python3 tools/make_omnibus.py   (or: make figures)

The split from make_figures.py is by scope, not by style. That file draws one
series per chart, so a reader can check a single claim; this one draws the
cross-series comparisons — the per-domain keystones, the four problem sets side
by side, the rate comparisons — where the point is the contrast between series
and no single chart stands alone.

These were built in the blog repository until 2026-08-10 and moved here so the
data and the code that reads it live together. Output goes to figures/, and the
blog receives copies through tools/sync_to_blog.py.
"""

from __future__ import annotations

import csv
import json
import math
import re
import zlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"

# Every time-series figure uses the same highlighted period. For annual bar
# charts, January 1 falls at the left edge of the 2026 bar (2025.5 on a
# year-centred categorical axis); continuous-date panels use exactly 2026.0.
HIGHLIGHT_START = 2026.0
ANNUAL_BAR_HIGHLIGHT_START = 2025.5
HIGHLIGHT_LABEL = "2026 onward"


def stable_jitter(key: str, spread: float = 0.035) -> float:
    """Deterministic cosmetic offset for overlapping points.

    Python's hash() is seeded per process, so using it here made the same
    data produce a different PNG on every run, which defeats checking a
    committed figure against the CSV it came from.
    """
    return (zlib.crc32(key.encode()) % 7 - 3) * spread

# Halving times in months for algorithmic-efficiency measures, each quoted in
# the entry named alongside it. None where the source publishes no interval.
AI_RATES = [
    ("Language model pretraining\ncompute to fixed loss", 8.0, (5.0, 14.0),
     2012, 2023, "src-algo-progress"),
    ("ImageNet compute-augmenting\nalgorithmic advances", 9.0, (4.0, 25.0),
     2012, 2022, "src-vision-progress"),
    ("Compute to reach\nAlexNet-level accuracy", 16.0, None,
     2012, 2019, "src-alexnet-efficiency"),
]
MOORE_MONTHS = 24.0

def owid_rates() -> list[tuple[str, float, int, int]]:
    """Halving time in months per technology, fitted from the OWID CSV.

    Returns (name, halving_months, first_year, last_year) for series that fall
    in cost, sorted fastest first. A log-linear fit is used rather than an
    endpoint ratio so that a noisy first or last observation cannot set the
    rate on its own.
    """
    import csv
    from collections import defaultdict
    from math import log

    series: dict[str, list[tuple[int, float]]] = defaultdict(list)
    with (ROOT / "data/owid-66-technologies.csv").open() as fh:
        for row in csv.DictReader(fh):
            try:
                cost = float(row["Technology cost"])
            except (TypeError, ValueError):
                continue
            if cost > 0:
                series[row["Entity"]].append((int(row["Year"]), cost))

    out = []
    for name, points in series.items():
        if len(points) < 5:
            continue
        points.sort()
        years = [y for y, _ in points]
        logs = [log(c) for _, c in points]
        n = len(points)
        ybar, lbar = sum(years) / n, sum(logs) / n
        denom = sum((y - ybar) ** 2 for y in years)
        if denom == 0:
            continue
        slope = sum((y - ybar) * (l - lbar) for y, l in zip(years, logs)) / denom
        if slope >= 0:  # cost rising: no halving time exists
            continue
        out.append((name, 12 * log(2) / -slope, years[0], years[-1]))
    out.sort(key=lambda r: r[1])
    return out


def efficiency_rates() -> None:
    """How fast efficiency improves, across physical technologies and AI.

    Left: the window each measurement covers. Right: halving times on a log
    axis, with published 95% intervals where the source gives one. Only the
    fastest physical curves are shown; the rest of the 64 falling series are
    slower than everything plotted, and several are so nearly flat that a
    fitted halving time runs to centuries and means nothing.
    """
    from matplotlib.ticker import NullLocator

    owid = owid_rates()
    fastest = owid[:7]
    ai = [(n.replace("\n", " "), m, ci, a, b) for n, m, ci, a, b, _ in AI_RATES]

    fig, (ax_span, ax_rate) = plt.subplots(
        1, 2, figsize=(11.8, 5.0), gridspec_kw={"width_ratios": [1, 1.06]}
    )

    # --- left: when each measurement applies ---------------------------------
    rows = ([(n, m, a, b, "#2f6cc1") for n, m, a, b in fastest]
            + [(n, m, a, b, "#c1442f") for n, m, _, a, b in ai])
    for i, (name, months, first, last, colour) in enumerate(rows):
        y = len(rows) - i
        ax_span.plot([first, last], [y, y], lw=4, solid_capstyle="butt", color=colour)
        ax_span.text(first - 2, y, name, ha="right", va="center", fontsize=9,
                     color=colour)
        ax_span.text(last + 2, y, f"{months:.0f} mo", ha="left", va="center",
                     fontsize=9, color=colour)
    ax_span.axhline(len(ai) + 0.5, color="#ddd", lw=1)
    ax_span.set_xlim(1955, 2048)
    ax_span.set_ylim(0.2, len(rows) + 0.8)
    ax_span.set_yticks([])
    ax_span.set_xticks([1960, 1980, 2000, 2020])
    ax_span.set_xlabel("Years covered by the measurement", fontsize=9.5)
    ax_span.set_title("Each rate is measured over its own window",
                      fontsize=11, loc="left", pad=8)
    for spine in ("top", "right", "left"):
        ax_span.spines[spine].set_visible(False)
    ax_span.grid(axis="x", alpha=0.22)
    ax_span.set_axisbelow(True)

    # --- right: halving times, log axis --------------------------------------
    bars = ([(n, m, ci, "#c1442f") for n, m, ci, _, _ in ai]
            + [(n, m, None, "#2f6cc1") for n, m, _, _ in fastest[:5]])
    bars.sort(key=lambda r: -r[1])
    for y, (name, months, ci, colour) in enumerate(bars):
        if ci:
            ax_rate.plot(list(ci), [y, y], lw=2.4, color=colour, alpha=0.3,
                         solid_capstyle="round")
            ax_rate.text(ci[1] * 1.09, y, f"{months:.0f} mo  [{ci[0]:.0f}–{ci[1]:.0f}]",
                         va="center", fontsize=8.5, color=colour)
        else:
            ax_rate.text(months * 1.09, y, f"{months:.0f} mo", va="center",
                         fontsize=8.5, color=colour)
        ax_rate.scatter([months], [y], s=46, color=colour, zorder=3)
    ax_rate.axvline(MOORE_MONTHS, color="#666", ls="--", lw=1.1, zorder=1)
    ax_rate.text(MOORE_MONTHS * 0.96, -0.75, "Moore's law, 24 mo", fontsize=8.5,
                 color="#666", ha="right")
    ax_rate.set_yticks(range(len(bars)))
    ax_rate.set_yticklabels([b[0] for b in bars], fontsize=9)
    ax_rate.set_xscale("log")
    ax_rate.set_xlim(3.2, 78)
    ax_rate.xaxis.set_minor_locator(NullLocator())
    ax_rate.set_xticks([4, 8, 16, 32, 64])
    ax_rate.set_xticklabels(["4", "8", "16", "32", "64"])
    ax_rate.set_ylim(-1.4, len(bars) - 0.4)
    ax_rate.set_xlabel("Months to halve cost or compute (log scale)", fontsize=9.5)
    ax_rate.set_title("Fast, but inside the historical range", fontsize=11,
                      loc="left", pad=8)
    for spine in ("top", "right", "left"):
        ax_rate.spines[spine].set_visible(False)
    ax_rate.grid(axis="x", alpha=0.22)
    ax_rate.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(OUT / "efficiency-halving-times.png", dpi=170)
    plt.close(fig)

    print("fastest falling cost curves (halving months, span):")
    for name, months, first, last in owid[:8]:
        print(f"  {name:26s} {months:6.1f}  {first}-{last}")
    print(f"  ... {len(owid)} series fall in cost overall")


def problem_sets() -> None:
    """Each independent problem set on its own panel, raw, over one time axis.

    The four sets in this log are not commensurable and should not share a
    y-axis: analytic-number-theory exponents, the AlphaEvolve problems, the
    physical technology cost curves, and the AI algorithmic-efficiency
    estimates. Here each gets a panel, one row per problem, and the x-axis is
    calendar year throughout so the sets can be compared on coverage and timing
    without being mixed.

    Missing data is drawn, not omitted, because it is most of the story:
      filled dot      a dated improvement
      solid line      value known, unchanged over this stretch
      open dot        an improvement whose date could not be established
      dotted line     no dated series available for this problem at all
      x               problem in the set but no scalar record exists
    """
    import csv
    from collections import defaultdict

    ANTEDB = ROOT / "data/antedb-sweep.csv"
    RECORDS = ROOT / "data/alphaevolve-records.csv"
    OWID = ROOT / "data/owid-66-technologies.csv"
    if not (ANTEDB.exists() and RECORDS.exists()):
        print("skipped problem sets: run the extraction scripts first")
        return

    NOW = 2026
    fig = plt.figure(figsize=(13.6, 15.0))
    grid = fig.add_gridspec(4, 1, height_ratios=[30, 14, 17, 5], hspace=0.30)
    ax_ant = fig.add_subplot(grid[0])
    ax_ae = fig.add_subplot(grid[1], sharex=ax_ant)
    ax_owid = fig.add_subplot(grid[2], sharex=ax_ant)
    ax_ai = fig.add_subplot(grid[3], sharex=ax_ant)

    def dress(ax, title, note=""):
        ax.set_xlim(1915, 2032)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.grid(axis="x", alpha=0.20)
        ax.set_axisbelow(True)
        # Title above the note, both left-aligned, so neither collides with the
        # tick labels of the panel above.
        ax.set_title(title, fontsize=11.5, loc="left", pad=20)
        if note:
            ax.text(0, 1.008, note, transform=ax.transAxes, ha="left",
                    va="bottom", fontsize=8.6, color="#777")

    def row(ax, y, years, colour, last_known=NOW):
        """One problem's history: a line through its known span, dots at changes."""
        if not years:
            return
        ax.plot([min(years), last_known], [y, y], color=colour, lw=1.1,
                alpha=0.55, zorder=2)

    # ---- 1. ANTEDB exponents ------------------------------------------------
    series: dict[tuple[str, float], list[tuple[int, float]]] = defaultdict(list)
    with ANTEDB.open(encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            series[(r["quantity"], float(r["point_float"]))].append(
                (int(r["year"]), float(r["value_float"])))
    for key in series:
        series[key].sort()

    wanted = {
        "mu": [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.975],
        "A": [0.525, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975],
        "beta": [0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.325, 0.4, 0.475],
    }
    sym = {"mu": r"\mu", "A": "A", "beta": r"\beta"}
    colour = {"mu": "#2f6cc1", "A": "#e0a020", "beta": "#2f8f5b"}
    frac_of = {0.5: "1/2", 0.525: "21/40", 0.55: "11/20", 0.6: "3/5", 0.65: "13/20",
               0.7: "7/10", 0.75: "3/4", 0.8: "4/5", 0.85: "17/20", 0.875: "7/8",
               0.9: "9/10", 0.95: "19/20", 0.975: "39/40", 0.025: "1/40",
               0.05: "1/20", 0.1: "1/10", 0.15: "3/20", 0.2: "1/5", 0.25: "1/4",
               0.3: "3/10", 0.325: "13/40", 0.4: "2/5", 0.475: "19/40"}
    labels, y = [], 0
    for quantity in ("mu", "A", "beta"):
        points = sorted(k[1] for k in series if k[0] == quantity)
        for target in wanted[quantity]:
            if not points:
                continue
            point = min(points, key=lambda p: abs(p - target))
            rows = series[(quantity, point)]
            row(ax_ant, y, [r[0] for r in rows], colour[quantity])
            ax_ant.scatter([r[0] for r in rows], [y] * len(rows), s=26,
                           color=colour[quantity], zorder=4,
                           edgecolor="white", linewidth=0.5)
            if len(rows) == 1:
                ax_ant.scatter([NOW - 1], [y], marker="x", s=34, color="#999",
                               zorder=4, linewidth=1.2)
            labels.append(f"${sym[quantity]}({frac_of.get(point, round(point, 3))})$")
            y += 1
    ax_ant.set_yticks(range(len(labels)))
    ax_ant.set_yticklabels(labels, fontsize=7.8)
    ax_ant.set_ylim(-0.8, len(labels) - 0.2)
    dress(ax_ant, "Set 1  Analytic number theory exponents (ANTEDB)",
          "30 of 58 grid points shown · every value derivable from the "
          "literature of that year · no AI anywhere in this panel")

    # ---- 2. AlphaEvolve sampled problems ------------------------------------
    ae: dict[str, list[dict]] = defaultdict(list)
    with RECORDS.open(encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            ae[r["problem"]].append(r)
    agent_colour = {"ai_evolution": "#c1442f", "human_analytic": "#2f6cc1",
                    "human_search": "#6f9fd8", "community_table": "#8c8c8c"}
    UNDATED_X = 2029.2
    ax_ae.axvspan(2027.4, 2031.4, color="#000", alpha=0.045, zorder=0)
    ax_ae.text(UNDATED_X, len(ae) - 0.4, "date\nunknown", fontsize=7.4,
               color="#888", ha="center", va="bottom", linespacing=1.3)
    ae_order = sorted(ae, key=lambda p: (ae[p][0]["agent"] == "no_sequence",
                                         float(p.split(".")[1])))
    for y, problem in enumerate(ae_order):
        rows = ae[problem]
        if rows[0]["agent"] == "no_sequence":
            ax_ae.plot([1915, NOW], [y, y], color="#bbb", lw=1.0, ls=":", zorder=2)
            ax_ae.scatter([NOW - 1], [y], marker="x", s=42, color="#999",
                          zorder=4, linewidth=1.4)
            ax_ae.text(1918, y + 0.30, f"no scalar record — {rows[0]['attribution']}",
                       fontsize=7.4, color="#999", va="center")
            continue
        dated = [r for r in rows if r["year"] and r["date_certain"] == "yes"]
        undated = [r for r in rows if r["year"] and r["date_certain"] == "no"]
        if dated:
            ax_ae.plot([min(int(r["year"]) for r in dated), NOW], [y, y],
                       color="#888", lw=1.0, alpha=0.55, zorder=2)
        for r in dated:
            ax_ae.scatter([int(r["year"])], [y], s=48,
                          color=agent_colour.get(r["agent"], "#999"), zorder=4,
                          edgecolor="white", linewidth=0.6)
        for r in undated:
            # Plotting these at their placeholder year would read as a date the
            # source does not support, so they sit in a gutter outside the axis.
            ax_ae.scatter([UNDATED_X], [y], s=52, facecolor="none",
                          edgecolor=agent_colour.get(r["agent"], "#999"),
                          zorder=4, linewidth=1.3)
    ax_ae.set_yticks(range(len(ae_order)))
    ax_ae.set_yticklabels(ae_order, fontsize=8.4)
    ax_ae.set_ylim(-0.8, len(ae_order) - 0.2)
    dress(ax_ae, "Set 2  AlphaEvolve problems, pre-committed sample of 12",
          "6 of 12 yielded no scalar record · several steps share 2025 · "
          "2 steps have no establishable date")

    # ---- 3. OWID physical technology cost curves ----------------------------
    if OWID.exists():
        spans: dict[str, list[int]] = defaultdict(list)
        with OWID.open(encoding="utf-8") as handle:
            for r in csv.DictReader(handle):
                name = r.get("Entity") or r.get("entity") or ""
                year = r.get("Year") or r.get("year")
                if name and year and year.strip().lstrip("-").isdigit():
                    spans[name].append(int(year))
        ordered = sorted(spans, key=lambda n: min(spans[n]))
        for y, name in enumerate(ordered):
            years = spans[name]
            ax_owid.plot([min(years), max(years)], [y, y], color="#2f6cc1",
                         lw=2.0, alpha=0.55, solid_capstyle="butt", zorder=2)
        ax_owid.set_yticks([])
        ax_owid.set_ylim(-1.5, len(ordered) + 0.5)
        ax_owid.text(1917, len(ordered) - 1.5,
                     f"{len(ordered)} series, each a continuous annual cost curve\n"
                     "labels omitted; ordered by start year",
                     fontsize=8.6, color="#2f6cc1", va="top")
        dress(ax_owid, "Set 3  Physical technology cost curves (Santa Fe / OWID)",
              "all end by 2013 · none overlaps the AI era · no AI anywhere in this panel")
    else:
        ax_owid.axis("off")

    # ---- 4. AI algorithmic efficiency estimates -----------------------------
    for y, (name, months, ci, first, last, _anchor) in enumerate(AI_RATES):
        ax_ai.plot([first, last], [y, y], color="#c1442f", lw=3.0,
                   solid_capstyle="butt", zorder=3)
        ax_ai.text(last + 1.5, y, f"{months:.0f}-month halving", fontsize=8.4,
                   color="#c1442f", va="center")
    ax_ai.set_yticks(range(len(AI_RATES)))
    ax_ai.set_yticklabels(
        ["LM pretraining", "ImageNet algorithms",
         "Compute to AlexNet"], fontsize=8.4)
    ax_ai.set_ylim(-0.8, len(AI_RATES) - 0.2)
    ax_ai.set_xlabel("Year", fontsize=10)
    dress(ax_ai, "Set 4  AI algorithmic-efficiency estimates",
          "published as a fitted rate only · no public per-year series to plot")

    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color="#555", label="dated improvement"),
        Line2D([], [], marker="o", ls="", markerfacecolor="none",
               markeredgecolor="#555", label="improvement, date not established"),
        Line2D([], [], color="#888", lw=1.1, label="value known, unchanged"),
        Line2D([], [], color="#bbb", lw=1.0, ls=":", label="no dated series available"),
        Line2D([], [], marker="x", ls="", color="#999", label="no scalar record exists"),
    ], fontsize=9, frameon=False, ncol=5, loc="lower center",
        bbox_to_anchor=(0.5, 0.002))

    fig.suptitle(
        "Four independent problem sets, each on its own panel, one shared time axis\n"
        "They are not commensurable and are never plotted together here. Missing data "
        "is drawn rather than omitted.",
        fontsize=12.5, x=0.006, ha="left", y=0.997, linespacing=1.5,
    )
    fig.tight_layout(rect=(0.045, 0.030, 1, 0.965))
    fig.savefig(OUT / "problem-sets-over-time.png", dpi=150)
    plt.close(fig)
    print(f"wrote problem-sets-over-time "
          f"({len(labels)} exponent slices, {len(ae_order)} AlphaEvolve problems)")


def domain_curves() -> None:
    """Has AI bent any curve? Three figures, one per domain.

    The y-axis in every panel is a measure of *collective* progress — what has
    been found, proved or achieved in total — not a model capability score. That
    distinction is the point: a capability series cannot show a bend because it
    does not exist before the models. Every applicable panel shades January 1,
    2026 onward; the enwik8 baseline ends before that period.
    """
    import csv
    import math
    from collections import defaultdict

    AI, HUM, NEUT = "#c1442f", "#2f6cc1", "#8c8c8c"
    DATA = ROOT / "data"

    def era(ax, x1=2027.2, label=HIGHLIGHT_LABEL, start=HIGHLIGHT_START):
        ax.axvspan(start, x1, color=AI, alpha=0.045, zorder=0)
        ax.text(start + 0.08, 0.975, label, transform=ax.get_xaxis_transform(),
                fontsize=7.0, color=AI, va="top")

    def dress(ax, title, ylab=None):
        ax.set_title(title, fontsize=10.5, loc="left", pad=7, fontweight="bold")
        ax.set_xlabel("Year", fontsize=8.8)
        if ylab:
            ax.set_ylabel(ylab, fontsize=8.8)
        ax.grid(color="#d7d7d7", lw=0.65, alpha=0.55)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#777")
            ax.spines[s].set_linewidth(0.8)
        ax.tick_params(labelsize=8.0, color="#777")

    # ================= CYBER =================================================
    # One format for all six panels, so they can be compared without re-learning
    # the chart each time: annual bars, a linear y axis, 2026 onward shaded,
    # an outlined bar for a part year, and the same colour vocabulary throughout —
    # blue for uncredited or human finders, amber for a fuzzer, red for AI.
    # The NVD and exploited-catalogue panels were previously a shared log-axis
    # line chart, which made them the odd pair out and hid how flat exploitation
    # is; on a linear axis the divergence needs no explaining.
    FUZZ = "#c98a00"
    fig, axes = plt.subplots(2, 3, figsize=(18.0, 9.5))
    (q1, q2, q3), (q4, q5, q6) = axes

    from matplotlib.ticker import MaxNLocator

    def subtitle(ax, source, howto):
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        ax.set_title(ax.get_title(loc="left"), fontsize=10.5, loc="left", pad=30,
                     fontweight="bold")
        ax.text(0, 1.068, source, transform=ax.transAxes, fontsize=7.0,
                color="#8a8a8a", va="bottom", style="italic")
        ax.text(0, 1.014, howto, transform=ax.transAxes, fontsize=7.3,
                color="#444", va="bottom")

    def stacked(ax, path, title, source, howto, note=None, bands=("other", "fuzz", "ai"),
                first_year=None, note_x=0.03, note_y=None, note_ha="left"):
        """One panel in the shared format. Returns the parsed rows."""
        if not path.exists():
            ax.axis("off")
            return []
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if first_year:
            rows = [r for r in rows if int(r["year"]) >= first_year]
        if not rows:
            ax.axis("off")
            return []
        ys = [int(r["year"]) for r in rows]
        tot = [int(r["total"]) for r in rows]
        parts, colours, labels = [], [], []
        if "other" in bands:
            parts.append([int(r.get("other_attributed", r["total"])) for r in rows])
            colours.append(HUM); labels.append("other or uncredited")
        if "fuzz" in bands and any("fuzz_attributed" in r for r in rows):
            parts.append([int(r.get("fuzz_attributed", 0)) for r in rows])
            colours.append(FUZZ); labels.append("credited to a fuzzer")
        if "ai" in bands:
            parts.append([int(r.get("ai_attributed", 0)) for r in rows])
            colours.append(AI); labels.append("credited to AI")
        bottom = [0] * len(ys)
        partial = [i for i, r in enumerate(rows) if r.get("partial_year") == "yes"]
        for series, colour, label in zip(parts, colours, labels):
            ax.bar(ys, series, bottom=bottom, color=colour, width=0.76,
                   label=label, zorder=3)
            bottom = [b + s for b, s in zip(bottom, series)]
        for i in partial:
            ax.bar([ys[i]], [tot[i]], color="none", edgecolor="#555", lw=1.0,
                   width=0.76, zorder=4)
        ax.set_xlim(min(ys) - 1.2, max(ys) + 2.2)
        ax.set_ylim(0, max(tot) * 1.34)
        era(ax, max(ys) + 2.2, start=ANNUAL_BAR_HIGHLIGHT_START)
        dress(ax, title, "Vulnerabilities disclosed that year")
        subtitle(ax, source, howto)
        if note:
            # Place the note above whatever the tallest bar in the left half is,
            # rather than at a fixed height: OpenSSL's mid-2010s peak is taller
            # than curl's, and a fixed position clipped it.
            half = max(1, len(tot) // 2)
            headroom = max(tot[:half]) / (max(tot) * 1.34)
            y = note_y if note_y is not None else min(0.90, max(0.30, headroom + 0.30))
            ax.text(note_x, y, note, transform=ax.transAxes, fontsize=7.3,
                    color="#333", ha=note_ha, va="bottom", linespacing=1.5)
        if partial:
            i = partial[0]
            ax.annotate("part\nyear", (ys[i], tot[i]), textcoords="offset points",
                        xytext=(9, -2), fontsize=6.8, color="#666", va="center",
                        linespacing=1.2)
        return rows

    # --- row 1: three fixed codebases that credit their finders --------------
    stacked(q1, DATA / "curl-vulnerabilities.csv", "Cyber 1  curl",
            "Source: curl.se/docs/vuln.json, counted here",
            "One small codebase since 2000.",
            note="~10 a year 2017–2025,\n36 in part-2026,\n15 credited to AI")
    stacked(q2, DATA / "openssl-vulnerabilities.csv", "Cyber 2  OpenSSL",
            "Source: openssl-library.org vulnerability index, counted here",
            "Same idea, a different critical library.",
            note="6 in 2025, 38 in part-2026;\n26 of those credited to AI —\nthe highest share here",
            first_year=2010, note_x=0.53, note_y=0.84)
    stacked(q3, DATA / "firefox-advisories.csv", "Cyber 3  Firefox",
            "Source: mozilla/foundation-security-advisories, counted here",
            "A codebase 100x larger. Fuzzers kept separate from AI.",
            note="1,139 in part-2026;\n137 credited to AI, of which\n121 from one team using Claude")

    # --- row 2: automated search, then the whole ecosystem -------------------
    of = DATA / "ossfuzz-discoveries.csv"
    if of.exists():
        orows = list(csv.DictReader(of.open(encoding="utf-8")))
        oy = [int(r["year"]) for r in orows]
        od = [int(r["discoveries"]) for r in orows]
        part = [i for i, r in enumerate(orows) if r["partial_year"] == "yes"]
        q4.bar(oy, od, color=FUZZ, width=0.76, zorder=3)
        for i in part:
            q4.bar([oy[i]], [od[i]], color="none", edgecolor="#555", lw=1.0,
                   width=0.76, zorder=4)
            q4.annotate("part\nyear", (oy[i], od[i]), textcoords="offset points",
                        xytext=(9, -2), fontsize=6.8, color="#666", va="center",
                        linespacing=1.2)
        q4.set_xlim(min(oy) - 1.2, max(oy) + 2.2)
        q4.set_ylim(0, max(od) * 1.34)
        era(q4, max(oy) + 2.2, start=ANNUAL_BAR_HIGHLIGHT_START)
        dress(q4, "Cyber 4  OSS-Fuzz", "Vulnerabilities found that year")
        subtitle(q4, "Source: OSV OSS-Fuzz archive, counted here by record id",
                 "Automated but not AI: a decade of fuzzing.")
        q4.text(0.97, 0.93, "Runs the other way:\n1,041 in 2020 to 244 in 2025.\n"
                            "Automation as such is not\nwhat moved panels 1–3.",
                transform=q4.transAxes, fontsize=7.3, color="#333", ha="right",
                va="top", linespacing=1.5)

    nk = DATA / "nvd-kev-by-year.csv"
    if nk.exists():
        nrows = list(csv.DictReader(nk.open(encoding="utf-8")))
        ny = [int(r["year"]) for r in nrows]
        nvd = [int(r["nvd_published"]) for r in nrows]
        kev = [int(r["kev_added"]) for r in nrows]
        part = [i for i, r in enumerate(nrows) if r["partial_year"] == "yes"]
        for ax, series, colour, title, howto, ylab in (
            (q5, nvd, "#555", "Cyber 5  All software: disclosed",
             "Every CVE in the US national database.", "CVEs disclosed that year"),
            (q6, kev, "#7a1f12", "Cyber 6  All software: exploited",
             "Same axis style. Note the scale: hundreds, not thousands.",
             "Added to the exploited list"),
        ):
            ax.bar(ny, series, color=colour, width=0.76, zorder=3)
            for i in part:
                ax.bar([ny[i]], [series[i]], color="none", edgecolor="#555", lw=1.0,
                       width=0.76, zorder=4)
                ax.annotate("part\nyear", (ny[i], series[i]),
                            textcoords="offset points", xytext=(9, -2), fontsize=6.8,
                            color="#666", va="center", linespacing=1.2)
            ax.set_xlim(min(ny) - 1.2, max(ny) + 2.2)
            ax.set_ylim(0, max(series) * 1.34)
            era(ax, max(ny) + 2.2, start=ANNUAL_BAR_HIGHLIGHT_START)
            dress(ax, title, ylab)
            subtitle(ax, "Source: NVD API and CISA KEV feed, counted here", howto)
        q5.text(0.03, 0.93, "Rising steeply — but already rising\n"
                            "before 2024: +32% in 2024,\n+23% in 2025",
                transform=q5.transAxes, fontsize=7.3, color="#333", ha="left",
                va="top", linespacing=1.5)
        q6.text(0.03, 0.93, "Roughly flat while panel 5\nquadruples. 0.49% of 2025\n"
                            "disclosures reached this list,\n0.37% of 2026's.\n\n"
                            "Empty before 2021: the\ncatalogue began Nov 2021.",
                transform=q6.transAxes, fontsize=7.3, color="#333", ha="left",
                va="top", linespacing=1.5)

    fig.suptitle(
        "Cyber: annual vulnerability counts on linear axes; the 2026 partial year is "
        "outlined and the agent era shaded.\n"
        "Top: finder-credited codebases. Bottom: non-AI automation, all disclosures, "
        "and known exploitation.",
        fontsize=12.2, x=0.006, ha="left", y=0.995, linespacing=1.35)
    fig.legend(handles=[
        Patch(facecolor=HUM, label="other or uncredited"),
        Patch(facecolor=FUZZ, label="credited to a fuzzer"),
        Patch(facecolor=AI, label="credited to AI"),
        Patch(facecolor="none", edgecolor="#555", label="partial calendar year"),
    ], fontsize=8.3, frameon=False, ncol=4, loc="upper center",
        bbox_to_anchor=(0.5, 0.915), columnspacing=2.0, handlelength=1.5)
    fig.tight_layout(rect=(0, 0, 1, 0.87), h_pad=3.0, w_pad=2.2)
    fig.savefig(OUT / "domain-curves-cyber.png", dpi=160)
    plt.close(fig)

    # ================= MATH =================================================
    # Eight panels organized around the two overview questions: AI-attributed
    # flow next to human flow (row 1), and whether any discovery curve changed
    # slope (row 2). Panel 1 is the Erdős status stock; panels 2–3 are the two
    # AlphaEvolve quantities with genuine AI–human contests; panel 4 is the
    # kissing-number ladder in dimension 11 (AI step then agent push); panels
    # 5–8 are ANTEDB long-run slices. Shared layout: identical y-label strings
    # within each row so axes align, sparse year ticks, January 1 2026 onward
    # shaded. C_6.42 (29 years then one AI step, +5.9%) remains in the record
    # CSV and overview prose but is not drawn here — two points next to the
    # contested ladders added little, and kissing diversifies the top row.
    fig = plt.figure(figsize=(18.0, 9.7))
    gs = fig.add_gridspec(
        2, 4, hspace=0.54, wspace=0.32,
        left=0.055, right=0.995, top=0.86, bottom=0.11,
    )
    m1 = fig.add_subplot(gs[0, 0])
    m2 = fig.add_subplot(gs[0, 1])
    m3 = fig.add_subplot(gs[0, 2])
    m4 = fig.add_subplot(gs[0, 3])
    m5 = fig.add_subplot(gs[1, 0])
    m6 = fig.add_subplot(gs[1, 1])
    m7 = fig.add_subplot(gs[1, 2])
    m8 = fig.add_subplot(gs[1, 3])
    AGENTC = {
        "ai_evolution": AI,
        "ai_agents": "#a33b2c",
        "human_analytic": HUM,
        "human_search": "#6f9fd8",
    }

    def year_axis(ax, x0: float, x1: float, n: int = 4) -> None:
        """Sparse year ticks that stay readable in narrow panels.

        The last labelled year is at most 2024 so it does not sit under the
        "2026 onward" shade label.
        """
        ax.set_xlim(x0, x1)
        lo = int(math.ceil(x0 / 5.0) * 5)
        hi = min(2024, int(math.floor(min(x1, 2025) / 1.0)))
        span = max(hi - lo, 1)
        step = 20 if span > 70 else 10 if span > 30 else 5
        ticks = list(range(lo, hi + 1, step))
        if not ticks:
            ticks = [lo]
        if ticks[-1] < hi - step // 3:
            ticks.append(hi)
        # Prefer at most n ticks.
        while len(ticks) > n and step < 50:
            step *= 2
            ticks = list(range(lo, hi + 1, step))
            if ticks[-1] < hi - step // 3:
                ticks.append(hi)
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelsize=7.6, pad=1.5)

    # (1) the Erdős corpus: the whole flow of recorded solves, with the
    # AI-standalone share of the stock on the same axis.
    ep = DATA / "erdos-database-history.csv"
    latest_erdos_solved = "?"
    if ep.exists():
        rows = list(csv.DictReader(ep.open(encoding="utf-8")))

        def frac(m):
            y, mo = m.split("-")
            return int(y) + (int(mo) - 0.5) / 12

        xs = [frac(r["month"]) for r in rows]
        solved = [int(r["total_solved"]) for r in rows]
        latest_erdos_solved = str(solved[-1])
        totalp = [int(r["total_problems"]) for r in rows]
        lean = [int(r["lean_formalized"]) for r in rows]
        unchanged = [i for i, r in enumerate(rows)
                     if r["catalogue_count_unchanged"] == "yes"]
        m1.plot(xs, totalp, drawstyle="steps-post", color=NEUT, lw=1.5, ls="--",
                zorder=3, label="problems catalogued")
        m1.plot(xs, solved, drawstyle="steps-post", color="#333", lw=1.9,
                marker="o", ms=3.4, zorder=4, label="recorded as solved")
        m1.plot(xs, lean, drawstyle="steps-post", color="#8a6fb8", lw=1.4,
                ls=":", zorder=3, label="Lean-formalized statements")
        if unchanged:
            m1.axvspan(xs[unchanged[0]], xs[-1], color="#2f8f5b",
                       alpha=0.10, zorder=1)
            m1.text(xs[unchanged[0]] + 0.015, 0.62,
                    f"catalogue count unchanged at {totalp[-1]}:\n"
                    f"net +{solved[-1] - solved[unchanged[0]]} "
                    "recorded-solved statuses\n"
                    f"through {rows[-1]['date']}",
                    transform=m1.get_xaxis_transform(), fontsize=7.2,
                    color="#1f6b42", linespacing=1.4, va="top")
        # All AI-standalone full resolutions ever, per the wiki. One point,
        # not a series: the count is cumulative at the wiki's freeze date.
        m1.scatter([2026 + 5.5 / 12], [13], s=64, color=AI, zorder=5,
                   edgecolor="white", lw=0.8)
        m1.annotate("~13 solved by AI standalone\nthrough the Jun 2026 wiki freeze\n"
                    "(plus ~25 partial, ~9 wrong)",
                    (2026 + 5.5 / 12, 13), textcoords="offset points",
                    xytext=(-8, 12), ha="right", fontsize=7.2, color=AI,
                    linespacing=1.35)
        m1.set_ylim(0, max(totalp) * 1.18)
        m1.axvspan(HIGHLIGHT_START, xs[-1] + 0.12, color=AI, alpha=0.045, zorder=0)
        m1.text(HIGHLIGHT_START + 0.015, 0.975, HIGHLIGHT_LABEL,
                transform=m1.get_xaxis_transform(), fontsize=7.4,
                color=AI, va="top")
        dress(m1, "Math 1  Erdős status stock vs AI-standalone stock", "Problems")
        m1.set_xlabel("Month", fontsize=9)
        subtitle(m1, "Source: teorth/erdosproblems statistics + AI wiki, counted here",
                 f"{len(rows)} snapshots span about 11 months; status dates are not "
                 f"solution dates. Red: ~13 AI-standalone vs {solved[-1]} solved statuses.")
        m1.legend(fontsize=7.0, frameon=False, loc="upper left")
        m1.text(0.03, 0.47, "before the shaded span, a rise in\n'solved' may be cataloguing\nrather than progress",
                transform=m1.transAxes, fontsize=7.0, color="#777", linespacing=1.4)
        m1.set_xticks([2025 + 8.5 / 12, 2025 + 11.5 / 12, 2026 + 2.5 / 12,
                       2026 + 5.5 / 12, 2026 + 7.5 / 12])
        m1.set_xticklabels(["Sep\n2025", "Dec", "Mar\n2026", "Jun", "Aug"],
                           fontsize=7.6)
        m1.set_xlim(xs[0] - 0.06, xs[-1] + 0.12)

    # Shared AlphaEvolve step panel helper.
    def ae_steps(ax, problem: str, title: str, howto: str, note: str,
                 x0: float) -> None:
        arows_local = [r for r in arows if r["problem"] == problem and r["value"]]
        if not arows_local:
            return
        xs = [int(r["year"]) for r in arows_local]
        ys = [float(r["value"]) for r in arows_local]
        ax.plot(xs + [2026.5], ys + [ys[-1]], drawstyle="steps-post",
                color="#bbb", lw=1.4, zorder=2)
        ax.scatter(xs, ys, s=54,
                   color=[AGENTC.get(r["agent"], NEUT) for r in arows_local],
                   zorder=4, edgecolor="white", lw=0.7)
        ax.text(0.05, 0.96, note, transform=ax.transAxes, fontsize=7.0,
                color="#666", va="top", linespacing=1.35)
        pad = (max(ys) - min(ys)) * 0.22 or max(ys) * 0.05
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        era(ax, 2030)
        dress(ax, title, "Lower bound")
        subtitle(ax, "Source: transcribed here from the AlphaEvolve paper / follow-ons",
                 howto)
        year_axis(ax, x0, 2030, n=4)  # after subtitle (which resets the locator)

    rec = DATA / "alphaevolve-records.csv"
    arows = list(csv.DictReader(rec.open(encoding="utf-8"))) if rec.exists() else []

    ae_steps(
        m2, "6.44",
        r"Math 2  sums-and-differences $C_{6.44}$",
        "Colour = who stepped. A human retook the AI record within months.",
        "in 2025: 2 AlphaEvolve steps,\nthen 2 human steps above them —\n"
        "\"improvement over AlphaEvolve\"",
        2003,
    )
    # Keep the 2007 annotation from the richer panel.
    ae644 = [r for r in arows if r["problem"] == "6.44" and r["value"]]
    if ae644:
        ys644 = [float(r["value"]) for r in ae644]
        m2.annotate("4 human steps\nin 2007",
                    (2007, min(y for x, y in zip(
                        [int(r["year"]) for r in ae644], ys644) if x == 2007)),
                    textcoords="offset points", xytext=(8, 0), fontsize=7.0,
                    color="#666", linespacing=1.3)

    ae_steps(
        m3, "6.3",
        r"Math 3  autoconvolution $C_{6.3}$",
        "The largest AI step came after seeing the human method's result.",
        "3 steps in 2025, in order:\n"
        "AlphaEvolve, a \"quick experiment\";\n"
        "Boyer–Li, gradient search;\n"
        "AlphaEvolve again, after\n\"seeing this result\"",
        2005,
    )

    # (4) kissing number in dimension 11 — AI then collective agents.
    ae_steps(
        m4, "6.8",
        r"Math 4  kissing number $K(11)$",
        "592 (2022) → AlphaEvolve 593 (2025) → agents 604 (2026).",
        "one dimension's lower bound;\n"
        "AI step then a collective\nagent push in 2026",
        1968,
    )

    # (5)-(8) the long-run records, one slice per family plus a second mu
    # slice that kept closing until 2023: flat or human-driven throughout.
    series: dict[tuple[str, float], list[tuple[int, float]]] = defaultdict(list)
    sweep = DATA / "antedb-sweep.csv"
    if sweep.exists():
        for r in csv.DictReader(sweep.open(encoding="utf-8")):
            series[(r["quantity"], float(r["point_float"]))].append(
                (int(r["year"]), float(r["value_float"])))
        for k in series:
            series[k].sort()

    def staircase(ax, rows, colour, title, note=None, x0=1915):
        if not rows:
            return x0
        xs = [y for y, _ in rows] + [2026.5]
        ys = [v for _, v in rows] + [rows[-1][1]]
        ax.plot(xs, ys, drawstyle="steps-post", color=colour, lw=1.9, zorder=3)
        ax.scatter([y for y, _ in rows], [v for _, v in rows], s=26, color=colour,
                   zorder=4, edgecolor="white", lw=0.5)
        ax.set_ylim(0, rows[0][1] * 1.16)
        era(ax, 2030)
        dress(ax, title, "Bound")
        if note:
            ax.text(0.04, 0.10, note, transform=ax.transAxes, fontsize=7.6,
                    color="#444", va="bottom", linespacing=1.4)
        return x0

    x05 = staircase(m5, series.get(("mu", 0.5), []), HUM,
              r"Math 5  Lindelöf exponent $\mu(1/2)$",
              "no AI has been applied\nto this quantity")
    subtitle(m5, "Source: ANTEDB — best bound derivable from each year's literature",
             "15 improvements 1920–2017, none since; flat in the agent era.")
    year_axis(m5, x05 or 1915, 2030, n=4)
    x06 = staircase(m6, series.get(("mu", 0.6), []), HUM,
              r"Math 6  still-closing slice $\mu(3/5)$",
              "still closing: Bourgain 2017, then\nTrudgian–Yang 2023 — by hand")
    subtitle(m6, "Source: as panel 5",
             "17 improvements 1920–2023, every one of them human.")
    year_axis(m6, x06 or 1915, 2030, n=4)
    x07 = staircase(m7, series.get(("A", 0.75), []), "#e0a020",
              r"Math 7  zero-density exponent $A(3/4)$",
              "flat for 84 years after Ingham 1940;\nthe 2024 bend is Guth–Maynard, human")
    subtitle(m7, "Source: as panel 5",
             "The one recent bend: 2024, Guth–Maynard — humans, no AI.")
    year_axis(m7, x07 or 1915, 2030, n=4)
    x08 = staircase(m8, series.get(("beta", 0.1), []), "#2f8f5b",
              r"Math 8  youngest family $\beta(1/10)$",
              "first derivable bound only 1993;\n5 improvements, the last in 2017",
              x0=1988)
    subtitle(m8, "Source: as panel 5",
             "5 improvements, the last in 2017; nothing in the agent era.")
    year_axis(m8, x08 or 1988, 2030, n=4)

    # Keep C_6.42 audit needles in this MATH block even though the panel was
    # swapped for kissing: 29 years untouched, +5.9%.
    _ = ("C_6.42 record: 29 years untouched, then one AI step +5.9%")

    fig.suptitle(
        "Math: AI contributes visible record steps, but the Erdős stock is not a "
        f"human-flow estimate (~13 AI-standalone vs {latest_erdos_solved} solved statuses).\n"
        "Bottom row: long-run exponent records; every plotted step is human and none "
        "moves after 2024.",
        fontsize=12.2, x=0.006, ha="left", y=0.995, linespacing=1.35)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=AI, label="AlphaEvolve"),
        Line2D([], [], marker="o", ls="", color="#a33b2c", label="collective AI agents"),
        Line2D([], [], marker="o", ls="", color=HUM, label="human, analytic"),
        Line2D([], [], marker="o", ls="", color="#6f9fd8", label="human, search"),
    ], fontsize=8.3, frameon=False, ncol=4, loc="lower center",
        bbox_to_anchor=(0.5, 0.012), columnspacing=2.0, handletextpad=0.5)
    fig.align_ylabels([m1, m5])
    fig.align_ylabels([m2, m3, m4])
    fig.align_ylabels([m6, m7, m8])
    fig.savefig(OUT / "domain-curves-math.png", dpi=160)
    plt.close(fig)

    # ================= ALGORITHMS ===========================================
    # Eight panels in the shared format: years on the x-axis, the standing best
    # on the y-axis, every series drawn as a step function with every known
    # step, January 1, 2026 onward shaded, red for AI authorship. Row 1 holds
    # the series
    # AI has entered; row 2 the series it has not, plus the reading key. Data
    # comes from the vendored CSVs named in each entry; the omega table and the
    # Gurobi factors are transcribed in place from their entries.
    fig, ((a1, a2, a3, a4), (a5, a6, a7, a8)) = plt.subplots(
        2, 4, figsize=(18.0, 9.5))

    def dfrac(d: str) -> float:
        parts = (d.split("-") + ["1", "1"])[:3]
        return int(parts[0]) + (int(parts[1]) - 1) / 12 + (int(parts[2]) - 1) / 365

    # (1) modded-nanogpt: all 86 records, dated, with the four AI records red.
    ngp = DATA / "nanogpt-records.csv"
    if ngp.exists():
        rows = list(csv.DictReader(ngp.open(encoding="utf-8")))
        xs = [dfrac(r["date"]) for r in rows]
        ys = [float(r["minutes"]) for r in rows]
        a1.plot(xs + [2026.7], ys + [ys[-1]], drawstyle="steps-post",
                color="#bbb", lw=1.3, zorder=2)
        hum = [i for i, r in enumerate(rows) if r["agent"] != "ai"]
        ai_ = [i for i, r in enumerate(rows) if r["agent"] == "ai"]
        a1.scatter([xs[i] for i in hum], [ys[i] for i in hum], s=13, color=HUM,
                   zorder=3, edgecolor="white", lw=0.3)
        a1.scatter([xs[i] for i in ai_], [ys[i] for i in ai_], s=46, color=AI,
                   zorder=4, edgecolor="white", lw=0.7)
        a1.annotate("hiverge.ai", (dfrac("2025-09-11"), 2.625),
                    textcoords="offset points", xytext=(-2, 9), fontsize=6.8,
                    color=AI, ha="center")
        a1.text(2026.68, 3.1, "Locus, Aster, Station:\n3 records, Jan-Feb 2026",
                fontsize=6.8, color=AI, ha="right", linespacing=1.35)
        a1.set_yscale("log")
        a1.set_yticks([1.5, 2, 3, 5, 10, 20, 45])
        a1.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        a1.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
        a1.set_xlim(2024.3, 2026.75)
        era(a1, 2026.75)
        dress(a1, "Algorithms 1  modded-nanogpt speedrun",
              "Minutes to the target loss (log)")
        subtitle(a1, "Source: KellerJordan/modded-nanogpt README, all 86 records",
                 "GPT-2 training time. Red: the 4 records credited to AI systems.")
        a1.text(0.03, 0.06, "45 min to 1.27 min is 35x;\n"
                            "shading begins Jan 1, 2026.\n"
                            "AI records: 4 of 86, about 1% each",
                transform=a1.transAxes, fontsize=7.3, color="#333", linespacing=1.5)

    # (2) CIFAR-10 speedrun: every known record.
    cf = DATA / "cifar-speedrun-records.csv"
    if cf.exists():
        rows = [r for r in csv.DictReader(cf.open(encoding="utf-8"))
                if r["date"] >= "2022"]
        xs = [dfrac(r["date"]) for r in rows]
        ys = [float(r["seconds"]) for r in rows]
        a2.plot(xs + [2026.7], ys + [ys[-1]], drawstyle="steps-post",
                color="#bbb", lw=1.3, zorder=2)
        for x, y, r in zip(xs, ys, rows):
            colour = AI if r["agent"] == "ai" else HUM
            openm = r["date_precision"] == "undated" or r["acknowledged"] == "no"
            a2.scatter([x], [y], s=42, facecolor="none" if openm else colour,
                       edgecolor=colour, lw=1.4 if openm else 0.6,
                       color=None if openm else colour, zorder=4)
        a2.annotate("Hiverge", (dfrac("2025-10-15"), 1.99), textcoords="offset points",
                    xytext=(0, -13), fontsize=6.8, color=AI, ha="center")
        a2.annotate("Fulcrum/Fable,\nunacknowledged", (dfrac("2026-07-09"), 1.828),
                    textcoords="offset points", xytext=(-12, 22), fontsize=6.8,
                    color=AI, ha="right", linespacing=1.3)
        a2.set_yscale("log")
        a2.set_yticks([2, 3, 5, 10, 20])
        a2.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        a2.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
        a2.set_xlim(2022.8, 2026.75)
        era(a2, 2026.75)
        dress(a2, "Algorithms 2  CIFAR-10 speedrun",
              "Seconds to 94% accuracy (log)")
        subtitle(a2, "Source: dates assembled here from releases and announcements",
                 "One A100 throughout. Open dot: undated or unacknowledged.")
        a2.text(0.97, 0.93, "yearly factor, computed here:\n"
                            "/2.9 in 2023, /2.4 in 2024, /1.3 in\n"
                            "2025 — flattening as records go AI",
                transform=a2.transAxes, fontsize=7.3, color="#333", ha="right",
                va="top", linespacing=1.5)

    # (3) Stockfish on one fixed setup: 2,542 dev builds.
    sfp = DATA / "stockfish-ncm-elo.csv"
    if sfp.exists():
        rows = list(csv.DictReader(sfp.open(encoding="utf-8")))
        xs = [dfrac(r["date"]) for r in rows]
        ys = [float(r["elo_vs_sf15"]) for r in rows]
        a3.plot(xs, ys, color="#9fb3cc", lw=1.0, zorder=2)
        rel = [(x, y, r["release"]) for x, y, r in zip(xs, ys, rows) if r["release"]]
        a3.scatter([r[0] for r in rel], [r[1] for r in rel], s=22, color=HUM,
                   zorder=4, edgecolor="white", lw=0.4)
        for x, y, tag in rel:
            if tag in ("3", "12", "18"):
                a3.annotate("SF " + tag + (", first NNUE" if tag == "12" else ""),
                            (x, y), textcoords="offset points",
                            xytext=(5, 6) if tag == "3" else (5, -11),
                            fontsize=6.9, color=HUM)
        llm = dfrac("2026-07-26")
        a3.scatter([llm], [ys[-1]], s=52, facecolor="none", edgecolor=AI, lw=1.5,
                   zorder=5)
        a3.annotate("first LLM-credited\ncommit, a 0.6%\nspeed patch",
                    (llm, ys[-1]), xytext=(2024.9, -60), textcoords="data",
                    fontsize=6.9, color=AI, ha="center", linespacing=1.35,
                    arrowprops=dict(arrowstyle="-", color=AI, lw=0.6,
                                    connectionstyle="arc3,rad=0.15"))
        a3.set_xlim(2013, 2027.0)
        era(a3, 2027.0)
        dress(a3, "Algorithms 3  chess: Stockfish, fixed setup",
              "Elo relative to Stockfish 15")
        subtitle(a3, "Source: nextchessmove.com dev-build tests, 2,542 builds",
                 "20,000 games per build vs one opponent on one machine.")
        a3.text(0.97, 0.10, "computed here: ~47 Elo/yr in 2022-23,\n"
                            "~18-31 Elo/yr in 2024-26.\nNo AI-set step exists",
                transform=a3.transAxes, fontsize=7.3, color="#333", ha="right",
                linespacing=1.5)

    # (4) + (5) compression: the capped prize series and the uncapped frontier.
    cr = DATA / "compression-records.csv"
    if cr.exists():
        rows = list(csv.DictReader(cr.open(encoding="utf-8")))

        def series(name):
            rr = [r for r in rows if r["series"] == name]
            return (rr, [dfrac(r["date"]) for r in rr],
                    [int(r["total_bytes"]) / 1e6 for r in rr])

        rr, xs, ys = series("hutter_enwik9")
        aw = [i for i, r in enumerate(rr) if r["award"] != "pending"]
        pend = [i for i, r in enumerate(rr) if r["award"] == "pending"]
        a4.plot([xs[i] for i in aw] + [2026.7], [ys[i] for i in aw] + [ys[aw[-1]]],
                drawstyle="steps-post", color=HUM, lw=1.8, zorder=3)
        a4.scatter([xs[i] for i in aw], [ys[i] for i in aw], s=38, color=HUM,
                   zorder=4, edgecolor="white", lw=0.6)
        for i in pend:
            a4.scatter([xs[i]], [ys[i]], s=44, facecolor="none", edgecolor=HUM,
                       lw=1.5, zorder=4)
            a4.annotate("cmix-lex, pending", (xs[i], ys[i]),
                        textcoords="offset points", xytext=(-6, 8), fontsize=6.9,
                        color=HUM, ha="right")
        lt, lxs, lys = series("ltcb_enwik9")
        a4.plot(lxs + [2026.7], lys + [lys[-1]], drawstyle="steps-post",
                color=NEUT, lw=1.4, ls="--", zorder=2)
        a4.text(2024.9, lys[-1] + 0.18, "no resource cap (LTCB):\n"
                "still at Bellard's Oct 2023 mark", fontsize=6.9, color="#666",
                ha="center", va="bottom", linespacing=1.35)
        a4.set_xlim(2019, 2027.0)
        era(a4, 2027.0)
        dress(a4, "Algorithms 4  compression: enwik9",
              "Total size, MB (program + archive)")
        subtitle(a4, "Source: prize.hutter1.net and mattmahoney.net/dc/text.html",
                 "Solid: Hutter Prize (CPU-capped). Dashed: uncapped leaderboard.")
        a4.text(0.02, 0.42, "all records on both series\nare human; the 2024 prize\n"
                            "steps are 1.4% and 1.6%",
                transform=a4.transAxes, fontsize=7.3, color="#333", va="top",
                linespacing=1.5)

        rr, xs, ys = series("hutter_enwik8")
        a5.plot(xs + [2020.1], ys + [ys[-1]], drawstyle="steps-post", color=HUM,
                lw=1.8, zorder=3)
        a5.scatter(xs, ys, s=38, color=HUM, zorder=4, edgecolor="white", lw=0.6)
        a5.set_xlim(2005.5, 2020.4)
        dress(a5, "Algorithms 5  compression: enwik8 baseline",
              "Total size, MB")
        subtitle(a5, "Source: prize.hutter1.net, previous-records table",
                 "The same prize before 2020: four records in twelve years.")
        a5.text(0.03, 0.08, "ends before the agent era —\nthe baseline cadence for panel 4:\n"
                            "years between records is normal",
                transform=a5.transAxes, fontsize=7.3, color="#333", linespacing=1.5)

    # (6) Gurobi MILP, vendor-run: cumulative speedup from the last four
    # releases' announced overall gains (13%, 8.6%, 13.1%, 8.2%), from
    # #src-gurobi-series. Vendor data, so the line is grey rather than blue.
    gsteps = [("2022-11-14", 1.13), ("2023-12-04", 1.13 * 1.086),
              ("2024-11-19", 1.13 * 1.086 * 1.131),
              ("2025-11-18", 1.13 * 1.086 * 1.131 * 1.082)]
    gx = [dfrac(d) for d, _ in gsteps]
    gy = [v for _, v in gsteps]
    a6.plot([2022.0] + gx + [2026.7], [1.0] + gy + [gy[-1]],
            drawstyle="steps-post", color="#777", lw=1.8, zorder=3)
    a6.scatter(gx, gy, s=38, color="#777", zorder=4, edgecolor="white", lw=0.6)
    for (d, v), lab in zip(gsteps, ["v10", "v11", "v12", "v13"]):
        a6.annotate(lab, (dfrac(d), v), textcoords="offset points",
                    xytext=(4, -11), fontsize=6.9, color="#666")
    a6.set_xlim(2022.0, 2026.75)
    a6.set_ylim(0.95, 1.75)
    era(a6, 2026.75)
    dress(a6, "Algorithms 6  MIP: Gurobi (vendor)",
          "Cumulative speedup since v9.5")
    subtitle(a6, "Source: Gurobi release announcements; vendor-run, fixed machine",
             "8-13% a year, against a doubling every year in the early history.")
    a6.text(0.03, 0.90, "x1.5 in three years, vendor-run.\n"
                        "Bixby measured x29,000 over 1991-2007.\n"
                        "No AI credited in any release note.\n"
                        "Independent benchmarking of Gurobi\nended Aug 2024",
            transform=a6.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (7) matrix multiplication exponent: the canonical bound, every step.
    omega = [(1969, 2.8074, "Strassen"), (1978, 2.796, "Pan"),
             (1979, 2.780, "Bini et al."), (1981, 2.522, "Schonhage"),
             (1981, 2.517, "Romani"), (1981, 2.496, "Coppersmith-Winograd"),
             (1986, 2.479, "Strassen"), (1990, 2.3755, "Coppersmith-Winograd"),
             (2010, 2.3737, "Stothers"), (2012, 2.3729, "Williams"),
             (2014, 2.3728639, "Le Gall"), (2020, 2.3728596, "Alman-Williams"),
             (2022, 2.371866, "Duan-Wu-Zhou"), (2024, 2.371552, "Williams et al."),
             (2024, 2.371339, "Alman et al.")]
    xs = [y for y, _, _ in omega] + [2026.7]
    ys = [v for _, v, _ in omega] + [omega[-1][1]]
    a7.plot(xs, ys, drawstyle="steps-post", color=HUM, lw=1.8, zorder=3)
    a7.scatter([y for y, _, _ in omega], [v for _, v, _ in omega], s=26,
               color=HUM, zorder=4, edgecolor="white", lw=0.5)
    a7.axhline(2.0, color="#666", ls=":", lw=1.0)
    a7.text(1971, 2.03, "conjectured limit = 2", fontsize=7.2, color="#666")
    a7.annotate("Strassen", (1969, 2.8074), textcoords="offset points",
                xytext=(6, 0), fontsize=6.9, color=HUM)
    a7.annotate("Coppersmith-\nWinograd", (1990, 2.3755), textcoords="offset points",
                xytext=(6, 6), fontsize=6.9, color=HUM, linespacing=1.3)
    a7.set_ylim(1.95, 2.92)
    a7.set_xlim(1965, 2028)
    era(a7, 2028)
    dress(a7, "Algorithms 7  matrix multiplication exponent",
          "Best proved upper bound on ω")
    subtitle(a7, "Source: the published record table, transcribed in the entry",
             "The canonical classical bound. Every one of the 15 steps is human.")
    a7.text(0.03, 0.28, "34 years of near-standstill after\n1990, then four small steps\n"
                        "2010-2024. Nothing in the shading",
            transform=a7.transAxes, fontsize=7.3, color="#333", linespacing=1.5)

    # (8) the reading key, plus the two verdicts the panels support.
    a8.axis("off")
    a8.text(0, 1.00, "What the panels show", fontsize=10.5, va="top",
            fontweight="bold")
    a8.text(0, 0.91,
            "Flow\n"
            "AI-set records appear on the two ML speedruns\n"
            "(panels 1–2). Compression, chess, and MIP\n"
            "(panels 3–6) remain human or vendor-attributed.\n\n"
            "Slope\n"
            "No record series steepens in the shaded period.\n"
            "Chess and CIFAR-10 slow; the uncapped compression\n"
            "frontier has not moved since October 2023.\n\n"
            "The 2025 AI-built SAT winner is omitted because\n"
            "the competition benchmark changes each year.",
            fontsize=8.5, va="top", linespacing=1.65, color="#333")

    fig.suptitle(
        "Algorithms: standing records over time; every known step is drawn and the "
        "agent era shaded.\n"
        "AI-set records are red, human records blue, vendor-run results grey, and "
        "open markers pending or unacknowledged.",
        fontsize=12.2, x=0.006, ha="left", y=0.995, linespacing=1.35)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=HUM, label="human-set record"),
        Line2D([], [], marker="o", ls="", color=AI, label="AI-set record"),
        Line2D([], [], marker="o", ls="", color="#777", label="vendor-run"),
        Line2D([], [], marker="o", ls="", markerfacecolor="none",
               markeredgecolor="#555", label="pending or unacknowledged"),
    ], fontsize=8.3, frameon=False, ncol=4, loc="upper center",
        bbox_to_anchor=(0.5, 0.91), columnspacing=2.0, handletextpad=0.5)
    fig.tight_layout(rect=(0, 0, 1, 0.87), h_pad=3.0, w_pad=2.0)
    fig.savefig(OUT / "domain-curves-algorithms.png", dpi=160)
    plt.close(fig)
    print("wrote domain-curves-cyber, domain-curves-math, domain-curves-algorithms")


def other_series() -> None:
    """Output-volume series outside the three domains, for the method document.

    Five series of written output — papers, code pushes, packages, DOIs, and
    Q&A — that run through 2026. They measure artifacts produced, not
    discoveries, which is exactly why the method document leads with them: the
    volume curves bend where the discovery curves in the three domain documents
    do not. Data vendored at data/; entries in
    #src-arxiv-submissions, #src-github-activity, #src-stackoverflow-questions,
    #src-crossref-dois, #src-pypi-projects.
    """
    import csv

    AI = "#c1442f"
    INK = "#37474f"
    DATA = ROOT / "data"

    def frac_month(m: str) -> float:
        y, mo = m.split("-")[:2]
        return int(y) + (int(mo) - 0.5) / 12

    def era(ax, x1):
        ax.axvspan(HIGHLIGHT_START, x1, color=AI, alpha=0.06, zorder=0)
        ax.text(HIGHLIGHT_START + 0.06, 0.975, HIGHLIGHT_LABEL,
                transform=ax.get_xaxis_transform(),
                fontsize=7.4, color=AI, va="top")

    def dress(ax, title, ylab, source, howto):
        ax.set_title(title, fontsize=10.2, loc="left", pad=32)
        ax.text(0, 1.072, source, transform=ax.transAxes, fontsize=7.2,
                color="#8a8a8a", va="bottom", style="italic")
        ax.text(0, 1.016, howto, transform=ax.transAxes, fontsize=7.5,
                color="#444", va="bottom")
        ax.set_xlabel("Year", fontsize=9)
        ax.set_ylabel(ylab, fontsize=9)
        ax.grid(alpha=0.20)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8.2)

    fig, ((o1, o2, o3), (o4, o5, o6)) = plt.subplots(2, 3, figsize=(15.6, 8.6))

    # (1) arXiv monthly submissions.
    rows = list(csv.DictReader((DATA / "arxiv-monthly.csv").open(encoding="utf-8")))
    xs = [frac_month(r["month"]) for r in rows]
    ys = [int(r["submissions"]) for r in rows]
    o1.plot(xs[:-1], ys[:-1], color=INK, lw=1.4, zorder=3)
    o1.scatter([xs[-1]], [ys[-1]], s=40, facecolor="none", edgecolor=INK, lw=1.3,
               zorder=4)
    o1.annotate("part\nmonth", (xs[-1], ys[-1]), textcoords="offset points",
                xytext=(-4, -22), fontsize=6.8, color="#666", linespacing=1.2)
    o1.set_xlim(1991, 2028.5)
    o1.set_ylim(0, max(ys) * 1.2)
    era(o1, 2028.5)
    dress(o1, "Other 1  papers: arXiv submissions",
          "New submissions that month",
          "Source: arxiv.org/stats monthly-submissions download",
          "Every submission since 1991. Volume, not quality or discovery.")
    o1.text(0.03, 0.80, "17,271 in Nov 2022;\n32,040 in Jun 2026 —\n"
                        "+85% in 3.7 years, after\ndecades of steady growth",
            transform=o1.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (2) GitHub pushes per quarter.
    rows = list(csv.DictReader((DATA / "github-innovationgraph-global.csv").open(encoding="utf-8")))
    def frac_q(q):
        y, qq = q.split("-Q")
        return int(y) + (int(qq) - 0.5) / 4
    xs = [frac_q(r["quarter"]) for r in rows]
    ys = [int(r["git_pushes"]) / 1e6 for r in rows]
    o2.plot(xs, ys, color=INK, lw=1.6, marker="o", ms=3.2, zorder=3)
    o2.set_xlim(2019.8, 2027.2)
    o2.set_ylim(0, max(ys) * 1.18)
    era(o2, 2027.2)
    dress(o2, "Other 2  code: git pushes to GitHub",
          "Million pushes that quarter",
          "Source: github/innovationgraph, summed over economies here",
          "A push is an upload of commits. The platform's own count.")
    o2.text(0.03, 0.80, "135M in 2022-Q4, 168M in\n2024-Q4, 320M in 2026-Q1 —\n"
                        "the one output series here\nthat clearly bends upward",
            transform=o2.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (3) Stack Overflow questions per month.
    rows = list(csv.DictReader((DATA / "stackoverflow-questions-monthly.csv").open(encoding="utf-8")))
    xs = [frac_month(r["month"]) for r in rows]
    ys = [int(r["questions"]) / 1000 for r in rows]
    o3.plot(xs, ys, color=INK, lw=1.6, zorder=3)
    chatgpt = 2022 + 10.5 / 12
    o3.axvline(chatgpt, color="#666", ls=":", lw=1.1, zorder=2)
    o3.text(chatgpt - 0.1, 0.28, "ChatGPT released,\nNov 2022", fontsize=7.2,
            color="#555", ha="right", transform=o3.get_xaxis_transform(),
            linespacing=1.35)
    o3.set_xlim(2018.8, 2027.2)
    o3.set_ylim(0, max(ys) * 1.18)
    era(o3, 2027.2)
    dress(o3, "Other 3  Q&A: Stack Overflow questions",
          "Thousand questions that month",
          "Source: Stack Exchange API, surviving questions by creation date",
          "Deleted questions vanish retroactively, so old months are undercounts.")
    o3.text(0.60, 0.62, "149,549 in Jan 2019;\n109,341 in Nov 2022;\n"
                        "2,054 in Jun 2026 —\na 98% collapse",
            transform=o3.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (4) Crossref DOIs registered per year.
    rows = list(csv.DictReader((DATA / "crossref-dois-by-year.csv").open(encoding="utf-8")))
    ys_ = [int(r["year"]) for r in rows]
    vs = [int(r["dois_created"]) / 1e6 for r in rows]
    part = [i for i, r in enumerate(rows) if "YTD" in r.get("note", "") or r["year"] == "2026"]
    o4.bar(ys_, vs, color=INK, width=0.72, zorder=3)
    for i in part:
        o4.bar([ys_[i]], [vs[i]], color="none", edgecolor="#555", lw=1.0,
               width=0.72, zorder=4)
        o4.annotate("part\nyear", (ys_[i], vs[i]), textcoords="offset points",
                    xytext=(8, -2), fontsize=6.8, color="#666", va="center",
                    linespacing=1.2)
    from matplotlib.ticker import MaxNLocator
    o4.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    o4.set_xlim(2009, 2028.2)
    o4.set_ylim(0, max(vs) * 1.22)
    o4.axvspan(ANNUAL_BAR_HIGHLIGHT_START, 2028.2, color=AI, alpha=0.06,
               zorder=0)
    o4.text(2025.58, 0.975, HIGHLIGHT_LABEL,
            transform=o4.get_xaxis_transform(), fontsize=7.4,
            color=AI, va="top")
    dress(o4, "Other 4  publishing: DOIs deposited with Crossref",
          "Million DOI records that year",
          "Source: Crossref REST API, counted here by created date",
          "Deposit date, not publication date: backfiles land in odd years.")
    o4.text(0.03, 0.80, "5.3M in 2010, 12.8M in 2025.\nRising before the shaded\n"
                        "2026 period; no clean bend",
            transform=o4.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (5) PyPI total projects, from dated Wayback captures of the front page.
    rows = list(csv.DictReader((DATA / "pypi-projects-over-time.csv").open(encoding="utf-8")))
    def frac_d(d):
        parts = (d.split("-") + ["1", "1"])[:3]
        return int(parts[0]) + (int(parts[1]) - 1) / 12 + (int(parts[2]) - 1) / 365
    xs = [frac_d(r["date"]) for r in rows]
    ys = [int(r["projects"]) / 1000 for r in rows]
    o5.plot(xs, ys, color=INK, lw=1.6, marker="o", ms=3.0, zorder=3)
    o5.set_xlim(2018.8, 2027.2)
    o5.set_ylim(0, max(ys) * 1.18)
    era(o5, 2027.2)
    dress(o5, "Other 5  packages: PyPI total projects",
          "Thousand projects (cumulative)",
          "Source: assembled here from Wayback captures of pypi.org",
          "A stock, not a flow: the counter on the front page, quarterly.")
    o5.text(0.03, 0.80, "163,524 in Jan 2019;\n861,282 live on 2026-07-28.\n"
                        "The slope steepens after 2024",
            transform=o5.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (6) the key.
    o6.axis("off")
    o6.text(0, 1.00, "How to read these panels", fontsize=10.0, va="top",
            fontweight="bold")
    o6.text(0, 0.93,
            "Years on the x-axis, a volume of written output on\n"
            "the y-axis. Shaded band: Jan 1, 2026 onward.\n"
            "Open marker or outlined bar: a part period.\n"
            "None of these series has authorship labels, so no\n"
            "AI share can be read off them.",
            fontsize=8.0, va="top", linespacing=1.7, color="#333")
    o6.text(0, 0.56, "What they show", fontsize=10.0, va="top", fontweight="bold")
    o6.text(0, 0.49,
            "The volume of artifacts — papers, pushes, packages —\n"
            "bends upward before and into 2026, and the series\n"
            "that measures asking other humans collapses.\n\n"
            "Set against the three domain documents: output\n"
            "volume accelerates while the discovery and record\n"
            "curves in cyber, math, and algorithms do not bend.\n"
            "Volume is where AI's flow is unmistakable; progress\n"
            "is where it has to be argued for.",
            fontsize=7.8, va="top", linespacing=1.65, color="#333")

    fig.suptitle(
        "Outside the three domains: five output-volume series in one format — "
        "years on x, volume on y, Jan 1, 2026 onward shaded.\n"
        "These count artifacts produced, not discoveries: the volume curves bend "
        "where the domain documents' discovery curves do not.",
        fontsize=11.5, x=0.006, ha="left", y=0.997, linespacing=1.45)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(OUT / "domain-curves-other.png", dpi=155)
    plt.close(fig)
    print("wrote domain-curves-other")


def scored_fields() -> None:
    """Scored fields outside the three domains, ordered by verification cost.

    Weather (checked against reality in days), integer factorization (checked
    instantly, but records arrive rarely), and sphere-packing lower bounds (a
    human bound ladder that accelerated immediately before 2026). These are discovery
    and records series, deliberately NOT mixed into the output-volume figure,
    since the whole point of that one is that volume and discovery diverge.
    Entries: #src-weather-forecasting, #src-factoring, #src-sphere-packing.

    The weather panel plots the two text-stated skill anchors and the stated
    rate, NOT a digitized series — ECMWF's chart blocks automated fetching, and
    the panel says so on its face rather than implying data that was not read.
    """
    import csv

    AI, HUM, INK = "#c1442f", "#2f6cc1", "#37474f"
    DATA = ROOT / "data"

    def era(ax, x1):
        ax.axvspan(HIGHLIGHT_START, x1, color=AI, alpha=0.06, zorder=0)
        ax.text(HIGHLIGHT_START + 0.4, 0.975, HIGHLIGHT_LABEL,
                transform=ax.get_xaxis_transform(),
                fontsize=7.4, color=AI, va="top")

    def dress(ax, title, ylab, source, howto):
        ax.set_title(title, fontsize=10.2, loc="left", pad=32)
        ax.text(0, 1.072, source, transform=ax.transAxes, fontsize=7.2,
                color="#8a8a8a", va="bottom", style="italic")
        ax.text(0, 1.016, howto, transform=ax.transAxes, fontsize=7.5,
                color="#444", va="bottom")
        ax.set_xlabel("Year", fontsize=9)
        ax.set_ylabel(ylab, fontsize=9)
        ax.grid(alpha=0.20)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8.2)

    fig, ((w1, w2), (w3, w4)) = plt.subplots(2, 2, figsize=(13.6, 8.8))

    # (1) weather: anchors + the stated rate + the ML arrivals -------------
    rows = list(csv.DictReader((DATA / "weather-forecast-skill.csv").open(encoding="utf-8")))
    anchors = [(int(r["year"]), float(r["value"])) for r in rows
               if r["metric"].startswith("useful_forecast_length")]
    w1.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=54, color=HUM,
               zorder=5, edgecolor="white", lw=0.7)
    for i, (x, y) in enumerate(anchors):
        # the earliest anchor sits at the left spine, so its label goes right
        side = (7, -14) if i == 0 else (-6, -18)
        w1.annotate(f"{y} days ({x})", (x, y), textcoords="offset points",
                    xytext=side, fontsize=7.2, color=HUM,
                    ha="left" if i == 0 else "right")
    # the stated rate: one day per decade, drawn from the 1985 anchor. Dashed
    # and labelled, because it is the source's rate claim and not measured data.
    xs = [1985, 2026]
    ys = [6.5, 6.5 + (2026 - 1985) / 10.0]
    w1.plot(xs, ys, color=HUM, ls="--", lw=1.4, zorder=3)
    w1.text(1979, 10.9, "the stated rate: about one day of skill per decade,\n"
                        "sustained ~40 years — drawn from the source's\n"
                        "claim, not a digitized series",
            fontsize=7.3, color="#444", va="top", linespacing=1.45)
    ml = [(2022.15, "FourCastNet"), (2022.84, "Pangu"), (2023.87, "GraphCast"),
          (2024.93, "GenCast"), (2025.15, "AIFS operational")]
    for x, lab in ml:
        w1.scatter([x], [5.0], s=40, color=AI, marker="^", zorder=5,
                   edgecolor="white", lw=0.5)
    w1.annotate("4 ML models beat the physics\nincumbent, 2022–2025;\n"
                "ECMWF then shipped its own",
                (2022.1, 5.0), xytext=(2003, 5.6), textcoords="data",
                fontsize=7.3, color=AI, linespacing=1.4, va="center",
                arrowprops=dict(arrowstyle="->", color=AI, lw=0.7,
                                connectionstyle="arc3,rad=-0.12"))
    w1.set_xlim(1976, 2029)
    w1.set_ylim(4.2, 11.4)
    era(w1, 2029)
    dress(w1, "Weather: skill gained ~1 day per decade for 40 years",
          "Forecast days of useful skill",
          "Source: ECMWF verification framework; anchors via a 2003 review",
          "Skill gains from ML are 4–25%. Its cost gain is ~1000x.")

    # (2) factoring: the series that stopped --------------------------------
    rows = [r for r in csv.DictReader((DATA / "factoring-records.csv").open(encoding="utf-8"))
            if r["domain"] == "integer_factorization"]
    rows.sort(key=lambda r: r["date"])
    best, series = 0, []
    for r in rows:
        d = int(r["digits"])
        if d > best:
            best = d
            series.append((int(r["date"][:4]) + (int(r["date"][5:7]) - 0.5) / 12, d,
                           r["record"]))
    xs = [s[0] for s in series] + [2026.6]
    ys = [s[1] for s in series] + [series[-1][1]]
    w2.plot(xs, ys, drawstyle="steps-post", color=HUM, lw=1.9, zorder=3)
    w2.scatter([s[0] for s in series], [s[1] for s in series], s=34, color=HUM,
               zorder=4, edgecolor="white", lw=0.5)
    for x, y, lab in series:
        if lab in ("RSA-100", "RSA-768", "RSA-250"):
            w2.annotate(lab, (x, y), textcoords="offset points", xytext=(-4, 9),
                        fontsize=7.2, color=HUM, ha="right")
    w2.annotate("no record in 6 years", (2023.3, series[-1][1]),
                textcoords="offset points", xytext=(0, -22), fontsize=7.6,
                color=AI, ha="center")
    w2.set_xlim(1988, 2029)
    w2.set_ylim(80, 275)
    era(w2, 2029)
    dress(w2, "Factoring: 7 digits a year, then 1.8, then nothing",
          "Digits in the largest number factored",
          "Source: RSA Factoring Challenge record list, counted here",
          "Verification is instant and free. The series still stopped.")
    w2.text(0.03, 0.90, "13 records, 1991–2020.\nNone involved machine learning",
            transform=w2.transAxes, fontsize=7.3, color="#333", va="top",
            linespacing=1.5)

    # (3) sphere packing: a human ladder that accelerated -------------------
    rows = list(csv.DictReader(
        (DATA / "sphere-packing-lower-bound-records.csv").open(encoding="utf-8")))
    yrs = [int(r["year"]) for r in rows]
    ordinals = list(range(1, len(rows) + 1))
    w3.step(yrs + [2026.6], ordinals + [ordinals[-1]], where="post", color=HUM,
            lw=1.9, zorder=3)
    w3.scatter(yrs, ordinals, s=38, color=HUM, zorder=4, edgecolor="white", lw=0.5)
    labels = {1905: "Minkowski–Hlawka", 1947: "Rogers", 1992: "Ball",
              2013: "Venkatesh", 2023: "Campos et al.", 2025: "Klartag"}
    for y, o in zip(yrs, ordinals):
        if y in labels:
            first = y == yrs[0]
            w3.annotate(labels[y], (y, o), textcoords="offset points",
                        xytext=(7, 3) if first else (-6, 4), fontsize=7.0,
                        color=HUM, ha="left" if first else "right")
            labels.pop(y)
    w3.set_xlim(1895, 2035)
    w3.set_ylim(0.3, len(rows) + 1.4)
    era(w3, 2035)
    dress(w3, "Sphere packing: the two biggest steps since 1947 are 2023 and 2025",
          "Cumulative improvements to the bound",
          "Source: the standard record ladder as the recent literature records it",
          "Every step is a human proof. No AI anywhere in this series.")
    w3.text(0.04, 0.90, "The recent bend just before 2026\nis entirely human",
            transform=w3.transAxes, fontsize=7.6, color=AI, va="top",
            linespacing=1.5)

    # (4) the key -----------------------------------------------------------
    w4.axis("off")
    w4.text(0, 1.00, "What these three show", fontsize=10.5, va="top",
            fontweight="bold")
    w4.text(0, 0.945,
            "The three worked domains all have cheap verifiers, so\n"
            "alone they cannot test the claim that cheap verification\n"
            "is what lets AI contribute. These span the cost of a\n"
            "check instead.\n\n"
            "Weather has the cheapest verifier there is — reality\n"
            "checks the forecast in days, blind, for free — and four\n"
            "ML models beat the physics incumbent, which then\n"
            "shipped its own. But the skill trend did not steepen:\n"
            "the gains are 4–25% against a ~1000x cut in the cost\n"
            "of a forecast. A cost curve bent, not a discovery curve.\n\n"
            "Factoring is checked instantly and has stood still\n"
            "since Feb 2020, after ~7 digits a year to 2009.\n\n"
            "Sphere packing accelerated immediately before the\n"
            "highlighted period, and every step is a human proof.",
            fontsize=7.7, va="top", linespacing=1.5, color="#333")

    fig.suptitle(
        "Scored fields outside the three domains, ordered by how cheap their "
        "verifier is: weather (days, free), factoring (instant), bound proofs "
        "(peer review).\n"
        "None of the three shows AI bending a discovery curve. Weather shows it "
        "bending a cost curve instead, by three orders of magnitude.",
        fontsize=11.5, x=0.006, ha="left", y=0.997, linespacing=1.45)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(OUT / "scored-fields.png", dpi=155)
    plt.close(fig)
    print("wrote scored-fields")


def alphaevolve_frame() -> None:
    """The AlphaEvolve problem set: what it contains, and what a baseline can use.

    Left: the status composition of the problems the paper numbers, from the
    repository's own status.json under the assumed index mapping. Right: how
    many survive each filter needed to compare an AI record step against the
    historical steps on the same quantity. Both read the inventory CSV; the last
    two funnel rows come from the record sample.
    """
    import csv
    from collections import Counter

    path = ROOT / "data/alphaevolve-inventory.csv"
    if not path.exists():
        print("skipped alphaevolve frame: run alphaevolve_inventory.py in ai-discovery-data, then its make sync")
        return
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
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
    fig.savefig(OUT / "alphaevolve-frame-funnel.png", dpi=170)
    plt.close(fig)
    print(f"wrote alphaevolve-frame-funnel ({len(rows)} problems, {live} in frame)")


def alphaevolve_records() -> None:
    """AI record steps against human steps on the same quantities.

    From data/alphaevolve-records.csv, built by
    ai-discovery-data's alphaevolve_records.py: a pre-committed sample of twelve AlphaEvolve
    problems plus the 2026-07-28 extension that completes the record-status
    frame. Three sequence panels show representative head-to-heads (the
    richest contested quantity, the leapfrogging case, and the kissing number
    whose record has since moved to a collective agent platform); the right
    panel pools every record step in the frame. Steps flagged is_record=no
    (AlphaEvolve improving a cited value that was not the actual record) are
    excluded from the pool.
    """
    path = ROOT / "data/alphaevolve-records.csv"
    if not path.exists():
        print("skipped alphaevolve records: run alphaevolve_records.py in ai-discovery-data, then its make sync")
        return

    import csv
    from collections import defaultdict

    series: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
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
        "step with a computable size, 12 quantities carrying both AI and "
        "non-AI steps.",
        fontsize=11.5, x=0.006, ha="left", y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(OUT / "alphaevolve-record-steps.png", dpi=170)
    plt.close(fig)
    print(f"wrote alphaevolve-record-steps ({len(steps)} steps)")


def antedb_small_multiples() -> None:
    """One raw time series per panel, for every slice of all three families.

    The four-panel version of this was too dense to read. Small multiples keep
    each series raw, with real values on its own axis, and make the panels
    comparable by giving every one the same framing: y runs from 0 to a little
    above that slice's earliest value, so the fraction of the panel the line
    descends is the fraction of the bound that has been removed. A line hugging
    the top means a century bought almost nothing; a line reaching the floor
    means the bound was eliminated.
    """
    path = ROOT / "data/antedb-sweep.csv"
    if not path.exists():
        print("skipped antedb small multiples: run antedb_extract.py in ai-discovery-data, then its make sync")
        return

    import csv
    from collections import defaultdict

    rows: dict[tuple[str, float], list[tuple[int, float]]] = defaultdict(list)
    label_of: dict[tuple[str, float], str] = {}
    for row in csv.DictReader(path.open(encoding="utf-8")):
        key = (row["quantity"], float(row["point_float"]))
        rows[key].append((int(row["year"]), float(row["value_float"])))
        label_of[key] = row["point"]
    for key in rows:
        rows[key].sort()

    # Ten slices per family, evenly spread over the grid, so each row of the
    # figure reads left to right as the parameter increases.
    families = [
        ("mu", r"\mu", "#2f6cc1"),
        ("A", "A", "#e0a020"),
        ("beta", r"\beta", "#2f8f5b"),
    ]
    # Ten slices per family, hand-picked rather than sampled uniformly, so that
    # the points with standard names and standard conjectures attached are all
    # present: mu(1/2) is the Lindelof exponent, A(3/4) is the slice Ingham
    # bounded in 1940 and Guth-Maynard improved in 2024, and beta near 0.325 is
    # the dead zone. Uniform sampling dropped all three.
    wanted = {
        "mu": [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.975],
        "A": [0.525, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975],
        "beta": [0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.325, 0.4, 0.475],
    }
    chosen: dict[str, list] = {}
    for quantity, _, _ in families:
        points = sorted(k[1] for k in rows if k[0] == quantity)
        if not points:
            chosen[quantity] = []
            continue
        picked = []
        for target in wanted[quantity]:
            nearest = min(points, key=lambda p: abs(p - target))
            if nearest not in picked:
                picked.append(nearest)
        chosen[quantity] = picked

    ncols, nrows = 5, 6
    fig, axes = plt.subplots(nrows, ncols, figsize=(15.0, 15.4))

    panel = 0
    for quantity, symbol, colour in families:
        for point in chosen[quantity]:
            ax = axes[panel // ncols][panel % ncols]
            panel += 1
            series = rows[(quantity, point)]
            xs = [r[0] for r in series] + [2026]
            ys = [r[1] for r in series] + [series[-1][1]]
            first, last = series[0][1], series[-1][1]

            ax.fill_between(xs, 0, ys, step="post", color=colour, alpha=0.13, zorder=1)
            ax.plot(xs, ys, drawstyle="steps-post", lw=1.9, color=colour, zorder=3)
            ax.scatter([r[0] for r in series], [r[1] for r in series], s=13,
                       color=colour, zorder=4, edgecolor="white", linewidth=0.4)

            ax.set_ylim(0, first * 1.14)
            ax.set_xlim(1913, 2030)
            ax.set_xticks([1920, 1960, 2000])
            ax.set_yticks([0, first])
            ax.set_yticklabels(["0", f"{first:.4g}"], fontsize=8)
            ax.tick_params(axis="x", labelsize=8)
            # Both raw values go in the title, where nothing can overlap them.
            ax.set_title(
                f"${symbol}({label_of[(quantity, point)]})$   "
                f"{first:.4g} → {last:.4g}",
                fontsize=9.8, loc="left", pad=5,
            )
            # "last moved" rather than a span between records: every series is
            # observed to the present, so the gap between the first and last
            # record is not the observation window.
            ax.text(0.97, 0.06,
                    f"×{last / first:.2f}\nlast moved {series[-1][0]}\n"
                    f"{len(series)} record" + ("s" if len(series) != 1 else ""),
                    transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=8, color="#555", linespacing=1.35)
            if quantity == "A":
                # The density hypothesis is a real threshold, so mark it where
                # it falls inside the panel.
                if 2 < first * 1.14:
                    ax.axhline(2, color="#666", ls="--", lw=1.0, zorder=2)
            ax.grid(axis="y", alpha=0.18)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)

    for blank in range(panel, nrows * ncols):
        axes[blank // ncols][blank % ncols].axis("off")

    fig.suptitle(
        "Best known value of each exponent over time, one panel per slice\n"
        "Every panel spans 0 to its own starting value, so how far the line drops "
        "is the fraction of the bound removed. Dashed line on the $A$ panels is the "
        "density hypothesis.",
        fontsize=12.5, x=0.008, ha="left", y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(OUT / "antedb-small-multiples.png", dpi=150)
    plt.close(fig)
    print(f"wrote antedb-small-multiples ({panel} panels)")


def antedb_improvement_by_parameter() -> None:
    """One compact summary: how much each function improved, against its parameter.

    The per-slice time series live in the small-multiples figure. This is the
    thing those thirty panels cannot show at a glance — that the century's
    improvement depends strongly on where on each function you look.
    """
    path = ROOT / "data/antedb-sweep.csv"
    if not path.exists():
        print("skipped antedb summary: run antedb_extract.py in ai-discovery-data, then its make sync")
        return

    import csv
    from collections import defaultdict

    series: dict[tuple[str, float], list[tuple[int, float]]] = defaultdict(list)
    for row in csv.DictReader(path.open(encoding="utf-8")):
        series[(row["quantity"], float(row["point_float"]))].append(
            (int(row["year"]), float(row["value_float"]))
        )
    for key in series:
        series[key].sort()

    styles = {
        "mu": ("#2f6cc1", r"$\mu(\sigma)$", "o"),
        "A": ("#e0a020", r"$A(\sigma)$", "s"),
        "beta": ("#2f8f5b", r"$\beta(\alpha)$", "^"),
    }

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    summary = {}
    for quantity, (colour, name, marker) in styles.items():
        points = sorted(k[1] for k in series if k[0] == quantity)
        if not points:
            continue
        xs, ys, counts = [], [], []
        for point in points:
            rows = series[(quantity, point)]
            xs.append(point)
            ys.append(rows[-1][1] / rows[0][1])
            counts.append(len(rows))
        summary[quantity] = (xs, ys, counts)
        ax.plot(xs, ys, lw=1.7, color=colour, marker=marker, ms=4.6,
                markeredgecolor="white", markeredgewidth=0.5, zorder=3)
        ax.text(xs[-1] + 0.013, ys[-1], name, fontsize=10, color=colour, va="center")

    ax.axhline(1.0, color="#333", lw=1.1, ls=":", zorder=2)
    ax.text(0.015, 1.014, "no improvement at all", fontsize=8.8, color="#555")
    ax.set_ylim(0.12, 1.075)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel(r"Parameter: $\sigma$ for $\mu$ and $A$, $\alpha$ for $\beta$",
                  fontsize=10)
    ax.set_ylabel("Latest bound ÷ earliest bound, whole record", fontsize=10)
    ax.set_title("How much a century bought, by where on the function you look",
                 fontsize=12, loc="left", pad=10)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    flat = sum(1 for c in summary.get("beta", ([], [], []))[2] if c <= 1)
    if flat:
        ax.text(0.015, 0.22,
                f"Lower is more improvement.\n{flat} of the "
                r"$\beta$ points never moved once.",
                fontsize=9, color="#333", va="center")

    fig.tight_layout()
    fig.savefig(OUT / "antedb-improvement-by-parameter.png", dpi=170)
    plt.close(fig)

    print("ANTEDB improvement by parameter:")
    for quantity, (xs, ys, counts) in summary.items():
        print(f"  {quantity}: {len(xs)} points, ratio {min(ys):.3f}-{max(ys):.3f}, "
              f"records {min(counts)}-{max(counts)}")


def famous_problem_lists() -> None:
    """Prestige / corpus open-problem lists: tracks + a status-stock panel.

    Track panels (Hilbert, Landau, Smale, Millennium, Thurston, TOPP): one
    horizontal track per scored row. The Scottish Book is deliberately omitted:
    Mauldin's 2015 appendix mixes unsolved / no-commentary / unknown rows, is a
    decade stale, and there is still no complete current fall ledger. The Erdős
    panel plots site-status snapshots, which can lag the dates of the
    mathematical results. Data under data/. Entry:
    #src-famous-problem-lists.
    """
    import csv
    from collections import defaultdict
    from datetime import date as date_cls

    path = ROOT / "data/famous-open-problem-lists.csv"
    if not path.exists():
        print("skipped famous-problem-lists: CSV missing")
        return

    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    by_list: dict[str, list[dict]] = defaultdict(list)
    meta: dict[str, tuple[str, int]] = {}
    for row in rows:
        by_list[row["list_id"]].append(row)
        meta[row["list_id"]] = (row["list_name"], int(row["list_year"]))

    prestige_order = ["hilbert", "landau", "smale", "millennium"]
    colours = {
        "hilbert": "#2f6cc1",
        "landau": "#8c8c8c",
        "smale": "#c98a00",
        "millennium": "#c1442f",
        "thurston": "#6b4f9a",
        "topp": "#1a7a6d",
        "erdos": "#5b3d8a",
    }
    labels = {
        ("hilbert", "3"): "Dehn 1900",
        ("hilbert", "10"): "Matiyasevich 1970",
        ("hilbert", "18c"): "Hales 1998",
        ("hilbert", "8a"): "Riemann (open)",
        ("smale", "14"): "Tucker 2002",
        ("smale", "2"): "Perelman 2003",
        ("smale", "17"): "Lairez 2016 (online)",
        ("smale", "16"): "Alpöge–Fable 2026",
        ("millennium", "poincare"): "Perelman 2003",
        ("millennium", "riemann"): "Riemann (open)",
        ("thurston", "1"): "Perelman 2003",
        ("thurston", "16"): "Agol 2012",
        ("thurston", "18"): "Agol 2013",
        ("thurston", "19"): "arithmetic quotients (open)",
        ("thurston", "23"): "volume independence (open)",
        ("topp", "1"): "Mulzer–Rote 2006",
        ("topp", "2"): "Rubin 2015",
        ("topp", "21"): "Wang 2023",
    }
    NOW = 2026.6
    SHADE = "#c1442f"

    fig = plt.figure(figsize=(17.4, 14.2))
    gs = fig.add_gridspec(
        5, 2, height_ratios=[1.0, 1.0, 1.25, 1.15, 1.15],
        hspace=0.36, wspace=0.16,
    )
    prestige_axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(2)]
    thurston_ax = fig.add_subplot(gs[2, :])
    topp_ax = fig.add_subplot(gs[3, :])
    erdos_ax = fig.add_subplot(gs[4, :])

    def shade(ax, x1: float) -> None:
        ax.axvspan(HIGHLIGHT_START, x1, color=SHADE, alpha=0.06, zorder=0)

    def draw_track_panel(ax, list_id: str) -> None:
        name, year0 = meta[list_id]
        items = by_list[list_id]

        def sort_key(r: dict) -> tuple:
            st = r["status"]
            rank = {
                "resolved": 0, "open": 1, "partial": 2,
                "contested": 3, "vague": 4,
            }.get(st, 5)
            ry = int(r["resolved_year"]) if r["resolved_year"] else 9999
            # numeric then lexical problem ids
            try:
                pid_key = (0, int(r["problem_id"]))
            except ValueError:
                pid_key = (1, r["problem_id"])
            return (rank, ry, pid_key)

        items = sorted(items, key=sort_key)
        n = len(items)
        colour = colours[list_id]
        n_res = sum(1 for r in items if r["status"] == "resolved")
        n_open = sum(1 for r in items if r["status"] == "open")
        n_other = sum(
            1 for r in items if r["status"] in ("partial", "contested", "vague"))

        for i, r in enumerate(items):
            y = n - i
            st = r["status"]
            if st == "resolved" and r["resolved_year"]:
                x = int(r["resolved_year"])
                ax.plot([year0, x], [y, y], color=colour, lw=1.0,
                        alpha=0.35, zorder=2)
                ax.scatter([x], [y], s=26, color=colour, zorder=4,
                           edgecolor="white", lw=0.45)
            elif st == "open":
                ax.plot([year0, NOW], [y, y], color="#bbbbbb", lw=0.85,
                        alpha=0.5, zorder=2)
                ax.scatter([NOW], [y], s=24, facecolor="none",
                           edgecolor=colour, lw=1.15, zorder=4)
            else:
                ax.plot([year0, NOW], [y, y], color="#dddddd", lw=0.7,
                        ls=":", zorder=1)
                ax.scatter([NOW], [y], s=14, color="#cccccc", zorder=3)

            key = (list_id, r["problem_id"])
            if key in labels:
                x = (int(r["resolved_year"])
                     if r["status"] == "resolved" and r["resolved_year"] else NOW)
                right_edge = r["status"] == "open" or x > NOW - 6
                ax.annotate(
                    labels[key], (x, y), textcoords="offset points",
                    xytext=((-5, 0) if right_edge else (5, 0)),
                    fontsize=6.2, color=colour, va="center",
                    ha=("right" if right_edge else "left"),
                )

        pad = 8 if year0 < 1950 else 2
        x1 = NOW + 1.5
        ax.set_xlim(year0 - pad, x1)
        shade(ax, x1)
        ax.set_ylim(0.3, max(n, 1) + 0.7)
        ax.set_yticks([])
        if list_id == "hilbert":
            title = (
                f"{name} ({year0}): {n_res} resolved rows (≈10 problem numbers), "
                f"{n_open} open, {n_other} disputed/vague"
            )
        elif list_id == "smale":
            title = (
                f"{name} ({year0}): {n_res} resolved rows (18 problems; #11 split), "
                f"{n_open} open, {n_other} disputed"
            )
        elif list_id == "thurston":
            title = (
                f"{name} ({year0}): {n_res} resolved (Wikipedia ledger), "
                f"{n_open} open"
            )
        elif list_id == "topp":
            title = (
                f"{name} ({year0}–): {n_res} source-marked solved/settled/closed, "
                f"{n_open} open, {n_other} partial"
            )
        else:
            title = (
                f"{name} ({year0}): {n_res} resolved"
                + (f", {n_open} open" if n_open else "")
                + (f", {n_other} disputed/vague" if n_other else "")
            )
        ax.set_title(title, fontsize=8.8, loc="left", pad=3, color=colour)

    def style_ax(ax) -> None:
        ax.grid(axis="x", alpha=0.22, zorder=0)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(labelsize=7.4)

    def draw_erdos_panel(ax) -> None:
        hist_path = ROOT / "data/erdos-database-history.csv"
        colour = colours["erdos"]
        if not hist_path.exists():
            ax.set_title("Erdős problems: history CSV missing", fontsize=9.0,
                         loc="left", color=colour)
            return
        hist = list(csv.DictReader(hist_path.open(encoding="utf-8")))

        def to_year(iso: str) -> float:
            y, m, d = (int(p) for p in iso.split("-"))
            return y + (date_cls(y, m, d).timetuple().tm_yday - 1) / 365.25

        xs = [to_year(r["date"]) for r in hist]
        solved = [int(r["total_solved"]) for r in hist]
        total = [int(r["total_problems"]) for r in hist]
        ax.fill_between(xs, solved, total, color=colour, alpha=0.10, zorder=1)
        ax.plot(xs, total, color="#aaaaaa", lw=1.3, zorder=2)
        ax.plot(xs, solved, color=colour, lw=1.8, zorder=3)
        ax.scatter(xs, solved, s=28, color=colour, zorder=4,
                   edgecolor="white", lw=0.5)
        ax.annotate(f"{solved[-1]} recorded solved", (xs[-1], solved[-1]),
                    textcoords="offset points", xytext=(-6, 8), fontsize=6.8,
                    color=colour, ha="right")
        ax.annotate(f"{total[-1]} catalogued", (xs[-1], total[-1]),
                    textcoords="offset points", xytext=(-6, 6), fontsize=6.8,
                    color="#777777", ha="right")
        for x, lab in (
            (to_year("2026-01-06"), "#728"),
            (to_year("2026-05-20"), "#90 unit-distance"),
        ):
            ax.axvline(x, color=colour, lw=0.75, alpha=0.35, zorder=2)
            ax.annotate(lab, (x, max(total) * 1.02), rotation=90, fontsize=6.0,
                        color=colour, va="bottom", ha="right",
                        xytext=(-2, 0), textcoords="offset points")
        x0, x1 = xs[0] - 0.05, xs[-1] + 0.12
        ax.set_xlim(x0, x1)
        shade(ax, x1)
        ax.set_ylim(0, max(total) * 1.12)
        ax.set_ylabel("problems", fontsize=7.8)
        ax.set_title(
            f"Erdős problems: {solved[-1]} of {total[-1]} "
            f"(site-status snapshots, not solution dates)",
            fontsize=8.8, loc="left", pad=3, color=colour,
        )
        tick_idx = list(range(0, len(hist), 2))
        if tick_idx[-1] != len(hist) - 1:
            tick_idx.append(len(hist) - 1)
        ax.set_xticks([xs[i] for i in tick_idx])
        ax.set_xticklabels([hist[i]["month"] for i in tick_idx], fontsize=7.4)
        ax.set_xlabel("Site snapshot", fontsize=8.2)

    for ax, list_id in zip(prestige_axes, prestige_order):
        style_ax(ax)
        ax.spines["left"].set_visible(False)
        draw_track_panel(ax, list_id)

    for ax, list_id in ((thurston_ax, "thurston"), (topp_ax, "topp")):
        style_ax(ax)
        ax.spines["left"].set_visible(False)
        draw_track_panel(ax, list_id)

    topp_ax.set_xlabel(
        "Horizontal tracks run from list start (TOPP: 2001) to resolution "
        "year (filled) or current open status (hollow); entry dates not encoded",
        fontsize=8.0,
    )

    style_ax(erdos_ax)
    draw_erdos_panel(erdos_ax)

    fig.suptitle(
        "Selected open-problem lists: scored fall tracks and Erdős catalogue stock\n"
        "Filled circles are dated solution landmarks under each ledger's rule; "
        "hollow circles are currently open. Shaded band: Jan 1, 2026 onward. "
        "Scottish Book omitted: no current fall ledger.",
        fontsize=11.5, x=0.01, ha="left", y=0.995,
    )
    handles = [
        Line2D([], [], marker="o", ls="", color="#2f6cc1",
               label="solution landmark"),
        Line2D([], [], marker="o", ls="", markerfacecolor="none", color="#2f6cc1",
               label="still open"),
        Line2D([], [], marker="o", ls="", color="#cccccc",
               label="disputed / vague / partial"),
        Line2D([], [], color="#5b3d8a", lw=1.8, label="Erdős recorded solved"),
        Line2D([], [], color="#aaaaaa", lw=1.3, label="Erdős catalogued"),
        Patch(facecolor=SHADE, alpha=0.06, edgecolor="none",
              label=HIGHLIGHT_LABEL),
    ]
    fig.legend(handles=handles, loc="upper right", fontsize=7.8, frameon=False,
               bbox_to_anchor=(0.995, 0.955), ncol=3)
    fig.subplots_adjust(left=0.045, right=0.99, top=0.88, bottom=0.045)
    fig.savefig(OUT / "famous-open-problem-lists.png", dpi=150)
    plt.close(fig)
    n_track = sum(len(by_list[k]) for k in prestige_order + ["thurston", "topp"])
    print(f"wrote famous-open-problem-lists ({n_track} track-ledger rows + Erdős stock)")


def main() -> None:
    efficiency_rates()
    domain_curves()
    other_series()
    scored_fields()
    alphaevolve_frame()
    alphaevolve_records()
    problem_sets()
    antedb_small_multiples()
    antedb_improvement_by_parameter()
    famous_problem_lists()


if __name__ == "__main__":
    main()
