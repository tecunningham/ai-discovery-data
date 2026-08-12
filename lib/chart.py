"""One visual language for every figure in the repository.

Colours, the shaded agent era, the axis styling and the save path all live here
so every chart stays comparable by eye. A problem folder draws its own series and
calls save(); it should not restate a colour or re-decide where 2026 starts.

    from lib import chart

    fig, ax = chart.new_chart("Title", "subtitle")
    ...
    chart.save(fig, HERE / "discovery-x.png", "what it shows", [url], __file__)
"""

from __future__ import annotations

import platform
import zlib
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import ft2font
from matplotlib.lines import Line2D

from lib.renderer import assert_canonical_renderer

ROOT = Path(__file__).resolve().parents[1]

AI = "#c1442f"
# Affiliation-only credits: the same family as AI, visibly weaker evidence.
# Shared here so the PNGs and the interactive pages use one soft red.
AI_SOFT = "#e09a8c"
HUMAN = "#2f6cc1"
FUZZ = "#c98a00"
VENDOR = "#777777"
NEUTRAL = "#aaaaaa"
# For a series with no authorship field at all, which is a different thing from
# one whose finders are recorded and happen to be human. Blue would claim more
# than the data says: nobody counted who wrote these artifacts.
UNATTRIBUTED = "#37474f"

# Severity is ordered, not categorical, so it takes one hue in even lightness
# steps rather than four separate colours: the reader should see the ordering in
# the ink without consulting the legend. The steps are spaced so the closest
# adjacent pair stays about 16 apart in OKLab (×100) under normal, protanopic
# and deuteranopic vision, and the lightest clears 2:1 against white. The hue is
# deliberately not the AI red or the fuzzer amber those charts already spend on
# identity, so a severity bar cannot be misread as a finder band.
SEVERITY_RAMP = ["#87afc1", "#547d8f", "#234f61", "#002435"]

# The highlighted period is the same everywhere. Annual bar charts start it at
# 2025.5, the left edge of the 2026 bar on a year-centred categorical axis.
ERA_START = 2026.0
ANNUAL_ERA_START = 2025.5
# A committed snapshot date keeps PNG bytes stable. tools/check.py rejects data
# newer than this date, so a refetch cannot silently leave standing-record lines
# ending before their newest observation.
AS_OF_DATE = date(2026, 8, 10)
NOW = AS_OF_DATE.year + (AS_OF_DATE.timetuple().tm_yday - 1) / 365.25


def stable_jitter(key: str, spread: float = 0.035) -> float:
    """Deterministic cosmetic offset for overlapping points.

    Python's hash() is seeded per process, so using it made identical data
    produce a different PNG on every run.
    """
    return (zlib.crc32(key.encode()) % 7 - 3) * spread



def year_fraction(value: str) -> float:
    parts = [int(part) for part in value.split("-")]
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return parts[0] + (parts[1] - 0.5) / 12
    day = date(*parts[:3])
    return day.year + (day.timetuple().tm_yday - 1) / 365.25



def new_chart(title: str, subtitle: str, figsize: tuple[float, float] = (8.4, 5.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(title, x=0.09, y=0.98, ha="left", fontsize=14, fontweight="bold")
    ax.set_title(subtitle, loc="left", fontsize=9.2, color="#444444", pad=12)
    return fig, ax



def shade_era(ax, right: float, annual: bool = False) -> None:
    start = ANNUAL_ERA_START if annual else ERA_START
    if right <= start:
        return
    ax.axvspan(start, right, color=AI, alpha=0.055, zorder=0)
    ax.text(
        right - max((right - start) * 0.025, 0.025),
        0.975,
        "Jan 2026 onward",
        transform=ax.get_xaxis_transform(),
        fontsize=8,
        color=AI,
        va="top",
        ha="right",
    )



def style(ax, ylabel: str, xlabel: str = "Year") -> None:
    ax.set_xlabel(xlabel, fontsize=9.5)
    ax.set_ylabel(ylabel, fontsize=9.5)
    ax.grid(color="#d5d5d5", linewidth=0.7, alpha=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5, color="#777777")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#777777")



def source_note(fig, text: str) -> None:
    fig.text(0.09, 0.018, text, fontsize=7.2, color="#777777", ha="left")


def save(fig, out_path, description: str, sources: list[str], built_by: str,
         adjust: dict[str, float] | None = None) -> None:
    """Write the figure beside the data it came from.

    built_by is the calling script's __file__; it is recorded in the PNG so a
    reader who finds the image alone can get back to the code that drew it.

    The margins are set here rather than by the caller so every figure in the
    collection frames its plot identically. A multi-panel figure that needs room
    for long tick labels passes ``adjust`` to override them; setting them before
    calling save would not work, since this is the last word on layout.
    """
    assert_canonical_renderer(
        matplotlib_version=matplotlib.__version__,
        freetype_version=ft2font.__freetype_version__,
    )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(**{"left": 0.09, "right": 0.97, "top": 0.84,
                           "bottom": 0.15, **(adjust or {})})
    fig.savefig(
        out_path,
        dpi=180,
        metadata={
            "Title": description.split(".")[0],
            "Description": description,
            "Source": " | ".join(sources),
            "Software": (
                f"Python {'.'.join(platform.python_version_tuple()[:2])}; "
                f"matplotlib {matplotlib.__version__}; "
                f"FreeType {ft2font.__freetype_version__}; "
                f"{Path(built_by).resolve().relative_to(ROOT)}"
            ),
        },
    )
    plt.close(fig)
    print(f"wrote {out_path.name}")



def common_legend(*, fuzz: bool = False, vendor: bool = False, pending: bool = False):
    handles = [
        Line2D([], [], marker="o", linestyle="", color=HUMAN, label="human or uncredited"),
        Line2D([], [], marker="o", linestyle="", color=AI, label="AI-credited"),
    ]
    if fuzz:
        handles.append(Line2D([], [], marker="o", linestyle="", color=FUZZ, label="fuzzer"))
    if vendor:
        handles.append(Line2D([], [], marker="o", linestyle="", color=VENDOR, label="vendor-run"))
    if pending:
        handles.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                markerfacecolor="none",
                markeredgecolor="#555555",
                label="pending or uncertain",
            )
        )
    return handles



def record_marker(ax, x: float, y: float, row: dict[str, str], size: float = 55) -> None:
    colour = AI if row["agent"].startswith("ai_") else HUMAN
    uncertain = row.get("date_certain") == "no"
    ax.scatter(
        [x],
        [y],
        s=size,
        facecolor="none" if uncertain else colour,
        edgecolor=colour,
        linewidth=1.5 if uncertain else 0.7,
        zorder=5,
    )
