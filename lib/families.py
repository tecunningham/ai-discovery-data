"""Chart shapes drawn by more than one problem.

Six vulnerability series are the same stacked bar; four prestige lists are the
same cumulative step plot; two Hutter corpora and two AlphaEvolve ladders are
the same standing-record plot. Those shapes live here, parameterised by the CSV
path, so a problem folder holding a series of a known kind is a short call
rather than a copy of 60 lines of matplotlib.

A shape belongs here only once a second problem needs it. One-off charts stay in
the folder that owns them.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

from lib.chart import (
    AI,
    HUMAN,
    FUZZ,
    NEUTRAL,
    NOW,
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
    style(ax, "Vulnerabilities disclosed that year")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7))
    ax.legend(handles=common_legend(fuzz=any(fuzz)), frameon=False, fontsize=8, ncol=3)
    latest = rows[-1]
    ax.text(
        0.02,
        0.9,
        f"{latest['total']} disclosures in partial 2026\n"
        f"{latest['ai_attributed']} explicitly AI-credited",
        transform=ax.transAxes,
        fontsize=9,
        color="#333333",
        va="top",
    )
    source_note(fig, f"Source: {source_label}. Finder credits are floors, not audited causation.")
    save(
        fig,
        out_path,
        f"{title}. Annual finder-attributed vulnerability disclosures; 2026 is partial.",
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
            f"partial year\nthrough {row.get('data_through', 'latest snapshot')}",
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
    rows = read_csv(csv_path)
    name = rows[0]["list_name"]
    start = int(rows[0]["list_year"])
    resolved = [
        (int(row["resolved_year"]), row)
        for row in rows
        if row["status"] == "resolved" and row["resolved_year"]
    ]
    resolved.sort(key=lambda item: (item[0], item[1]["problem_id"]))
    years = [start] + [year for year, _ in resolved] + [NOW]
    counts = [0] + list(range(1, len(resolved) + 1)) + [len(resolved)]
    fig, ax = new_chart(
        f"{name}: dated resolution landmarks",
        "Cumulative rows scored resolved under this ledger; disputed, partial, and vague rows are not counted",
    )
    ax.plot(years, counts, drawstyle="steps-post", color=HUMAN, linewidth=2, zorder=3)
    for index, (year, row) in enumerate(resolved, 1):
        colour = AI if row["problem_id"] == ai_problem else HUMAN
        ax.scatter([year], [index], color=colour, s=52, edgecolor="white", linewidth=0.7, zorder=4)
        if colour == AI:
            ax.annotate(
                f"{row['short_name']}\nformal checks complete; peer review pending",
                (year, index),
                xytext=(-8, 10),
                textcoords="offset points",
                ha="right",
                fontsize=8,
                color=AI,
            )
    open_count = sum(row["status"] == "open" for row in rows)
    other_count = len(rows) - len(resolved) - open_count
    right = NOW + max((NOW - start) * 0.035, 1.2)
    ax.set_xlim(start - max((NOW - start) * 0.04, 1), right)
    ax.set_ylim(-0.3, max(len(resolved) + 2, 2))
    shade_era(ax, right)
    style(ax, "Cumulative resolved rows")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.text(
        0.02,
        0.94,
        f"{len(rows)} scored rows now: {len(resolved)} resolved, "
        f"{open_count} open, {other_count} disputed/partial/vague",
        transform=ax.transAxes,
        fontsize=8.5,
        va="top",
        color="#333333",
    )
    if resolved:
        ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    else:
        # Landau's four rows are all open, so there are no markers to key and the
        # legend swatches would sit on the flat line at zero, where they read as
        # resolution landmarks.
        ax.annotate(
            "no row resolved since the list was posed",
            (start, 0),
            xytext=(8, 12),
            textcoords="offset points",
            fontsize=8.5,
            color=HUMAN,
        )
    source_note(fig, f"Source: {rows[0]['source']}. Years are resolution landmarks, not effort-adjusted discovery rates.")
    save(
        fig,
        out_path,
        f"{name}: cumulative dated resolution landmarks under the source ledger.",
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

