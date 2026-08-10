#!/usr/bin/env python3
"""Draw efficiency-halving-times.png from the OWID 66-technology cost curves.

Run: python3 problems/technology-cost-curves/figure.py

The physical rates are fitted here from owid-66-technologies.csv. The three AI
rates are quoted from the sources named beside them and are not fitted: each is
the interval its own authors published.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from math import log
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import NullLocator  # noqa: E402

from lib.chart import AI, HUMAN  # noqa: E402
from lib.table import read_csv  # noqa: E402

MOORE_MONTHS = 24.0


def ai_rates() -> list[tuple[str, float, tuple[float, float] | None, int, int, str]]:
    """The published algorithmic-efficiency halving times, from the CSV.

    These are quotations rather than measurements: each is a rate an author
    fitted and published, with the interval they gave, and recomputing one here
    would be inventing a number the source did not state. They are in a CSV
    rather than in this file because the source log's evidence-coverage figure
    plots the same three windows, and a rate transcribed in two places is a rate
    that will eventually disagree with itself. The label carries a `|` where the
    chart breaks the line.
    """
    out = []
    for row in read_csv(HERE / "ai-efficiency-rates.csv"):
        ci = ((float(row["ci_low_months"]), float(row["ci_high_months"]))
              if row["ci_low_months"] else None)
        out.append((row["label"].replace("|", "\n"), float(row["halving_months"]),
                    ci, int(row["first_year"]), int(row["last_year"]),
                    row["source_anchor"]))
    return out


def owid_rates() -> list[tuple[str, float, int, int]]:
    """Halving time in months per technology, fitted from the OWID CSV.

    Returns (name, halving_months, first_year, last_year) for series that fall
    in cost, sorted fastest first. A log-linear fit is used rather than an
    endpoint ratio so that a noisy first or last observation cannot set the
    rate on its own.
    """
    series: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in read_csv(HERE / "owid-66-technologies.csv"):
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


def main() -> None:
    """How fast efficiency improves, across physical technologies and AI.

    Left: the window each measurement covers. Right: halving times on a log
    axis, with published 95% intervals where the source gives one. Only the
    fastest physical curves are shown; the rest of the 64 falling series are
    slower than everything plotted, and several are so nearly flat that a
    fitted halving time runs to centuries and means nothing.
    """
    owid = owid_rates()
    fastest = owid[:7]
    ai = [(n.replace("\n", " "), m, ci, a, b) for n, m, ci, a, b, _ in ai_rates()]

    fig, (ax_span, ax_rate) = plt.subplots(
        1, 2, figsize=(11.8, 5.0), gridspec_kw={"width_ratios": [1, 1.06]}
    )

    # --- left: when each measurement applies ---------------------------------
    rows = ([(n, m, a, b, HUMAN) for n, m, a, b in fastest]
            + [(n, m, a, b, AI) for n, m, _, a, b in ai])
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
    bars = ([(n, m, ci, AI) for n, m, ci, _, _ in ai]
            + [(n, m, None, HUMAN) for n, m, _, _ in fastest[:5]])
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
    # Saved directly rather than through lib.chart.save(): this figure has to
    # stay byte-identical to the composite it was extracted from, and save()
    # imposes its own dpi and margins.
    fig.savefig(HERE / "efficiency-halving-times.png", dpi=170)
    plt.close(fig)

    print("fastest falling cost curves (halving months, span):")
    for name, months, first, last in owid[:8]:
        print(f"  {name:26s} {months:6.1f}  {first}-{last}")
    print(f"  ... {len(owid)} series fall in cost overall")


if __name__ == "__main__":
    main()
