"""One cumulative step-function view per series, all drawn the same way.

[CUMULATIVE.md](../CUMULATIVE.md) is a second index of the collection in which
every series is redrawn as a single step function of progress to date: a rising
cumulative count of events, a declining count of what remains when the series
has a known denominator, or the native value of a standing record. The four
shapes here are that page's whole vocabulary, and they are deliberately plainer
than the folder charts — one line, no attribution splits, no per-event
annotations — so that a difference between two panels on that page is a
difference in the data rather than in how it was plotted.

Drawn in slate (lib.chart.UNATTRIBUTED) because a cumulative total carries no
authorship; the folder charts keep the finder splits and the event colouring.
"""

from __future__ import annotations

import re
from pathlib import Path

from matplotlib.lines import Line2D

from lib.chart import (
    NOW,
    UNATTRIBUTED,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.table import read_csv

# Two ladders in one folder still get one panel on the cumulative page, so a
# second or third line reuses the same slate ink and varies only its dashing.
LINE_STYLES = ("-", "--", ":")

# label, xs (year fractions), ys — one step line on the shared panel.
Series = tuple[str, list[float], list[float]]


def _period_bounds(label: str) -> tuple[float, float]:
    """Start and end of a period label as year fractions.

    Accepts the three period vocabularies the vendored CSVs use: a year
    ("2000"), a quarter ("2020-Q1"), or a month ("1991-07"). The end matters
    more than the start: a cumulative total through a period is a fact that
    becomes true at the period's end, so that is where the step lands.
    """
    if re.fullmatch(r"\d{4}", label):
        year = int(label)
        return year, year + 1
    quarter = re.fullmatch(r"(\d{4})-Q([1-4])", label)
    if quarter:
        year, q = int(quarter.group(1)), int(quarter.group(2))
        return year + (q - 1) / 4, year + q / 4
    month = re.fullmatch(r"(\d{4})-(\d{2})", label)
    if month:
        year, m = int(month.group(1)), int(month.group(2))
        return year + (m - 1) / 12, year + m / 12
    raise ValueError(f"unrecognized period label: {label!r}")


def _draw(
    out_path: Path,
    *,
    title: str,
    subtitle: str,
    ylabel: str,
    series: list[Series],
    source_label: str,
    source_url: str,
    built_by: str,
    caption: str,
    ylog: bool = False,
    ylim: tuple[float, float] | None = None,
    note: str = "",
) -> None:
    """The one drawing everything on the cumulative page shares.

    A steps-post line holds each value until the next observation, which is the
    honest reading of every series here: a cumulative count is what has happened
    so far, a remaining count is what is left, a standing record stands until it
    is beaten. Each line extends flat to the chart snapshot date, so a series
    that stopped moving shows its flat stretch rather than ending early.
    """
    fig, ax = new_chart(title, subtitle)
    for index, (label, xs, ys) in enumerate(series):
        if xs[-1] < NOW:
            xs = xs + [NOW]
            ys = ys + [ys[-1]]
        ax.plot(xs, ys, drawstyle="steps-post", color=UNATTRIBUTED,
                linestyle=LINE_STYLES[index % len(LINE_STYLES)],
                linewidth=1.9, zorder=3)
    if len(series) > 1:
        ax.legend(handles=[
            Line2D([], [], color=UNATTRIBUTED,
                   linestyle=LINE_STYLES[i % len(LINE_STYLES)], label=label)
            for i, (label, _, _) in enumerate(series)
        ], frameon=False, fontsize=8)
    left = min(xs[0] for _, xs, _ in series)
    right = NOW + max((NOW - left) * 0.03, 0.5)
    ax.set_xlim(left - max((NOW - left) * 0.02, 0.3), right)
    if ylog:
        ax.set_yscale("log")
    elif ylim is not None:
        ax.set_ylim(*ylim)
    shade_era(ax, right)
    style(ax, ylabel)
    if note:
        ax.text(0.02, 0.94, note, transform=ax.transAxes, fontsize=8.5,
                color="#555555", va="top", linespacing=1.5)
    source_note(fig, f"Source: {source_label}.")
    save(fig, out_path, caption, [source_url], built_by)


def counts_chart(
    out_path: Path,
    *,
    title: str,
    ylabel: str,
    period_labels: list[str],
    counts: list[float],
    source_label: str,
    source_url: str,
    built_by: str,
    subtitle: str = "Cumulative count of events to date",
    note: str = "",
) -> None:
    """Cumulative events to date, rising from zero at the first period's start.

    Each step lands at its period's end, capped at the snapshot date for the
    final partial period: the total through 2026 is only known through the day
    the data stops.
    """
    running = 0.0
    xs = [_period_bounds(period_labels[0])[0]]
    ys = [0.0]
    for label, count in zip(period_labels, counts):
        running += count
        xs.append(min(_period_bounds(label)[1], NOW))
        ys.append(running)
    _draw(
        out_path,
        title=title,
        subtitle=subtitle,
        ylabel=ylabel,
        series=[("", xs, ys)],
        ylim=(0, running * 1.15),
        source_label=source_label,
        source_url=source_url,
        built_by=built_by,
        caption=f"{title}. Cumulative count over time.",
        note=note,
    )


def events_chart(
    out_path: Path,
    *,
    title: str,
    ylabel: str,
    dates: list[str],
    source_label: str,
    source_url: str,
    built_by: str,
    weights: list[float] | None = None,
    subtitle: str = "Cumulative count of events to date",
    note: str = "",
) -> None:
    """Cumulative dated events, stepping up at each event's own date.

    The counts_chart sibling is for periodic totals, which are only known at
    each period's end; an event dated to a day or a year steps the line on that
    date. Dates may be years, months or full ISO dates, and must be passed in
    ascending order so the line the reader sees is the order the CSV states.
    """
    weights = weights if weights is not None else [1.0] * len(dates)
    xs = [year_fraction(dates[0])]
    ys = [0.0]
    running = 0.0
    for date_label, weight in zip(dates, weights):
        running += weight
        xs.append(year_fraction(date_label))
        ys.append(running)
    _draw(
        out_path,
        title=title,
        subtitle=subtitle,
        ylabel=ylabel,
        series=[("", xs, ys)],
        ylim=(0, running * 1.15),
        source_label=source_label,
        source_url=source_url,
        built_by=built_by,
        caption=f"{title}. Cumulative count over time.",
        note=note,
    )


def remaining_chart(
    out_path: Path,
    *,
    title: str,
    subtitle: str,
    ylabel: str,
    xs: list[float],
    ys: list[float],
    source_label: str,
    source_url: str,
    built_by: str,
    note: str = "",
) -> None:
    """What remains of a known denominator, declining toward zero.

    The y-axis is pinned to zero so the distance still to travel is part of the
    picture: a list that has barely moved shows as a high flat line, not as a
    zoomed-in wiggle.
    """
    _draw(
        out_path,
        title=title,
        subtitle=subtitle,
        ylabel=ylabel,
        series=[("", xs, ys)],
        ylim=(0, max(ys) * 1.15),
        source_label=source_label,
        source_url=source_url,
        built_by=built_by,
        caption=f"{title}. Count remaining over time, toward zero.",
        note=note,
    )


def staircase_chart(
    out_path: Path,
    *,
    title: str,
    subtitle: str,
    ylabel: str,
    series: list[Series],
    source_label: str,
    source_url: str,
    built_by: str,
    ylog: bool = False,
    note: str = "",
) -> None:
    """A standing record's native value as a step function.

    Used where a series tracks a quantity rather than a count — an Elo, a byte
    total, an exponent — and cumulating events would discard the size of each
    step. The direction of better differs by series, so the subtitle or note
    must say which way is progress.
    """
    _draw(
        out_path,
        title=title,
        subtitle=subtitle,
        ylabel=ylabel,
        series=series,
        ylog=ylog,
        source_label=source_label,
        source_url=source_url,
        built_by=built_by,
        caption=f"{title}. Standing value over time as a step function.",
        note=note,
    )


def ledger_remaining_chart(
    csv_path: Path,
    out_path: Path,
    built_by: str,
) -> None:
    """The six problem-list ledgers' shared remaining-open view.

    Starts at the full list and steps down once per dated resolution, so the
    line answers "how much of this list is left" at any date. Rows resolved
    without a dateable year, and contested or partial rows, never move the
    line; the note states how many such rows the endpoint hides.
    """
    rows = read_csv(csv_path)
    name = rows[0]["list_name"]
    list_year = int(rows[0]["list_year"])
    total = len(rows)
    dated = sorted(
        int(row["resolved_year"])
        for row in rows
        if row["status"] == "resolved" and row["resolved_year"]
    )
    undated = sum(
        row["status"] == "resolved" and not row["resolved_year"] for row in rows
    )
    open_count = sum(row["status"] == "open" for row in rows)
    other = total - len(dated) - undated - open_count
    start = min([list_year, *dated])
    xs = [float(start)]
    ys = [float(total)]
    remaining = total
    for year in dated:
        remaining -= 1
        xs.append(float(year))
        ys.append(float(remaining))
    parts = [f"{open_count} open"]
    if undated:
        parts.append(f"{undated} resolved undated")
    if other:
        parts.append(f"{other} contested / partial / vague")
    note = (f"{remaining} of {total} rows lack a dated resolution: "
            + ", ".join(parts))
    remaining_chart(
        out_path,
        title=f"{name}: rows remaining",
        subtitle="Scored rows minus cumulative dated resolutions; "
                 "undated statuses do not move the line",
        ylabel="Rows without a dated resolution",
        xs=xs,
        ys=ys,
        source_label=rows[0]["source"],
        source_url=sorted({row["source"] for row in rows})[0],
        built_by=built_by,
        note=note,
    )
