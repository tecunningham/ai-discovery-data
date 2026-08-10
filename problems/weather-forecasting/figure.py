#!/usr/bin/env python3
"""Draw discovery-weather-forecasting.png from this folder's two CSVs.

Run: python3 problems/weather-forecasting/figure.py

Two things are on one axis and only one of them is data. The filled points are
the two text-stated skill anchors; the dashed line is the rate the literature
states, drawn from the later anchor. ECMWF's live skill chart blocks automated
fetching, so no year-by-year series exists here to plot, and the figure has to
say which of the two marks is a measurement and which is a claim.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from matplotlib.lines import Line2D  # noqa: E402

from lib.chart import (  # noqa: E402
    AI,
    HUMAN,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv  # noqa: E402

RIGHT = 2029.0
ARRIVAL_Y = 4.3
ISO_DATE = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
OPERATIONAL = re.compile(r"operational (\d{4}-\d{2}-\d{2})")


def main() -> None:
    skill = read_csv(HERE / "weather-forecast-skill.csv")
    anchors = sorted(
        (int(row["year"]), float(row["value"]))
        for row in skill
        if row["metric"].startswith("useful_forecast_length")
    )
    rate_per_decade = next(
        float(row["value"]) for row in skill
        if row["metric"] == "skill_gain_rate_500hPa_Z"
    )

    models = read_csv(HERE / "weather-ml-models.csv")
    arrivals = [(year_fraction(ISO_DATE.search(row["date"]).group()), row["model"])
                for row in models]
    operational = [(year_fraction(match.group(1)),
                    date.fromisoformat(match.group(1)).strftime("%b %Y"))
                   for row in models
                   if (match := OPERATIONAL.search(row["date"]))]

    fig, ax = new_chart(
        "Weather forecast skill",
        "Forty years of about one day of skill per decade, and the arrival of "
        "machine-learning models that match or beat it",
    )

    ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=58, color=HUMAN,
               zorder=5, edgecolor="white", lw=0.7)
    for index, (year, value) in enumerate(anchors):
        # The later anchor is where the dashed rate line starts, so its label
        # goes to the left of the point to stay off the line.
        last = index == len(anchors) - 1
        ax.annotate(f"{value} days ({year})", (year, value),
                    textcoords="offset points",
                    xytext=(-7, 9) if last else (7, 8),
                    ha="right" if last else "left",
                    fontsize=8, color=HUMAN)

    last_year, last_value = anchors[-1]
    ax.plot([last_year, 2026],
            [last_value, last_value + (2026 - last_year) * rate_per_decade / 10.0],
            color=HUMAN, ls="--", lw=1.5, zorder=3)

    ax.scatter([a[0] for a in arrivals], [ARRIVAL_Y] * len(arrivals), s=46,
               color=AI, marker="^", zorder=5, edgecolor="white", lw=0.5)
    for x, when in operational:
        ax.axvline(x, color=AI, lw=1.1, ls=":", zorder=2)
        ax.text(x - 0.6, 6.9, f"ECMWF's own model\noperational, {when}",
                fontsize=7.8, color=AI, va="top", ha="right", linespacing=1.35)

    ax.annotate(
        " · ".join(name for _, name in arrivals[:3]) + "\n"
        + " · ".join(name for _, name in arrivals[3:]),
        (arrivals[0][0], ARRIVAL_Y), xytext=(1992, 5.4), textcoords="data",
        fontsize=7.8, color=AI, linespacing=1.4, va="center",
        arrowprops=dict(arrowstyle="->", color=AI, lw=0.7,
                        connectionstyle="arc3,rad=-0.12"),
    )

    ax.text(2024.8, 3.35,
            "Triangles mark arrival dates; their height carries no value.",
            fontsize=7.4, color="#666666", ha="right", va="bottom")

    ax.text(1978, 13.0,
            "Dashed line: the rate as the literature states it — about one day of\n"
            "skill per decade, sustained for forty years — drawn forward from the\n"
            f"{last_year} anchor. It is the source's claim, not a digitized series.",
            fontsize=8, color="#444444", va="top", linespacing=1.5)
    ax.text(1978, 10.6,
            "Reported machine-learning gains are 4–25% on skill,\n"
            "against about a 1000-fold cut in energy per forecast.\n"
            "No source here claims the forty-year trend steepened.",
            fontsize=8, color="#333333", va="top", linespacing=1.5)

    ax.set_xlim(1976, RIGHT)
    ax.set_ylim(3.0, 13.2)
    shade_era(ax, RIGHT)
    style(ax, "Forecast days of useful skill (500 hPa height, ACC 0.6)")
    ax.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color=HUMAN,
                   label="skill anchor, stated in the literature"),
            Line2D([], [], linestyle="--", color=HUMAN,
                   label="the stated rate, drawn forward (a claim, not data)"),
            Line2D([], [], marker="^", linestyle="", color=AI,
                   label="machine-learning model beats the physics incumbent"),
        ],
        loc="lower left", bbox_to_anchor=(0.0, 0.0), frameon=False, fontsize=8,
    )
    source_note(
        fig,
        "Sources: a 2003 review for the anchors, Bauer and co-authors for the rate; "
        "every model claim is its developers' own, including ECMWF's.",
    )
    save(
        fig,
        HERE / "discovery-weather-forecasting.png",
        "Weather forecast skill: two stated anchors, the stated one-day-per-decade rate, "
        "and the 2022-2025 arrival of machine-learning models.",
        [
            "https://www.ecmwf.int/en/forecasts/quality-our-forecasts",
            "https://www.nature.com/articles/nature14956",
        ],
        __file__,
    )


if __name__ == "__main__":
    main()
