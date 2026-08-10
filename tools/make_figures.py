#!/usr/bin/env python3
"""Generate one chart per discovery series from the vendored CSVs in data/.

Run: python3 tools/make_figures.py   (or: make figures)

Every chart shares one visual language so series can be compared without
re-learning the chart: AI-credited red, human or uncredited blue, fuzzer amber,
vendor-run grey, open markers pending or unacknowledged, and January 2026
onward shaded. Output goes to figures/, one PNG per series.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, ScalarFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"

AI = "#c1442f"
HUMAN = "#2f6cc1"
FUZZ = "#c98a00"
VENDOR = "#777777"
NEUTRAL = "#aaaaaa"
ERA_START = 2026.0
ANNUAL_ERA_START = 2025.5
NOW = 2026.62


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def save(fig, filename: str, description: str, sources: list[str]) -> None:
    fig.subplots_adjust(left=0.09, right=0.97, top=0.84, bottom=0.15)
    fig.savefig(
        OUT / filename,
        dpi=180,
        metadata={
            "Title": description.split(".")[0],
            "Description": description,
            "Source": " | ".join(sources),
            "Software": "tools/make_figures.py",
        },
    )
    plt.close(fig)
    print(f"wrote {filename}")


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


def cyber_stacked(
    csv_name: str,
    filename: str,
    title: str,
    subtitle: str,
    source_label: str,
    source_url: str,
) -> None:
    rows = read(csv_name)
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
        filename,
        f"{title}. Annual finder-attributed vulnerability disclosures; 2026 is partial.",
        [source_url],
    )


def cyber_simple_bars(
    csv_name: str,
    value_column: str,
    filename: str,
    title: str,
    subtitle: str,
    ylabel: str,
    colour: str,
    source_label: str,
    source_url: str,
) -> None:
    rows = read(csv_name)
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
    save(fig, filename, f"{title}. Annual count; 2026 is partial.", [source_url])


def cyber_charts() -> None:
    cyber_stacked(
        "curl-vulnerabilities.csv",
        "discovery-cyber-curl.png",
        "curl vulnerability disclosures",
        "One fixed codebase; annual disclosures split by explicit finder credit",
        "curl vulnerability JSON, counted in the vendored CSV",
        "https://curl.se/docs/vuln.json",
    )
    cyber_stacked(
        "openssl-vulnerabilities.csv",
        "discovery-cyber-openssl.png",
        "OpenSSL vulnerability disclosures",
        "One critical library; annual disclosures split by explicit finder credit",
        "OpenSSL vulnerability index, counted in the vendored CSV",
        "https://openssl-library.org/news/vulnerabilities/",
    )
    cyber_stacked(
        "firefox-advisories.csv",
        "discovery-cyber-firefox.png",
        "Firefox vulnerability disclosures",
        "Security-advisory CVEs split by explicit AI, fuzzer, or other credit",
        "Mozilla foundation-security-advisories, counted in the vendored CSV",
        "https://github.com/mozilla/foundation-security-advisories",
    )
    cyber_simple_bars(
        "ossfuzz-discoveries.csv",
        "discoveries",
        "discovery-cyber-oss-fuzz.png",
        "OSS-Fuzz vulnerability discoveries",
        "Automated fuzzing baseline: annual records in the OSS-Fuzz archive",
        "Vulnerabilities found that year",
        FUZZ,
        "OSV OSS-Fuzz archive, counted by record id",
        "https://osv.dev/list?q=ecosystem%3AOSS-Fuzz",
    )
    cyber_simple_bars(
        "nvd-kev-by-year.csv",
        "nvd_published",
        "discovery-cyber-nvd-disclosed.png",
        "All software: vulnerabilities disclosed",
        "Every CVE published in the US National Vulnerability Database",
        "CVEs disclosed that year",
        HUMAN,
        "NVD API, counted by publication year",
        "https://nvd.nist.gov/developers/vulnerabilities",
    )
    cyber_simple_bars(
        "nvd-kev-by-year.csv",
        "kev_added",
        "discovery-cyber-kev-exploited.png",
        "All software: vulnerabilities known exploited",
        "Annual additions to CISA's Known Exploited Vulnerabilities catalogue",
        "Added to the exploited list",
        HUMAN,
        "CISA KEV feed, counted by catalogue-addition year",
        "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
    )


def erdos_chart() -> None:
    rows = read("erdos-database-history.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    solved = [int(row["total_solved"]) for row in rows]
    total = [int(row["total_problems"]) for row in rows]
    lean = [int(row["lean_formalized"]) for row in rows]
    fig, ax = new_chart(
        "Erdős problems: catalogue status over time",
        "Site snapshots, not historical solution dates; the comparable window is only eleven months",
    )
    ax.plot(xs, total, drawstyle="steps-post", color=NEUTRAL, linestyle="--", linewidth=1.7, label="catalogued")
    ax.plot(xs, solved, drawstyle="steps-post", color=HUMAN, linewidth=2, marker="o", markersize=4, label="marked solved")
    ax.plot(xs, lean, drawstyle="steps-post", color="#8a6fb8", linestyle=":", linewidth=1.7, label="Lean-formalized")
    right = max(xs) + 0.08
    ax.set_xlim(min(xs) - 0.04, right)
    ax.set_ylim(0, max(total) * 1.16)
    shade_era(ax, right)
    style(ax, "Problems", "Site snapshot")
    tick_idx = list(range(0, len(rows), 2))
    if tick_idx[-1] != len(rows) - 1:
        tick_idx.append(len(rows) - 1)
    ax.set_xticks([xs[i] for i in tick_idx])
    ax.set_xticklabels([rows[i]["month"] for i in tick_idx], rotation=30, ha="right")
    # The AI-standalone stock (~13) is two orders of magnitude below the
    # catalogue stocks, so plot it as a callout rather than a point on this axis.
    ax.text(
        0.98,
        0.18,
        "Separate stock (wiki freeze 2026-06-30):\n"
        f"~13 full AI-standalone resolutions\n"
        f"vs {solved[-1]} statuses marked solved",
        transform=ax.transAxes,
        fontsize=8.5,
        color=AI,
        ha="right",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=AI, linewidth=0.8, alpha=0.92),
    )
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    source_note(fig, "Source: teorth/erdosproblems statistics and the AI-resolution wiki; stocks are not an AI-vs-human flow.")
    save(
        fig,
        "discovery-math-erdos.png",
        "Erdős problem catalogue stocks and a separately counted AI-resolution stock.",
        ["https://github.com/teorth/erdosproblems"],
    )


def problem_list_chart(list_id: str, filename: str, ai_problem: str | None = None) -> None:
    rows = [row for row in read("famous-open-problem-lists.csv") if row["list_id"] == list_id]
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
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    source_note(fig, f"Source: {rows[0]['source']}. Years are resolution landmarks, not effort-adjusted discovery rates.")
    save(
        fig,
        filename,
        f"{name}: cumulative dated resolution landmarks under the source ledger.",
        sorted({row["source"] for row in rows}),
    )


def antedb_chart() -> None:
    rows = read("antedb-sweep.csv")
    series: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        series[(row["quantity"], row["point"])].append((int(row["year"]), float(row["value_float"])))
    events: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for (quantity, _point), values in series.items():
        values.sort()
        previous = values[0][1]
        for year, value in values[1:]:
            if value != previous:
                events[quantity][year] += 1
                previous = value
    fig, ax = new_chart(
        "ANTEDB analytic-number-theory exponents",
        "Cumulative slice-level record changes across 58 parameter points; one theorem can move many slices",
    )
    labels = {"mu": r"$\mu$: 20 slices", "A": r"$A$: 19 slices", "beta": r"$\beta$: 19 slices"}
    line_styles = {"mu": "-", "A": "--", "beta": ":"}
    for quantity in ("mu", "A", "beta"):
        cumulative = 0
        xs = [min(events[quantity])]
        ys = [0]
        for year, count in sorted(events[quantity].items()):
            cumulative += count
            xs.append(year)
            ys.append(cumulative)
        xs.append(NOW)
        ys.append(cumulative)
        ax.plot(
            xs,
            ys,
            drawstyle="steps-post",
            color=HUMAN,
            linestyle=line_styles[quantity],
            linewidth=2,
            label=labels[quantity],
        )
    right = 2030
    ax.set_xlim(1915, right)
    shade_era(ax, right)
    style(ax, "Cumulative slice-level improvements")
    ax.legend(frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.88,
        "All plotted changes are derived from human literature.\nNo LLM-attributed step appears in the vendored series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: ANTEDB extraction. Counts are parameter-slice changes, not independent papers or discoveries.")
    save(
        fig,
        "discovery-math-antedb.png",
        "ANTEDB cumulative record changes across 58 exponent slices, grouped by family.",
        ["https://github.com/teorth/expdb"],
    )


def sphere_chart() -> None:
    rows = read("sphere-packing-lower-bound-records.csv")
    years = [int(row["year"]) for row in rows]
    steps = list(range(1, len(rows) + 1))
    fig, ax = new_chart(
        "Sphere-packing lower-bound ladder",
        "Cumulative improvements because the bound changes functional form and cannot share one numeric y-axis",
    )
    ax.plot(years + [NOW], steps + [steps[-1]], drawstyle="steps-post", color=HUMAN, linewidth=2)
    ax.scatter(years, steps, color=HUMAN, s=52, edgecolor="white", linewidth=0.7, zorder=4)
    for index, row in enumerate(rows):
        if row["year"] in {"1905", "1947", "1992", "2013", "2023", "2025"}:
            ax.annotate(
                row["finder"].split(" (")[0],
                (years[index], steps[index]),
                xytext=(-4, 8),
                textcoords="offset points",
                fontsize=7.5,
                color=HUMAN,
                ha="right",
            )
    right = 2032
    ax.set_xlim(1898, right)
    ax.set_ylim(0.4, len(rows) + 1.2)
    shade_era(ax, right)
    style(ax, "Cumulative improvements to the bound")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.text(
        0.98,
        0.12,
        "The two newest steps, 2023 and 2025,\nare human proofs; no AI step is in this ladder.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, "Source URLs are carried row-by-row in sphere-packing-lower-bound-records.csv.")
    save(
        fig,
        "discovery-math-sphere-packing.png",
        "Cumulative improvements in the asymptotic sphere-packing lower-bound ladder.",
        sorted({row["source_url"] for row in rows}),
    )


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


def alphaevolve_value_chart(
    problems: list[str],
    filename: str,
    title: str,
    subtitle: str,
    ylabel: str,
    annotations: dict[tuple[str, str], str] | None = None,
) -> None:
    rows = [
        row
        for row in read("alphaevolve-records.csv")
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
    source_note(fig, "Source: alphaevolve-records.csv, transcribed from the paper and cited follow-ons. Open markers have uncertain dates.")
    save(
        fig,
        filename,
        f"{title}. Standing records over time with AI and human authorship.",
        sorted({row["ref"] for row in rows if row["ref"]}),
    )


def related_alphaevolve_chart() -> None:
    selected = {"6.5", "6.7", "6.48", "6.49", "6.50"}
    rows = [
        row
        for row in read("alphaevolve-records.csv")
        if row["problem"] in selected and row["year"] and row.get("is_record", "yes") == "yes"
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["problem"]].append(row)
    fig, ax = new_chart(
        "Finite construction records around AlphaEvolve",
        "Cumulative record steps by problem group; values have incompatible units, so this plots discoveries rather than levels",
    )
    labels = {
        "6.5": "minimum-overlap type",
        "6.7": "difference basis",
        "6.48": "triangle packing",
        "6.49": "convex packing",
        "6.50": "max-min packing",
    }
    line_styles = ["-", "--", ":", "-.", (0, (3, 1, 1, 1))]
    for index, problem in enumerate(sorted(grouped)):
        local = sorted(grouped[problem], key=lambda row: (int(row["year"]), row["quantity"], int(row["step"])))
        xs = [int(row["year"]) for row in local]
        ys = list(range(1, len(local) + 1))
        ax.plot(
            xs + [NOW],
            ys + [ys[-1]],
            drawstyle="steps-post",
            color=NEUTRAL,
            linestyle=line_styles[index],
            linewidth=1.5,
            label=labels[problem],
        )
        for x, y, row in zip(xs, ys, local):
            record_marker(ax, x, y, row, size=45)
    right = 2030
    ax.set_xlim(min(int(row["year"]) for row in rows) - 5, right)
    shade_era(ax, right)
    style(ax, "Cumulative record steps in group")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(frameon=False, fontsize=7.3, ncol=2)
    ax.text(
        0.02,
        0.93,
        "Red points are AI-set records; blue points are human.\n"
        "The difference-basis step followed a supplied Singer-code hint.",
        transform=ax.transAxes,
        fontsize=8.3,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: alphaevolve-records.csv. Multiple quantities within a group are counted separately.")
    save(
        fig,
        "discovery-math-alphaevolve-related-records.png",
        "Cumulative record steps in selected finite construction and packing problems.",
        sorted({row["ref"] for row in rows if row["ref"]}),
    )


def matrix_omega_chart() -> None:
    rows = read("matrix-multiplication-omega.csv")
    years = [int(row["year"]) for row in rows]
    values = [float(row["omega"]) for row in rows]
    fig, ax = new_chart(
        "Matrix-multiplication exponent ω",
        "Best proved asymptotic upper bound; lower is better and every recorded step is human",
    )
    ax.plot(years + [NOW], values + [values[-1]], drawstyle="steps-post", color=HUMAN, linewidth=2)
    ax.scatter(years, values, color=HUMAN, s=45, edgecolor="white", linewidth=0.6, zorder=4)
    ax.axhline(2, color=VENDOR, linestyle=":", linewidth=1)
    ax.text(1970, 2.025, "conjectured limit = 2", fontsize=8, color="#555555")
    for target in ("Strassen", "Coppersmith–Winograd", "Alman et al."):
        row = next(row for row in rows if row["discoverer"] == target)
        ax.annotate(
            target,
            (int(row["year"]), float(row["omega"])),
            xytext=(5, 7),
            textcoords="offset points",
            fontsize=7.5,
            color=HUMAN,
        )
    right = 2030
    ax.set_xlim(1965, right)
    ax.set_ylim(1.96, 2.9)
    shade_era(ax, right)
    style(ax, "Best proved upper bound on ω")
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    # Counted at plot time rather than written into the caption, so re-vendoring
    # the chronology cannot leave the annotation asserting a stale count.
    recent = [value for year, value in zip(years, values) if year >= 2010]
    earlier = [value for year, value in zip(years, values) if year < 2010]
    ax.text(
        0.98,
        0.22,
        f"{len(recent)} human improvements since 2010, worth "
        f"{earlier[-1] - recent[-1]:.4f} together;\nno LLM-attributed step in the series.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        ha="right",
    )
    source_note(fig, "Source: matrix-multiplication-omega.csv; secondary chronology matching the existing source-log transcription.")
    save(
        fig,
        "discovery-matrix-omega.png",
        "Best proved upper bound on the matrix-multiplication exponent over time.",
        sorted({row["source_url"] for row in rows}),
    )


def math_charts() -> None:
    erdos_chart()
    problem_list_chart("hilbert", "discovery-math-hilbert.png")
    problem_list_chart("smale", "discovery-math-smale.png", ai_problem="16")
    problem_list_chart("millennium", "discovery-math-millennium.png")
    problem_list_chart("topp", "discovery-math-topp.png")
    antedb_chart()
    sphere_chart()
    alphaevolve_value_chart(
        ["6.8"],
        "discovery-math-kissing-11.png",
        "Kissing number in dimension 11",
        "Standing lower bound: human records, AlphaEvolve, then collective AI agents",
        "Best known lower bound K(11)",
        {("6.8", "3"): "AlphaEvolve", ("6.8", "4"): "collective agents"},
    )
    alphaevolve_value_chart(
        ["6.44", "6.3"],
        "discovery-math-sums-autoconvolution.png",
        "Sums-and-differences and autoconvolution",
        "Two related standing lower-bound ladders; colour marks who set each step",
        "Best known lower bound",
        {("6.44", "4"): "AlphaEvolve", ("6.44", "6"): "human retakes record", ("6.3", "3"): "AlphaEvolve"},
    )
    related_alphaevolve_chart()
    matrix_omega_chart()


def nanogpt_chart() -> None:
    rows = read("nanogpt-records.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["minutes"]) for row in rows]
    fig, ax = new_chart(
        "modded-nanogpt training speedrun",
        "All 86 listed runs: minutes to the fixed target loss; lower is better",
    )
    ax.plot(xs + [NOW], ys + [ys[-1]], drawstyle="steps-post", color=NEUTRAL, linewidth=1.5)
    for x, y, row in zip(xs, ys, rows):
        colour = AI if row["agent"] == "ai" else HUMAN
        ax.scatter([x], [y], color=colour, s=48 if colour == AI else 20, edgecolor="white", linewidth=0.5, zorder=4)
        if row["ai_system"]:
            ax.annotate(row["ai_system"], (x, y), xytext=(3, 7), textcoords="offset points", fontsize=7, color=AI)
    right = NOW + 0.12
    ax.set_xlim(min(xs) - 0.08, right)
    ax.set_yscale("log")
    ax.set_yticks([1.5, 2, 3, 5, 10, 20, 45])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    shade_era(ax, right)
    style(ax, "Minutes to target loss (log scale)", "Date of run")
    ax.legend(handles=common_legend(), frameon=False, fontsize=8)
    ax.text(0.02, 0.13, "45 → 1.27 minutes; 4 of 86 listed runs are AI-credited.", transform=ax.transAxes, fontsize=8.5)
    source_note(fig, "Source: KellerJordan/modded-nanogpt README, vendored as nanogpt-records.csv.")
    save(
        fig,
        "discovery-algorithms-nanogpt.png",
        "modded-nanogpt training-speed records with credited AI systems marked.",
        ["https://github.com/KellerJordan/modded-nanogpt"],
    )


def cifar_chart() -> None:
    rows = [row for row in read("cifar-speedrun-records.csv") if row["date"] >= "2022"]
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["seconds"]) for row in rows]
    fig, ax = new_chart(
        "CIFAR-10 speedrun",
        "Seconds to 94% accuracy on one A100; lower is better",
    )
    ax.plot(xs + [NOW], ys + [ys[-1]], drawstyle="steps-post", color=NEUTRAL, linewidth=1.5)
    for x, y, row in zip(xs, ys, rows):
        colour = AI if row["agent"] == "ai" else HUMAN
        uncertain = row["date_precision"] == "undated" or row["acknowledged"] == "no"
        ax.scatter(
            [x],
            [y],
            s=55,
            facecolor="none" if uncertain else colour,
            edgecolor=colour,
            linewidth=1.5 if uncertain else 0.7,
            zorder=4,
        )
        if row["agent"] == "ai":
            label = (
                "Hiverge"
                if row["acknowledged"] == "yes"
                else "Fulcrum/Fable\nunacknowledged"
            )
            offset = (-5, 8) if row["acknowledged"] == "yes" else (-7, 11)
            ax.annotate(
                label,
                (x, y),
                xytext=offset,
                textcoords="offset points",
                ha="right",
                fontsize=7.5,
                color=AI,
            )
    right = NOW + 0.15
    ax.set_xlim(min(xs) - 0.08, right)
    ax.set_yscale("log")
    ax.set_yticks([2, 3, 5, 10, 20])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    shade_era(ax, right)
    style(ax, "Seconds to 94% accuracy (log scale)", "Record date")
    ax.legend(handles=common_legend(pending=True), frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.14,
        "The open red 1.828 s point is unacknowledged\nand carries specification-gaming caveats.",
        transform=ax.transAxes,
        fontsize=8.3,
    )
    source_note(fig, "Source: dates assembled from releases and announcements in cifar-speedrun-records.csv; no official ledger exists.")
    save(
        fig,
        "discovery-algorithms-cifar10.png",
        "CIFAR-10 speedrun records on one A100 with AI and uncertain records marked.",
        ["https://github.com/KellerJordan/cifar10-airbench"],
    )


def stockfish_chart() -> None:
    rows = read("stockfish-ncm-elo.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    ys = [float(row["elo_vs_sf15"]) for row in rows]
    fig, ax = new_chart(
        "Stockfish development builds on fixed hardware",
        "20,000 games per build against Stockfish 15; releases are marked",
    )
    ax.plot(xs, ys, color="#9fb3cc", linewidth=1, zorder=2)
    releases = [(x, y, row["release"]) for x, y, row in zip(xs, ys, rows) if row["release"]]
    ax.scatter([row[0] for row in releases], [row[1] for row in releases], color=HUMAN, s=35, edgecolor="white", linewidth=0.5, zorder=4)
    llm_x = year_fraction("2026-07-26")
    ax.scatter([llm_x], [ys[-1]], s=70, facecolor="none", edgecolor=AI, linewidth=1.6, zorder=5)
    ax.annotate(
        "first LLM-credited master commit:\n0.6% speed patch, not an Elo record",
        (llm_x, ys[-1]),
        xytext=(-8, -35),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=AI,
    )
    right = 2027
    ax.set_xlim(2013, right)
    shade_era(ax, right)
    style(ax, "Elo relative to Stockfish 15")
    ax.legend(handles=common_legend(pending=True), frameon=False, fontsize=8)
    source_note(fig, "Source: nextchessmove.com fixed-machine development-build tests, vendored as stockfish-ncm-elo.csv.")
    save(
        fig,
        "discovery-algorithms-stockfish.png",
        "Stockfish fixed-hardware Elo progression with the first LLM-credited commit marked.",
        ["https://nextchessmove.com/dev-builds"],
    )


def compression_chart(series: str, filename: str, title: str, subtitle: str) -> None:
    all_rows = read("compression-records.csv")
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
        "Source: prize.hutter1.net and mattmahoney.net/dc/text.html, vendored as compression-records.csv.",
    )
    save(
        fig,
        filename,
        f"{title}. Hutter Prize compression records with pending entries open.",
        ["https://prize.hutter1.net/", "http://mattmahoney.net/dc/text.html"],
    )


def gurobi_chart() -> None:
    rows = read("gurobi-milp-speedups.csv")
    xs = [year_fraction(row["date"]) for row in rows]
    factors = []
    cumulative = 1.0
    for row in rows:
        cumulative *= float(row["release_speedup"])
        factors.append(cumulative)
    fig, ax = new_chart(
        "Gurobi mixed-integer programming speed",
        "Cumulative vendor-reported speedup over v9.5; fixed-machine release comparisons",
    )
    ax.plot([2022.0] + xs + [NOW], [1.0] + factors + [factors[-1]], drawstyle="steps-post", color=VENDOR, linewidth=2)
    ax.scatter(xs, factors, color=VENDOR, s=55, edgecolor="white", linewidth=0.7, zorder=4)
    for x, y, row in zip(xs, factors, rows):
        ax.annotate(row["release"], (x, y), xytext=(4, -12), textcoords="offset points", fontsize=8, color=VENDOR)
    right = NOW + 0.3
    ax.set_xlim(2022, right)
    ax.set_ylim(0.95, max(factors) * 1.2)
    shade_era(ax, right)
    style(ax, "Cumulative speedup since v9.5")
    ax.legend(handles=common_legend(vendor=True), frameon=False, fontsize=8)
    ax.text(
        0.02,
        0.9,
        f"×{factors[-1]:.2f} across four releases.\nNo AI credit in the release notes.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#333333",
        va="top",
    )
    source_note(fig, "Source: Gurobi release announcements; vendor-run figures, transcribed with URLs in gurobi-milp-speedups.csv.")
    save(
        fig,
        "discovery-algorithms-gurobi.png",
        "Cumulative Gurobi vendor-reported MILP speedup across releases 10 through 13.",
        [row["source_url"] for row in rows],
    )


def algorithms_charts() -> None:
    nanogpt_chart()
    cifar_chart()
    stockfish_chart()
    compression_chart(
        "hutter_enwik9",
        "discovery-algorithms-enwik9.png",
        "Hutter Prize compression: enwik9",
        "Standing CPU-capped records on the 1 GB corpus; lower total size is better",
    )
    compression_chart(
        "hutter_enwik8",
        "discovery-algorithms-enwik8.png",
        "Hutter Prize compression: enwik8",
        "The retired 100 MB series provides a pre-agent record-cadence baseline",
    )
    gurobi_chart()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cyber_charts()
    math_charts()
    algorithms_charts()


if __name__ == "__main__":
    main()
