"""Chart shapes drawn by more than one problem.

Five vulnerability series share annual bar shapes; six problem-list ledgers
share one dated-resolutions chart; one Hutter corpus and one
AlphaEvolve ladder folder use the same standing-record plot. Those shapes live
here, parameterised by the CSV path, so a problem folder holding a series of a
known kind is a short call rather than a copy of 60 lines of matplotlib.

A shape belongs here only once a second problem needs it. One-off charts stay in
the folder that owns them.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

from lib.chart import (
    AI,
    HUMAN,
    FUZZ,
    SEVERITY_RAMP,
    NEUTRAL,
    NOW,
    UNATTRIBUTED,
    common_legend,
    new_chart,
    record_marker,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv



def cyber_stacked(
    csv_path: Path,
    out_path: Path,
    title: str,
    subtitle: str,
    source_label: str,
    source_url: str,
    built_by: str,
    *,
    ylabel: str = "Vulnerabilities disclosed that year",
    unit_label: str = "disclosures",
) -> None:
    rows = read_csv(csv_path)
    years = [int(row["year"]) for row in rows]
    other = [int(row["other_attributed"]) for row in rows]
    fuzz = [int(row.get("fuzz_attributed") or 0) for row in rows]
    ai = [int(row["ai_attributed"]) for row in rows]
    totals = [int(row["total"]) for row in rows]
    fig, ax = new_chart(title, subtitle)
    ax.bar(years, other, color=HUMAN, width=0.76, label="human or uncredited", zorder=3)
    if any(fuzz):
        ax.bar(years, fuzz, bottom=other, color=FUZZ, width=0.76, label="fuzzer", zorder=3)
    bottoms = [a + b for a, b in zip(other, fuzz)]
    ax.bar(years, ai, bottom=bottoms, color=AI, width=0.76, label="AI-credited", zorder=3)
    partial = [i for i, row in enumerate(rows) if row.get("partial_year") == "yes"]
    for index in partial:
        ax.bar(
            years[index],
            totals[index],
            width=0.76,
            facecolor="none",
            edgecolor="#444444",
            linewidth=1.3,
            zorder=4,
        )
        ax.annotate(
            "partial year",
            (years[index], totals[index]),
            xytext=(-4, 7),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color="#555555",
        )
    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(totals) * 1.23)
    shade_era(ax, right, annual=True)
    style(ax, ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.legend(handles=common_legend(fuzz=any(fuzz)), frameon=False, fontsize=8, ncol=3)
    if partial:
        latest = rows[partial[-1]]
        through = (
            f" through {latest['data_through']}"
            if latest.get("data_through") else ""
        )
        ax.text(
            0.02,
            0.9,
            f"{latest['total']} {unit_label} in partial {latest['year']}{through}\n"
            f"{latest['ai_attributed']} explicitly AI-credited",
            transform=ax.transAxes,
            fontsize=9,
            color="#333333",
            va="top",
        )
    source_note(fig, f"Source: {source_label}. Finder credits are textual markers, not audited causation.")
    save(
        fig,
        out_path,
        f"{title}. Annual finder-attributed {unit_label}; "
        + (f"{rows[partial[-1]]['year']} is partial." if partial else "complete years."),
        [source_url],
        built_by,
    )



def cyber_simple_bars(
    csv_path: Path,
    value_column: str,
    out_path: Path,
    title: str,
    subtitle: str,
    ylabel: str,
    colour: str,
    source_label: str,
    source_url: str,
    built_by: str,
) -> None:
    rows = read_csv(csv_path)
    years = [int(row["year"]) for row in rows]
    values = [int(row[value_column]) for row in rows]
    fig, ax = new_chart(title, subtitle)
    ax.bar(years, values, color=colour, width=0.76, zorder=3)
    for i, row in enumerate(rows):
        if row.get("partial_year") != "yes":
            continue
        ax.bar(
            years[i],
            values[i],
            width=0.76,
            facecolor="none",
            edgecolor="#444444",
            linewidth=1.3,
            zorder=4,
        )
        ax.annotate(
            f"partial year\nthrough {row.get('data_through') or 'latest snapshot'}",
            (years[i], values[i]),
            xytext=(-5, 7),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color="#555555",
        )
    right = max(years) + 1.2
    ax.set_xlim(min(years) - 1, right)
    ax.set_ylim(0, max(values) * 1.25)
    shade_era(ax, right, annual=True)
    style(ax, ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.legend(
        handles=[
            Patch(facecolor=colour, label="annual count"),
            Patch(facecolor="none", edgecolor="#444444", label="partial calendar year"),
        ],
        frameon=False,
        fontsize=8,
    )
    source_note(fig, f"Source: {source_label}.")
    save(fig, out_path, f"{title}. Annual count; 2026 is partial.", [source_url], built_by)



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


def severity_panels(
    out_path: Path,
    title: str,
    subtitle: str,
    *,
    years: list[str],
    by_year: dict[str, dict[str, int]],
    cohorts: list[tuple[str, dict[str, int]]],
    severities: list[str],
    source_label: str,
    source_url: str,
    built_by: str,
    year_caption: str,
    cohort_caption: str,
) -> None:
    """Two views of one severity field: drift over time, and mix by cohort.

    Both panels are drawn as shares rather than counts. A severity chart asks
    what a year's disclosures were made of, and counts answer a different
    question the folder's main figure already answers; plotting shares also lets
    a year with nine disclosures sit beside one with thirty-nine without the
    small year vanishing.

    The top panel is the drift — whether a codebase's findings are getting
    shallower — and the bottom panel is the comparison the drift is usually
    invoked for, one bar per cohort of finders. Keeping them on one figure is
    the point: the cohort difference means little without the trend it sits in,
    since a shallow AI cohort inside a series that was already shallowing is a
    weaker claim than the same gap in a flat series.

    Callers pass only the years their upstream actually rated. A project that
    scored nothing before some date has an absence of data there, not a run of
    low-severity findings, and the honest rendering of that is to start the panel
    where the ratings start and say so in the document.
    """
    ramp = dict(zip(severities, SEVERITY_RAMP))
    bands = list(severities)

    fig, (year_ax, cohort_ax) = plt.subplots(
        2, 1, figsize=(8.4, 6.4), gridspec_kw={"height_ratios": (2.05, 1.0), "hspace": 0.42}
    )
    fig.suptitle(title, x=0.09, y=0.985, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.09, 0.930, subtitle, fontsize=9.2, color="#444444", ha="left", va="top")

    positions = list(range(len(years)))
    bottoms = [0.0] * len(years)
    for band in bands:
        shares = []
        for year in years:
            counts = by_year[year]
            total = sum(counts.values()) or 1
            shares.append(100 * counts.get(band, 0) / total)
        year_ax.bar(positions, shares, bottom=bottoms, width=0.74, color=ramp[band],
                    label=band, zorder=3, linewidth=0.8, edgecolor="white")
        bottoms = [b + s for b, s in zip(bottoms, shares)]
    year_ax.set_xticks(positions)
    year_ax.set_xticklabels(years)
    year_ax.set_xlim(-0.7, len(years) - 0.3)
    year_ax.set_ylim(0, 100)
    year_ax.set_yticks([0, 25, 50, 75, 100])
    year_ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    if years and years[-1] == "2026":
        # The era band is placed by bar index: this axis is categorical, so the
        # year-valued constants the other charts shade with do not apply.
        year_ax.axvspan(len(years) - 1.5, len(years) - 0.3, color=AI, alpha=0.055, zorder=0)
    style(year_ax, "Share of that year's disclosures")

    labels = [label for label, _ in cohorts]
    spots = list(range(len(cohorts)))[::-1]
    lefts = [0.0] * len(cohorts)
    for band in bands:
        widths = []
        for _, counts in cohorts:
            total = sum(counts.values()) or 1
            widths.append(100 * counts.get(band, 0) / total)
        cohort_ax.barh(spots, widths, left=lefts, height=0.52, color=ramp[band],
                       zorder=3, linewidth=0.8, edgecolor="white")
        for spot, width, left in zip(spots, widths, lefts):
            # Direct-label the segments with room for the text. The lightest step
            # sits below 3:1 on white, so the share it carries is written out
            # rather than left to the eye to estimate.
            if width >= 11:
                cohort_ax.text(left + width / 2, spot, f"{width:.0f}%", ha="center",
                               va="center", fontsize=8,
                               color="#22333a" if band == severities[0] else "white",
                               zorder=4)
        lefts = [left + width for left, width in zip(lefts, widths)]
    # The cohort names sit above their bars rather than in the margin. As tick
    # labels they would need a left margin wide enough for the longest of them,
    # which would push the year panel above off-centre for no reason.
    for spot, label in zip(spots, labels):
        cohort_ax.text(0.4, spot + 0.34, label, fontsize=8.5, color="#444444",
                       va="bottom", ha="left", zorder=4)
    cohort_ax.set_yticks(spots)
    cohort_ax.set_yticklabels([""] * len(spots))
    cohort_ax.tick_params(axis="y", length=0)
    cohort_ax.set_ylim(-0.5, len(cohorts) - 0.15)
    cohort_ax.set_xlim(0, 100)
    cohort_ax.set_xticks([0, 25, 50, 75, 100])
    cohort_ax.set_xticklabels(["0", "25", "50", "75", "100%"])
    style(cohort_ax, "", cohort_caption)
    cohort_ax.grid(axis="y", visible=False)

    handles = [Patch(facecolor=ramp[band], label=band) for band in bands]
    year_ax.legend(handles=handles, frameon=False, fontsize=8, ncol=len(bands),
                   loc="lower left", bbox_to_anchor=(0, 1.03))
    source_note(fig, f"Source: {source_label}. {year_caption}")
    save(fig, out_path, f"{title}. {subtitle}.", [source_url], built_by,
         adjust={"left": 0.095, "right": 0.97, "top": 0.83, "bottom": 0.115})
