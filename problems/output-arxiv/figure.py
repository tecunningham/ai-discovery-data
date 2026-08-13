#!/usr/bin/env python3
"""Draw this folder's four figures from its monthly submission counts.

Run: python3 problems/output-arxiv/figure.py

output-arxiv-submissions.png plots submissions per month;
output-arxiv-by-field.png splits the same months by top-level field group;
output-arxiv-math-subfields.png is a small-multiples grid of the math.*
subfields; cumulative-output-arxiv.png redraws the total as cumulative
submissions to date, for the collection-wide cumulative index.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import (  # noqa: E402
    AS_OF_DATE,
    NOW,
    UNATTRIBUTED,
    new_chart,
    save,
    shade_era,
    source_note,
    style,
    year_fraction,
)
from lib.cumulative import counts_chart  # noqa: E402
from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The month ChatGPT was released, which is the comparison the series is usually
# put to. Named here rather than in the text so the arithmetic below cannot
# drift from the label it produces.
CHATGPT = "2022-11"

# Archives arXiv subsumed into the modern taxonomy; the harvested primary
# categories on old papers still carry these names, and dropping them would
# delete the early years of exactly the subfields with the longest histories.
LEGACY = {
    "alg-geom": "math.AG", "dg-ga": "math.DG", "funct-an": "math.FA",
    "q-alg": "math.QA", "cmp-lg": "cs.CL", "chao-dyn": "nlin.CD",
    "patt-sol": "nlin.PS", "adap-org": "nlin.AO", "comp-gas": "nlin.CG",
    "solv-int": "nlin.SI", "acc-phys": "physics.acc-ph",
    "ao-sci": "physics.ao-ph", "atom-ph": "physics.atom-ph",
    "bayes-an": "physics.data-an", "chem-ph": "physics.chem-ph",
    "plasm-ph": "physics.plasm-ph", "supr-con": "cond-mat.supr-con",
    "mtrl-th": "cond-mat.mtrl-sci",
}
# arXiv's own grouping: math-ph sits with physics, not mathematics.
PHYSICS_ARCHIVES = {
    "astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th",
    "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph",
}
GROUP_OF_ARCHIVE = {
    "math": "mathematics", "cs": "computer science", "stat": "statistics",
    "eess": "elec. eng. & systems", "econ": "economics",
    "q-bio": "quantitative biology", "q-fin": "quantitative finance",
    **{archive: "physics" for archive in PHYSICS_ARCHIVES},
}
# Paul Tol's bright palette: this chart compares fields, a semantics none of
# the collection's finder colours carry, so it takes its own hues.
FIELD_COLOURS = {
    "physics": "#4477aa", "mathematics": "#ee6677",
    "computer science": "#228833", "statistics": "#ccbb44",
    "elec. eng. & systems": "#66ccee", "quantitative biology": "#aa3377",
    "quantitative finance": "#ee8866", "economics": "#888888",
}
MATH_SUBFIELD_NAMES = {
    "math.AC": "Commutative Algebra", "math.AG": "Algebraic Geometry",
    "math.AP": "Analysis of PDEs", "math.AT": "Algebraic Topology",
    "math.CA": "Classical Analysis", "math.CO": "Combinatorics",
    "math.CT": "Category Theory", "math.CV": "Complex Variables",
    "math.DG": "Differential Geometry", "math.DS": "Dynamical Systems",
    "math.FA": "Functional Analysis", "math.GM": "General Mathematics",
    "math.GN": "General Topology", "math.GR": "Group Theory",
    "math.GT": "Geometric Topology", "math.HO": "History and Overview",
    "math.IT": "Information Theory", "math.KT": "K-Theory",
    "math.LO": "Logic", "math.MG": "Metric Geometry",
    "math.NA": "Numerical Analysis", "math.NT": "Number Theory",
    "math.OA": "Operator Algebras", "math.OC": "Optimization and Control",
    "math.PR": "Probability", "math.QA": "Quantum Algebra",
    "math.RA": "Rings and Algebras", "math.RT": "Representation Theory",
    "math.SG": "Symplectic Geometry", "math.SP": "Spectral Theory",
    "math.ST": "Statistics Theory",
}


def group_of(category: str) -> str:
    """The top-level field group a primary category belongs to.

    Unknown archives fail loudly: a silent "other" bucket would absorb any
    future taxonomy change and quietly bend the field lines.
    """
    modern = LEGACY.get(category, category)
    archive = modern.split(".")[0]
    if archive not in GROUP_OF_ARCHIVE:
        raise SystemExit(f"unmapped arXiv archive {archive!r} ({category!r})")
    return GROUP_OF_ARCHIVE[archive]


def by_field() -> None:
    rows = read_csv(HERE / "arxiv-monthly-by-category.csv")
    per_group: dict[str, defaultdict] = {}
    for row in rows:
        group = group_of(row["category"])
        per_group.setdefault(group, defaultdict(int))
        per_group[group][row["month"]] += int(row["submissions"])
    months = sorted({row["month"] for row in rows})
    # The last harvested month is partial; the lines stop at the last
    # complete one so no field appears to collapse.
    months = months[:-1]
    xs = [year_fraction(month) for month in months]
    fig, ax = new_chart(
        "arXiv submissions per month, by field",
        "Primary category grouped to arXiv's own top level; volume, not discovery",
    )
    order = sorted(per_group, key=lambda g: -per_group[g][months[-1]])
    placed: list[float] = []
    for group in order:
        series = per_group[group]
        ys = [series[month] for month in months]
        ax.plot(xs, ys, color=FIELD_COLOURS[group], linewidth=1.5, zorder=3)
        # Direct labels at the right edge, nudged apart when two fields end
        # at nearly the same level; a ten-entry legend would be unreadable.
        label_y = ys[-1]
        gap = max(series[months[-1]] for series in per_group.values()) * 0.035
        while any(abs(label_y - other) < gap for other in placed):
            label_y += gap
        placed.append(label_y)
        ax.annotate(
            group,
            (xs[-1], label_y),
            xytext=(6, 0),
            textcoords="offset points",
            fontsize=7.8,
            color=FIELD_COLOURS[group],
            va="center",
        )
    right = NOW + 6.5
    ax.set_xlim(min(xs) - 0.6, right)
    ax.set_ylim(0, None)
    shade_era(ax, right)
    style(ax, "New submissions that month")
    source_note(
        fig,
        "Source: arXiv OAI-PMH metadata, month of first version, primary "
        "category only.",
    )
    save(
        fig,
        HERE / "output-arxiv-by-field.png",
        "arXiv submissions per month by top-level field group.",
        ["https://oaipmh.arxiv.org/oai"],
        __file__,
    )


def math_subfields() -> None:
    rows = read_csv(HERE / "arxiv-monthly-by-category.csv")
    per_subfield: dict[str, defaultdict] = {}
    for row in rows:
        modern = LEGACY.get(row["category"], row["category"])
        if not modern.startswith("math."):
            continue
        per_subfield.setdefault(modern, defaultdict(int))
        per_subfield[modern][row["month"]] += int(row["submissions"])
    months = sorted({month for series in per_subfield.values()
                     for month in series})[:-1]
    xs = [year_fraction(month) for month in months]
    order = sorted(per_subfield,
                   key=lambda s: -sum(per_subfield[s].values()))
    columns = 4
    grid_rows = -(-len(order) // columns)
    fig, axes = plt.subplots(
        grid_rows, columns, figsize=(8.4, 1.35 * grid_rows + 1.1),
        sharex=True, squeeze=False,
    )
    fig.suptitle(
        "arXiv mathematics submissions per month, by subfield",
        x=0.06, y=0.99, ha="left", fontsize=14, fontweight="bold",
    )
    fig.text(0.06, 0.99 - 0.5 / (1.35 * grid_rows + 1.1),
             "Primary category only; panels sorted by total volume and "
             "scaled independently; the shaded band is Jan 2026 onward",
             fontsize=9.2, color="#444444", ha="left", va="top")
    for ax, subfield in zip(axes.flat, order):
        series = per_subfield[subfield]
        ys = [series[month] for month in months]
        ax.plot(xs, ys, color=UNATTRIBUTED, linewidth=0.9)
        ax.axvspan(2026.0, max(xs), color="#c1442f", alpha=0.07, zorder=0)
        ax.set_title(
            f"{subfield} · {MATH_SUBFIELD_NAMES.get(subfield, '')}",
            loc="left", fontsize=7.2, color="#333333", pad=2,
        )
        ax.text(0.02, 0.86, f"{ys[-1]:,}", transform=ax.transAxes,
                fontsize=6.8, color="#777777", va="top")
        ax.set_ylim(0, max(ys) * 1.15 or 1)
        ax.tick_params(labelsize=6.4, colors="#777777", length=2)
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#cccccc")
    for ax in axes.flat[len(order):]:
        ax.axis("off")
    source_note(
        fig,
        "Source: arXiv OAI-PMH metadata; legacy archives (alg-geom, q-alg, "
        "dg-ga, funct-an) are mapped to their modern subfields. The corner "
        "number is the last complete month.",
    )
    save(
        fig,
        HERE / "output-arxiv-math-subfields.png",
        "Monthly arXiv submissions for every mathematics subfield.",
        ["https://oaipmh.arxiv.org/oai"],
        __file__,
        adjust={"left": 0.06, "right": 0.985,
                "top": 1 - 1.0 / (1.35 * grid_rows + 1.1),
                "bottom": 0.55 / (1.35 * grid_rows + 1.1),
                "hspace": 0.55, "wspace": 0.08},
    )


def cumulative() -> None:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts_chart(
        HERE / "cumulative-output-arxiv.png",
        title="arXiv submissions: cumulative",
        ylabel="Submissions to date, millions",
        period_labels=[row["month"] for row in rows],
        counts=[int(row["submissions"]) / 1e6 for row in rows],
        source_label="arxiv.org/stats download, vendored as arxiv-monthly.csv",
        source_url="https://arxiv.org/stats/monthly_submissions",
        built_by=__file__,
    )


def main() -> None:
    rows = read_csv(HERE / "arxiv-monthly.csv")
    counts = {row["month"]: int(row["submissions"]) for row in rows}
    # The last row is the month in progress at fetch time, so every comparison
    # uses the last complete month instead. That rule silently breaks when a
    # fetch lands just after a month boundary, before arXiv opens the new
    # month's row — so assert it rather than assume it.
    if rows[-1]["month"] != f"{AS_OF_DATE.year}-{AS_OF_DATE.month:02d}":
        raise SystemExit(
            f"the last row is {rows[-1]['month']}, not the AS_OF_DATE month "
            f"{AS_OF_DATE.year}-{AS_OF_DATE.month:02d}; the last-row-is-partial "
            "rule no longer holds")
    last = rows[-2]["month"]
    span = (year_fraction(last) - year_fraction(CHATGPT))
    growth = counts[last] / counts[CHATGPT] - 1

    volume_series(
        HERE / "output-arxiv-submissions.png",
        xs=[year_fraction(row["month"]) for row in rows],
        ys=[int(row["submissions"]) for row in rows],
        title="arXiv submissions per month",
        subtitle="Every preprint submitted since 1991; volume, not discovery",
        ylabel="New submissions that month",
        reading=f"{counts[CHATGPT]:,} in {CHATGPT}, when ChatGPT was released\n"
                f"{counts[last]:,} in {last} — up {growth:.0%} in {span:.1f} years,\n"
                f"after decades of steadier growth",
        source_label="arxiv.org/stats download, vendored as arxiv-monthly.csv",
        source_url="https://arxiv.org/stats/monthly_submissions",
        built_by=__file__,
        partial_last="part month",
    )
    by_field()
    math_subfields()
    cumulative()


if __name__ == "__main__":
    main()
