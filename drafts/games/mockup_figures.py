"""Draft mock-up charts for a possible games- section.

Standalone exploratory renderer for the hand-transcribed CSVs in this folder.
Deliberately NOT part of the pinned figure pipeline (lib/chart.py, make
figure): these PNGs are throwaway drafts, regenerable with any matplotlib.

Usage: python mockup_figures.py  (writes mockup-*.png next to the CSVs)
"""

import csv
import datetime as dt
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
TODAY = dt.date(2026, 9, 1)

INK = "#333333"
MUTED = "#767676"
GRID = "#e3e3e3"


def load(name, value_col):
    rows = []
    with open(HERE / name) as f:
        for r in csv.DictReader(f):
            rows.append(
                (
                    dt.date.fromisoformat(r["date"]),
                    float(r[value_col]),
                    r["status"],
                    r.get("player") or r.get("runner") or r.get("program", ""),
                )
            )
    return sorted(rows)


def base_axes(ax, title, subtitle):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold", pad=14)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=8, color=MUTED)


def draw(ax, rows, color, extend=True):
    dates = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    if extend:
        dates = dates + [TODAY]
        vals = vals + [vals[-1]]
    ax.step(dates, vals, where="post", color=color, linewidth=2, zorder=3)
    for d, v, status, _ in rows:
        filled = status == "verified"
        ax.plot(
            d, v, "o", ms=4.5, zorder=4,
            markerfacecolor=color if filled else "white",
            markeredgecolor=color, markeredgewidth=1.2,
        )


def annotate(ax, x, y, text, dx=0, dy=8, ha="center"):
    ax.annotate(
        text, (x, y), textcoords="offset points", xytext=(dx, dy),
        fontsize=7.5, color=INK, ha=ha,
    )


def fmt_time(s):
    return f"{int(s // 60)}:{s % 60:06.3f}"


def smb1(ax):
    rows = load("speedrun-smb1-anypercent.csv", "time_s")
    base_axes(
        ax,
        "Super Mario Bros. any% world record",
        "human real-time record, speedrun.com lineage · filled = verified row, open = approximate",
    )
    draw(ax, rows, "#2a78d6")
    ax.set_ylim(294.2, 298.4)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_time(v)))
    annotate(ax, rows[0][0], rows[0][1], "andrewg 4:58.092", dx=10, ha="left")
    annotate(ax, rows[-1][0], rows[-1][1], "Niftski 4:54.482", dx=-6, dy=10, ha="right")
    ax.axhline(294.266, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(
        dt.date(2014, 6, 1), 294.31, "tool-assisted limit 4:54.266",
        fontsize=7.5, color=MUTED, va="bottom",
    )


def ssdf(ax):
    rows = load("chess-ssdf-elo.csv", "elo")
    base_axes(
        ax,
        "Best chess program on the SSDF rating list",
        "SSDF Elo, 1984 – final list 2023 · mostly approximate pending refetch of archived lists",
    )
    draw(ax, rows, "#eb6834", extend=False)
    ax.set_ylabel("SSDF Elo", fontsize=8, color=MUTED)
    annotate(ax, rows[0][0], rows[0][1], "Novag Super\nConstellation", dx=14, dy=2, ha="left")
    annotate(ax, dt.date(2008, 9, 15), 3238, "Deep Rybka 3", dx=0, dy=6)
    annotate(ax, rows[-1][0], rows[-1][1], "list discontinued\n2023-12-31", dx=6, dy=-30, ha="right")
    ax.set_xlim(dt.date(1983, 1, 1), dt.date(2027, 6, 1))


def tetris(ax):
    rows = load("tetris-nes-score.csv", "score")
    base_axes(
        ax,
        "NES Tetris highest score",
        "community-tracked score record (log scale) · filled = verified row, open = approximate",
    )
    draw(ax, rows, "#1baf7a")
    ax.set_yscale("log")
    ax.set_ylim(8e5, 8e7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e6:g}M"))
    ax.axhline(999999, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(dt.date(2009, 8, 1), 1.05e6, "display cap 999,999", fontsize=7.5, color=MUTED, va="bottom")
    annotate(ax, dt.date(2024, 3, 11), 10.2e6, "rolling era", dx=-30, dy=4)
    annotate(ax, rows[-1][0], rows[-1][1], "Blue Scuti 40.3M", dx=-4, dy=6, ha="right")


def dk(ax):
    rows = load("donkey-kong-score.csv", "score")
    base_axes(
        ax,
        "Donkey Kong arcade high score",
        "world record score, 1982–2026 · filled = verified row, open = approximate/disputed",
    )
    draw(ax, rows, "#4a3aa7")
    ax.set_ylim(830000, 1330000)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e6:.2f}M"))
    annotate(ax, rows[0][0], rows[0][1], "Mitchell 874,300\n(18-year reign)", dx=12, dy=4, ha="left")
    annotate(ax, dt.date(2016, 1, 1), 1272800, "Lakeman 1,272,800\nstanding since 2021", dx=0, dy=6, ha="right")


PANELS = [
    ("mockup-smb1.png", smb1),
    ("mockup-ssdf.png", ssdf),
    ("mockup-tetris.png", tetris),
    ("mockup-donkey-kong.png", dk),
]


def main():
    for fname, fn in PANELS:
        fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=150)
        fn(ax)
        fig.tight_layout()
        fig.savefig(HERE / fname, facecolor="white")
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 7.6), dpi=150)
    for (_, fn), ax in zip(PANELS, axes.flat):
        fn(ax)
    fig.suptitle(
        "Draft mock-ups: game record time series (hand-transcribed, approximate rows open-circled)",
        x=0.01, ha="left", fontsize=12, fontweight="bold", color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(HERE / "mockup-overview.png", facecolor="white")
    plt.close(fig)
    print("wrote", len(PANELS) + 1, "figures")


if __name__ == "__main__":
    main()
