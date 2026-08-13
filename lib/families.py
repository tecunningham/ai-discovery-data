"""Chart shapes drawn by more than one problem.

Eight vulnerability series share the periodic (quarterly or monthly) stacked
bars and four of them the severity count heatmap; six problem-list ledgers
share one dated-resolutions chart; one Hutter corpus and one AlphaEvolve
ladder folder use the same standing-record plot. Those shapes live here,
parameterised by the CSV path, so a problem folder holding a series of a
known kind is a short call rather than a copy of 60 lines of matplotlib.

A shape belongs here only once a second problem needs it. One-off charts stay in
the folder that owns them.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from lib.chart import (
    AI,
    HUMAN,
    SEVERITY_RAMP,
    NEUTRAL,
    NOW,
    UNATTRIBUTED,
    common_legend,
    new_chart,
    period_bounds,
    record_marker,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv



def periodic_stacked(
    out_path: Path,
    *,
    title: str,
    subtitle: str,
    ylabel: str,
    periods: list[str],
    stacks: list[tuple[str, str, list[int]]],
    source_label: str,
    source_url: str,
    built_by: str,
    partial_last: str = "",
    note: str = "",
) -> None:
    """Stacked bars at a series' native cadence — quarters or months.

    The annual bar shapes hid the cadence the granular CSVs actually carry, and
    a within-year surge is exactly the thing an agent-era reading needs to see.
    ``periods`` are ascending labels ("2016-Q1" or "2016-01" or "2016"); each
    stack is (label, colour, values per period), drawn bottom-up in the order
    given. A legend entry appears only for stacks with any ink.

    ``partial_last`` marks the final period as incomplete: it gets the same
    outline-and-annotation treatment the annual charts gave a part year, because
    a short final bar otherwise reads as a collapse.
    """
    bounds = [period_bounds(label) for label in periods]
    centers = [(start + end) / 2 for start, end in bounds]
    width = (bounds[0][1] - bounds[0][0]) * 0.86
    fig, ax = new_chart(title, subtitle)
    bottoms = [0] * len(periods)
    for label, colour, values in stacks:
        if any(values):
            ax.bar(centers, values, bottom=bottoms, width=width, color=colour,
                   label=label, zorder=3)
        bottoms = [b + v for b, v in zip(bottoms, values)]
    if partial_last:
        ax.bar(centers[-1], bottoms[-1], width=width, facecolor="none",
               edgecolor="#444444", linewidth=1.1, zorder=4)
        ax.annotate(
            partial_last,
            (centers[-1], bottoms[-1]),
            xytext=(-4, 7),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color="#555555",
        )
    left = bounds[0][0]
    right = max(bounds[-1][1] + (bounds[-1][1] - left) * 0.01, NOW + 0.15)
    ax.set_xlim(left - (right - left) * 0.012, right)
    ax.set_ylim(0, max(bottoms) * 1.24)
    shade_era(ax, right)
    style(ax, ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Two columns at upper left: a full-width legend row runs into the era
        # label the shaded band writes at the top right.
        ax.legend(handles=handles, labels=labels, frameon=False, fontsize=8,
                  ncol=2, loc="upper left")
    if note:
        ax.text(0.02, 0.78 if handles else 0.92, note, transform=ax.transAxes,
                fontsize=8.8, color="#333333", va="top", linespacing=1.5)
    source_note(fig, f"Source: {source_label}.")
    save(
        fig,
        out_path,
        f"{title}. {subtitle}.",
        [source_url],
        built_by,
    )



def severity_heatmap(
    out_path: Path,
    title: str,
    subtitle: str,
    *,
    years: list[str],
    panels: list[tuple[str, dict[str, dict[str, int]]]],
    severities: list[str],
    source_label: str,
    source_url: str,
    built_by: str,
    note: str = "",
) -> None:
    """Counts by severity × year, one annotated grid per finder-origin cohort.

    Every cell prints its count, so the chart can be read as a table: the
    number of disclosures at each severity, in each year, from each origin.
    Shading is normalized within each panel — the cohorts differ by orders of
    magnitude, and one shared scale would blank every panel but the largest.
    The severity ordering runs most severe at the top, and the shading reuses
    the severity hue so this cannot be misread as a finder-band chart.
    """
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list(
        "severity_counts", ["#ffffff", SEVERITY_RAMP[-1]]
    )
    # A cohort with nothing in it would render as a grid of zeros; its absence
    # from the chart is the statement, so it is dropped rather than drawn.
    panels = [
        (label, by_year)
        for label, by_year in panels
        if any(count for years in by_year.values() for count in years.values())
    ]
    rows = list(reversed(severities))  # most severe first, top row down
    height = 1.0 + 0.34 * len(rows) * len(panels) + 0.42 * len(panels)
    fig, axes = plt.subplots(
        len(panels),
        1,
        figsize=(8.4, max(4.4, height)),
        squeeze=False,
    )
    fig.suptitle(title, x=0.09, y=0.99, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.09, 0.99 - 0.42 / max(4.4, height), subtitle, fontsize=9.2,
             color="#444444", ha="left", va="top")
    for ax, (label, by_year) in zip(axes[:, 0], panels):
        grid = [[by_year.get(year, {}).get(severity, 0) for year in years]
                for severity in rows]
        peak = max((value for row in grid for value in row), default=0) or 1
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=peak, aspect="auto",
                  interpolation="nearest")
        for r, row in enumerate(grid):
            for c, value in enumerate(row):
                dark = value > 0.55 * peak
                ax.text(c, r, str(value),
                        ha="center", va="center", fontsize=7.6,
                        color="white" if dark
                        else ("#333333" if value else "#b5b5b5"))
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(rows, fontsize=8)
        ax.set_xticks(range(len(years)))
        if ax is axes[-1, 0]:
            ax.set_xticklabels(years, fontsize=7.6,
                               rotation=45 if len(years) > 12 else 0,
                               ha="right" if len(years) > 12 else "center")
        else:
            ax.set_xticklabels([])
        ax.set_title(label, loc="left", fontsize=9.2, color="#444444", pad=6)
        ax.tick_params(length=0, colors="#777777")
        for spine in ax.spines.values():
            spine.set_visible(False)
        if years and years[-1] == "2026":
            # The era marker on a categorical grid: box the partial 2026
            # column rather than shading a year span that has no x-axis.
            ax.add_patch(plt.Rectangle(
                (len(years) - 1.5, -0.5), 1, len(rows),
                facecolor="none", edgecolor=AI, linewidth=1.2, zorder=4,
            ))
    caption = "Counts, not shares; shading is scaled within each panel."
    if note:
        caption = f"{note} {caption}"
    source_note(fig, f"Source: {source_label}. {caption}")
    save(
        fig,
        out_path,
        f"{title}. {subtitle}.",
        [source_url],
        built_by,
        adjust={"left": 0.115, "right": 0.97,
                "top": 1 - 1.05 / max(4.4, height),
                "bottom": 0.9 / max(4.4, height), "hspace": 0.5},
    )



def problem_list_chart(
    csv_path: Path,
    out_path: Path,
    built_by: str,
    ai_problem: str | None = None,
) -> None:
    """Show a list's dated resolution events by year.

    The event bars retain the chronology needed to discuss acceleration without
    making a numerical-bound staircase and a problem-status ledger look like the
    same instrument. The present-day status split — open, contested, undated
    resolutions — lives in the CSV and the document's prose; a one-line note
    here says how much of the list the dated events account for.
    """
    rows = read_csv(csv_path)
    name = rows[0]["list_name"]
    start = int(rows[0]["list_year"])
    total = len(rows)
    resolved = [
        (int(row["resolved_year"]), row)
        for row in rows
        if row["status"] == "resolved" and row["resolved_year"]
    ]
    resolved.sort(key=lambda item: (item[0], item[1]["problem_id"]))
    open_count = sum(row["status"] == "open" for row in rows)

    fig, timeline_ax = new_chart(
        f"{name}: dated resolutions",
        "Resolution events by year (event count, not the value of a bound)",
    )

    human_by_year: dict[int, int] = defaultdict(int)
    ai_by_year: dict[int, int] = defaultdict(int)
    ai_row: tuple[int, dict[str, str]] | None = None
    for year, row in resolved:
        if row["problem_id"] == ai_problem:
            ai_by_year[year] += 1
            ai_row = (year, row)
        else:
            human_by_year[year] += 1
    event_years = sorted(set(human_by_year) | set(ai_by_year))
    bar_width = max(0.65, min(1.4, (NOW - start) * 0.018))
    if resolved:
        human_values = [human_by_year[year] for year in event_years]
        ai_values = [ai_by_year[year] for year in event_years]
        timeline_ax.bar(
            event_years,
            human_values,
            width=bar_width,
            color=HUMAN,
            zorder=3,
        )
        timeline_ax.bar(
            event_years,
            ai_values,
            bottom=human_values,
            width=bar_width,
            color=AI,
            zorder=4,
        )
        for year, human_value, ai_value in zip(event_years, human_values, ai_values):
            timeline_ax.text(
                year,
                human_value + ai_value + 0.08,
                str(human_value + ai_value),
                ha="center",
                va="bottom",
                fontsize=7.5,
                color="#555555",
            )
        if ai_row:
            year, row = ai_row
            timeline_ax.annotate(
                f"{row['short_name']}\nformal checks complete; peer review pending",
                (year, human_by_year[year] + ai_by_year[year]),
                xytext=(-10, 26),
                textcoords="offset points",
                ha="right",
                fontsize=8,
                color=AI,
                arrowprops={"arrowstyle": "-", "color": AI, "linewidth": 0.8},
            )
        timeline_ax.set_ylim(
            0,
            max(human_by_year[year] + ai_by_year[year] for year in event_years)
            + 1.15,
        )
    else:
        timeline_ax.text(
            0.5,
            0.52,
            "No row has a dated resolution",
            transform=timeline_ax.transAxes,
            ha="center",
            va="center",
            fontsize=8.5,
            color=HUMAN,
        )
        timeline_ax.set_ylim(0, 1)

    right = NOW + max((NOW - start) * 0.035, 1.2)
    left_year = min([start, *event_years])
    timeline_ax.set_xlim(
        left_year - max((NOW - left_year) * 0.04, 1),
        right,
    )
    shade_era(timeline_ax, right)
    style(timeline_ax, "Resolutions in year")
    timeline_ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    timeline_ax.text(
        0.02,
        0.96,
        f"{len(resolved)} of {total} scored rows have dated resolutions; "
        f"{open_count} are open today",
        transform=timeline_ax.transAxes,
        fontsize=8.5,
        color="#555555",
        va="top",
    )
    source_note(
        fig,
        f"Source: {rows[0]['source']}. Years are resolution landmarks, "
        "not effort-adjusted discovery rates.",
    )
    save(
        fig,
        out_path,
        f"{name}: dated resolution events per year.",
        sorted({row["source"] for row in rows}),
        built_by,
    )



def alphaevolve_value_chart(
    csv_path: Path,
    problems: list[str],
    out_path: Path,
    title: str,
    subtitle: str,
    ylabel: str,
    annotations: dict[tuple[str, str], str] | None = None,
    built_by: str = "",
) -> None:
    rows = [
        row
        for row in read_csv(csv_path)
        if row["problem"] in problems and row["value"] and row.get("is_record", "yes") == "yes"
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["problem"]].append(row)
    fig, ax = new_chart(title, subtitle)
    line_styles = ["-", "--", ":"]
    for line_index, problem in enumerate(problems):
        local = grouped[problem]
        local.sort(key=lambda row: (int(row["year"]), int(row["step"])))
        xs = [int(row["year"]) for row in local]
        ys = [float(row["value"]) for row in local]
        ax.plot(
            xs + [NOW],
            ys + [ys[-1]],
            drawstyle="steps-post",
            color=NEUTRAL,
            linestyle=line_styles[line_index % len(line_styles)],
            linewidth=1.6,
            label=local[0]["quantity"],
            zorder=2,
        )
        for x, y, row in zip(xs, ys, local):
            record_marker(ax, x, y, row)
            label = (annotations or {}).get((problem, row["step"]))
            if label:
                ax.annotate(
                    label,
                    (x, y),
                    xytext=(5, 7),
                    textcoords="offset points",
                    fontsize=7.5,
                    color=AI if row["agent"].startswith("ai_") else HUMAN,
                )
    right = 2030
    ax.set_xlim(min(int(row["year"]) for row in rows) - 5, right)
    shade_era(ax, right)
    style(ax, ylabel)
    ax.legend(handles=common_legend(pending=True) + [
        Line2D([], [], color=NEUTRAL, linestyle=line_styles[i], label=grouped[p][0]["quantity"])
        for i, p in enumerate(problems)
    ], frameon=False, fontsize=7.5, ncol=2)
    source_note(
        fig,
        f"Source: {Path(csv_path).name}, transcribed from the paper and cited follow-ons. "
        "Open markers have uncertain dates.",
    )
    save(
        fig,
        out_path,
        f"{title}. Standing records over time with AI and human authorship.",
        sorted({row["ref"] for row in rows if row["ref"]}),
        built_by,
    )



def compression_chart(
    csv_path: Path,
    series: str,
    out_path: Path,
    title: str,
    subtitle: str,
    built_by: str,
) -> None:
    all_rows = read_csv(csv_path)
    rows = [row for row in all_rows if row["series"] == series]
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [int(row["total_bytes"]) / 1e6 for row in rows]
    awarded = [i for i, row in enumerate(rows) if row["award"] != "pending"]
    fig, ax = new_chart(title, subtitle)
    ax.plot(
        [xs[i] for i in awarded] + [NOW],
        [ys[i] for i in awarded] + [ys[awarded[-1]]],
        drawstyle="steps-post",
        color=HUMAN,
        linewidth=2,
        label="Hutter Prize (CPU-capped)",
    )
    ax.scatter([xs[i] for i in awarded], [ys[i] for i in awarded], color=HUMAN, s=52, edgecolor="white", linewidth=0.7, zorder=4)
    for i, row in enumerate(rows):
        if row["award"] != "pending":
            continue
        ax.scatter([xs[i]], [ys[i]], s=60, facecolor="none", edgecolor=HUMAN, linewidth=1.6, zorder=5)
        ax.annotate(
            f"{row['program']}, pending",
            (xs[i], ys[i]),
            xytext=(-5, 8),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color=HUMAN,
        )
    if series == "hutter_enwik9":
        ltcb = [row for row in all_rows if row["series"] == "ltcb_enwik9"]
        if ltcb:
            lxs = [year_fraction(row["date"]) for row in ltcb]
            lys = [int(row["total_bytes"]) / 1e6 for row in ltcb]
            ax.plot(
                lxs + [NOW],
                lys + [lys[-1]],
                drawstyle="steps-post",
                color=NEUTRAL,
                linewidth=1.5,
                linestyle="--",
                label="uncapped leaderboard (LTCB)",
            )
            ax.text(
                0.98,
                0.28,
                f"uncapped frontier flat since Oct 2023\nat {lys[-1]:.1f} MB",
                transform=ax.transAxes,
                fontsize=8,
                color="#666666",
                ha="right",
            )
    right = NOW + 0.5
    ax.set_xlim(min(xs) - 0.7, right)
    shade_era(ax, right)
    style(ax, "Total size, MB (program + archive)")
    handles = common_legend(pending=True)
    if series == "hutter_enwik9":
        handles.append(Line2D([], [], color=NEUTRAL, linestyle="--", label="uncapped (LTCB)"))
    ax.legend(handles=handles, frameon=False, fontsize=8)
    ax.text(0.02, 0.12, "All awarded records are human; lower is better.", transform=ax.transAxes, fontsize=8.5)
    source_note(
        fig,
        "Source: prize.hutter1.net and mattmahoney.net/dc/text.html, "
        f"vendored as {Path(csv_path).name}.",
    )
    save(
        fig,
        out_path,
        f"{title}. Hutter Prize compression records with pending entries open.",
        ["https://prize.hutter1.net/", "http://mattmahoney.net/dc/text.html"],
        built_by,
    )



def volume_series(
    out_path: Path,
    *,
    xs: list[float],
    ys: list[float],
    title: str,
    subtitle: str,
    ylabel: str,
    reading: str,
    source_label: str,
    source_url: str,
    built_by: str,
    bars: bool = False,
    markers: bool = False,
    partial_last: str = "",
    rules: tuple[tuple[float, str], ...] = (),
    right_pad: float = 1.2,
) -> None:
    """One output-volume series: years on x, a count on y, era shaded.

    The three volume series are three different artifacts counted by three
    organizations, and the only thing that makes them comparable is being drawn
    the same way. They are the collection's contrast case — volume against
    discovery — so a difference in shape between one of these and a record series
    has to be a difference in the data, not in how it was plotted.

    Drawn in slate rather than blue: these counts carry no authorship field, so
    the finder vocabulary the other charts use does not apply.

    `reading` is the sentence of numbers on the axes. Callers compute it from
    their own CSV rather than passing a literal, so it cannot go stale when the
    series is refetched.
    """
    fig, ax = new_chart(title, subtitle)
    if bars:
        ax.bar(xs, ys, color=UNATTRIBUTED, width=0.72, zorder=3)
    else:
        ax.plot(xs, ys, color=UNATTRIBUTED, linewidth=1.7, zorder=3,
                marker="o" if markers else None, markersize=3.2)
    if partial_last:
        if bars:
            ax.bar([xs[-1]], [ys[-1]], width=0.72, facecolor="none",
                   edgecolor="#444444", linewidth=1.3, zorder=4)
        else:
            ax.scatter([xs[-1]], [ys[-1]], s=46, facecolor="white",
                       edgecolor=UNATTRIBUTED, linewidth=1.4, zorder=5)
        # A part bar is short, so its label goes centred above it; offsetting it
        # sideways lands the text on the taller neighbour. Beside a line the
        # series itself occupies that space, so the label goes below the marker.
        ax.annotate(partial_last, (xs[-1], ys[-1]),
                    xytext=(0, 8) if bars else (-7, -16),
                    textcoords="offset points",
                    ha="center" if bars else "right", fontsize=8,
                    color="#555555",
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.75,
                              pad=1))
    for position, label in rules:
        ax.axvline(position, color="#777777", linestyle=":", linewidth=1.1, zorder=2)
        ax.text(position - 0.08, 0.30, label, transform=ax.get_xaxis_transform(),
                fontsize=8, color="#555555", ha="right", linespacing=1.35)
    right = max(xs) + right_pad
    ax.set_xlim(min(xs) - right_pad * 0.35, right)
    ax.set_ylim(0, max(ys) * 1.22)
    shade_era(ax, right, annual=bars)
    style(ax, ylabel)
    if bars:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.text(0.02, 0.90, reading, transform=ax.transAxes, fontsize=8.8,
            color="#333333", va="top", linespacing=1.5)
    # Kept short deliberately: the note is one line at the foot of the figure and
    # a longer one runs off the canvas rather than wrapping.
    source_note(fig, f"Source: {source_label}. No authorship field, so no AI "
                     "share can be read off it.")
    save(fig, out_path, f"{title}. {subtitle}", [source_url], built_by)
