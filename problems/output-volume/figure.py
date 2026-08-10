#!/usr/bin/env python3
"""Draw output-volume.png from this folder's five volume series.

Run: python3 problems/output-volume/figure.py

Six panels: the five series and a key. The panels share one format — years on
x, a volume on y, January 2026 onward shaded — so the five indicators can be
read against each other and against the discovery series in the other folders.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from lib.chart import AI, ANNUAL_ERA_START, ERA_START  # noqa: E402
from lib.table import read_csv  # noqa: E402

INK = "#37474f"
ERA_LABEL = "2026 onward"


def frac_month(month: str) -> float:
    year, mo = month.split("-")[:2]
    return int(year) + (int(mo) - 0.5) / 12


def era(ax, right: float) -> None:
    ax.axvspan(ERA_START, right, color=AI, alpha=0.06, zorder=0)
    ax.text(ERA_START + 0.06, 0.975, ERA_LABEL,
            transform=ax.get_xaxis_transform(),
            fontsize=7.4, color=AI, va="top")


def dress(ax, title: str, ylab: str, source: str, howto: str) -> None:
    ax.set_title(title, fontsize=10.2, loc="left", pad=32)
    ax.text(0, 1.072, source, transform=ax.transAxes, fontsize=7.2,
            color="#8a8a8a", va="bottom", style="italic")
    ax.text(0, 1.016, howto, transform=ax.transAxes, fontsize=7.5,
            color="#444", va="bottom")
    ax.set_xlabel("Year", fontsize=9)
    ax.set_ylabel(ylab, fontsize=9)
    ax.grid(alpha=0.20)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(labelsize=8.2)


def main() -> None:
    fig, ((o1, o2, o3), (o4, o5, o6)) = plt.subplots(2, 3, figsize=(15.6, 8.6))

    # (1) arXiv monthly submissions.
    rows = read_csv(HERE / "arxiv-monthly.csv")
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
    rows = read_csv(HERE / "github-innovationgraph-global.csv")

    def frac_q(quarter):
        year, qq = quarter.split("-Q")
        return int(year) + (int(qq) - 0.5) / 4

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
    rows = read_csv(HERE / "stackoverflow-questions-monthly.csv")
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
    rows = read_csv(HERE / "crossref-dois-by-year.csv")
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
    o4.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    o4.set_xlim(2009, 2028.2)
    o4.set_ylim(0, max(vs) * 1.22)
    o4.axvspan(ANNUAL_ERA_START, 2028.2, color=AI, alpha=0.06,
               zorder=0)
    o4.text(2025.58, 0.975, ERA_LABEL,
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
    rows = read_csv(HERE / "pypi-projects-over-time.csv")

    def frac_d(day):
        parts = (day.split("-") + ["1", "1"])[:3]
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
    # Saved directly rather than through lib.chart.save(): this figure has to
    # stay byte-identical to the composite it was extracted from, and save()
    # imposes its own dpi and margins.
    fig.savefig(HERE / "output-volume.png", dpi=155)
    plt.close(fig)
    print("wrote output-volume.png")


if __name__ == "__main__":
    main()
