#!/usr/bin/env python3
"""Extract dated best-bound series from the Analytic Number Theory Exponent Database.

Writes data/antedb-bounds.csv, which
tools/sources_figures.py then plots. The extraction is separated from the
plotting because it needs the ANTEDB source tree and a cddlib-backed
pycddlib, neither of which belongs in this repo's dependencies — the CSV is
vendored the same way the OWID 66-technology CSV is.

What it does: ANTEDB records each bound with the reference that established it,
and its `Hypothesis_Set.list_hypotheses(year=...)` filters to results published
up to a given year. So for each year we can ask the database's own solver for
the best bound *provable from the literature available then*, and read a record
sequence off the answers. The bound at year Y is therefore what the database
believes was derivable in year Y, not what someone had written down — those
differ, because the database's whole point is that combining known relations
yields bounds nobody had stated.

Attribution walks each derived bound's dependency tree to its literature
leaves and reports the latest one, which is the paper that moved the record.

Setup (roughly two minutes, all outside this repo):

    git clone --depth 1 https://github.com/teorth/expdb
    python3 -m venv venv && . venv/bin/activate
    brew install cddlib          # or the system equivalent
    CFLAGS="-I$(brew --prefix)/include -I$(brew --prefix)/include/cddlib" \
      LDFLAGS="-L$(brew --prefix)/lib" pip install "pycddlib<3"
    pip install sympy numpy scipy matplotlib
    python3 tools/antedb_extract.py --expdb path/to/expdb

`pycddlib<3` is required: the ANTEDB code uses the 2.x `cdd.Matrix` API.
"""

from __future__ import annotations

import argparse
import csv
import sys
from fractions import Fraction as frac
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/antedb-bounds.csv"
OUT_SWEEP = ROOT / "data/antedb-sweep.csv"

# mu, A and beta are functions of a parameter, not single series, so picking a
# few points understates how much of the database moves. The sweep records, for
# each point on a grid, how many times the record changed and by how much — so
# the figure can plot progress against the parameter instead of against a
# handful of named slices.
GRID_STEPS = 20

# Which scalar quantities to trace. For mu the relevant conjecture is Lindelof,
# mu(sigma) = 0 for sigma >= 1/2; for the zero-density exponent A the density
# hypothesis is A(sigma) <= 2, already proved for sigma near 1 and open at 3/4.
MU_SIGMAS = [frac(1, 2), frac(3, 5), frac(3, 4), frac(7, 8)]
ZD_SIGMAS = [frac(3, 4), frac(9, 10)]


def literature_years(lit_set) -> list[int]:
    years = set()
    for hypothesis in lit_set.list_hypotheses():
        year = hypothesis.reference.year()
        if isinstance(year, int) and 1900 < year < 2030:
            years.add(year)
    return sorted(years)


def _leaves(hypothesis, found: set, depth: int = 0) -> None:
    """Collect the literature references a derived bound ultimately rests on."""
    if depth > 12:
        return
    dependencies = getattr(hypothesis, "dependencies", None) or []
    if not dependencies:
        reference = hypothesis.reference
        if reference.is_literature() and isinstance(reference.year(), int):
            found.add((reference.year(), reference.author()))
        return
    for dependency in dependencies:
        _leaves(dependency, found, depth + 1)


def _attribution(hypothesis) -> str:
    found: set = set()
    _leaves(hypothesis, found, 0)
    if not found:
        reference = hypothesis.reference
        author = reference.author()
        return author if author != "Unknown author" else ""
    return max(found)[1]


def mu_series(lit_set, sigma, years, hypothesis_set_cls, best_mu_bound) -> list[dict]:
    rows = []
    for year in years:
        available = hypothesis_set_cls()
        available.add_hypotheses(lit_set.list_hypotheses(year=year))
        try:
            best = best_mu_bound(sigma, available)
        except Exception:
            continue
        rows.append(
            {
                "quantity": "mu",
                "sigma": str(sigma),
                "year": year,
                "value": str(frac(best.data.mu)),
                "value_float": float(best.data.mu),
                "attribution": _attribution(best),
            }
        )
    return rows


def zd_series(lit_set, sigma, years, hypothesis_set_cls) -> list[dict]:
    """Best A(sigma) available each year, minimised over the recorded estimates."""
    rows = []
    for year in years:
        available = hypothesis_set_cls()
        available.add_hypotheses(lit_set.list_hypotheses(year=year))
        best, who = None, ""
        for hypothesis in available.list_hypotheses(hypothesis_type="Zero density estimate"):
            if not hypothesis.data.interval.contains(sigma):
                continue
            try:
                value = frac(hypothesis.data.at(sigma))
            except Exception:
                continue
            if best is None or value < best:
                best, who = value, hypothesis.reference.author()
        if best is None:
            continue
        rows.append(
            {
                "quantity": "A",
                "sigma": str(sigma),
                "year": year,
                "value": str(best),
                "value_float": float(best),
                "attribution": who,
            }
        )
    return rows


def _records(rows: list[tuple[int, "frac"]]) -> list[tuple[int, "frac"]]:
    """Keep only the years where the value actually changed."""
    out, last = [], None
    for year, value in rows:
        if value != last:
            out.append((year, value))
            last = value
    return out


def sweep_mu(lit_set, years, hypothesis_set_cls) -> list[dict]:
    """mu across a grid of sigma, using the piecewise solver (one solve a year)."""
    from bound_mu import best_mu_bound_piecewise
    from functions import Interval

    grid = [frac(1, 2) + frac(i, GRID_STEPS) * frac(1, 2) for i in range(GRID_STEPS)]
    collected: dict = {g: [] for g in grid}
    for year in years:
        available = hypothesis_set_cls()
        available.add_hypotheses(lit_set.list_hypotheses(year=year))
        try:
            pieces = best_mu_bound_piecewise(Interval(frac(1, 2), 1), available)
        except Exception as exc:
            print(f"    mu sweep {year}: skipped ({str(exc)[:50]})")
            continue
        for point in grid:
            best = None
            for piece in pieces:
                try:
                    value = piece.at(point)
                except Exception:
                    value = None
                if value is None:
                    continue
                value = frac(value)
                if best is None or value < best:
                    best = value
            if best is not None:
                collected[point].append((year, best))
    return _rows_from(collected, "mu", "sigma")


def sweep_zd(lit_set, years, hypothesis_set_cls) -> list[dict]:
    grid = [frac(1, 2) + frac(i, GRID_STEPS) * frac(1, 2) for i in range(1, GRID_STEPS)]
    collected: dict = {g: [] for g in grid}
    for year in years:
        available = hypothesis_set_cls()
        available.add_hypotheses(lit_set.list_hypotheses(year=year))
        for point in grid:
            best = None
            for hypothesis in available.list_hypotheses(hypothesis_type="Zero density estimate"):
                if not hypothesis.data.interval.contains(point):
                    continue
                try:
                    value = frac(hypothesis.data.at(point))
                except Exception:
                    continue
                if best is None or value < best:
                    best = value
            if best is not None:
                collected[point].append((year, best))
    return _rows_from(collected, "A", "sigma")


def sweep_beta(lit_set, years, hypothesis_set_cls) -> list[dict]:
    """beta across a grid of alpha in (0, 1/2)."""
    import exponent_pair as ep

    grid = [frac(i, 2 * GRID_STEPS) for i in range(1, GRID_STEPS)]
    collected: dict = {g: [] for g in grid}
    for year in years:
        available = hypothesis_set_cls()
        available.add_hypotheses(lit_set.list_hypotheses(year=year))
        try:
            bounds = ep.compute_best_beta_bounds(available)
        except Exception as exc:
            # One year (1991) trips an internal error in the database's own
            # solver. Recorded rather than silently dropped.
            print(f"    beta sweep {year}: skipped ({str(exc)[:50]})")
            continue
        for point in grid:
            best = None
            for bound in bounds:
                try:
                    value = bound.data.bound.at(point)
                except Exception:
                    value = None
                if value is None:
                    continue
                value = frac(value)
                if best is None or value < best:
                    best = value
            if best is not None:
                collected[point].append((year, best))
    return _rows_from(collected, "beta", "alpha")


def _rows_from(collected: dict, quantity: str, parameter: str) -> list[dict]:
    """Long format: one row per record change, so the full series can be plotted.

    Only the years where the value moved are kept. A step-post plot through them,
    extended to the present, reconstructs the series exactly.
    """
    rows = []
    for point, series in collected.items():
        if not series:
            continue
        records = _records(series)
        for year, value in records:
            rows.append(
                {
                    "quantity": quantity,
                    "parameter": parameter,
                    "point": str(point),
                    "point_float": float(point),
                    "year": year,
                    "value": str(value),
                    "value_float": float(value),
                }
            )
    rows.sort(key=lambda r: (r["quantity"], r["point_float"], r["year"]))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expdb", required=True, help="path to a checkout of github.com/teorth/expdb"
    )
    args = parser.parse_args()

    python_dir = Path(args.expdb).expanduser().resolve() / "blueprint/src/python"
    if not python_dir.is_dir():
        raise SystemExit(f"no ANTEDB python package at {python_dir}")
    sys.path.insert(0, str(python_dir))

    import matplotlib

    matplotlib.use("Agg")  # the ANTEDB modules import pyplot at module scope
    import literature as lit_module
    from bound_mu import best_mu_bound
    from hypotheses import Hypothesis_Set

    lit_set = lit_module.literature
    years = literature_years(lit_set)
    print(f"{len(years)} years carry a literature entry, {years[0]}–{years[-1]}")

    rows: list[dict] = []
    for sigma in MU_SIGMAS:
        series = mu_series(lit_set, sigma, years, Hypothesis_Set, best_mu_bound)
        rows += series
        distinct = len({r["value"] for r in series})
        print(f"  mu({sigma}): {len(series)} years, {distinct} distinct values")
    for sigma in ZD_SIGMAS:
        series = zd_series(lit_set, sigma, years, Hypothesis_Set)
        rows += series
        distinct = len({r["value"] for r in series})
        print(f"  A({sigma}):  {len(series)} years, {distinct} distinct values")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["quantity", "sigma", "year", "value", "value_float", "attribution"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT.relative_to(ROOT)}")

    print("sweeping the three parameterised families across a grid")
    sweep: list[dict] = []
    sweep += sweep_zd(lit_set, years, Hypothesis_Set)
    sweep += sweep_mu(lit_set, years, Hypothesis_Set)
    sweep += sweep_beta(lit_set, years, Hypothesis_Set)
    for quantity in ("mu", "A", "beta"):
        subset = [r for r in sweep if r["quantity"] == quantity]
        if not subset:
            continue
        per_point: dict = {}
        for row in subset:
            per_point.setdefault(row["point_float"], []).append(row)
        counts = [len(v) for v in per_point.values()]
        ratios = [v[-1]["value_float"] / v[0]["value_float"] for v in per_point.values()]
        moved = sum(1 for c in counts if c > 1)
        print(f"  {quantity}: {len(per_point)} grid points, {moved} moved, "
              f"records {min(counts)}–{max(counts)}, "
              f"ratio {min(ratios):.3f}–{max(ratios):.3f}")
    with OUT_SWEEP.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["quantity", "parameter", "point", "point_float",
                        "year", "value", "value_float"],
        )
        writer.writeheader()
        writer.writerows(sweep)
    print(f"wrote {len(sweep)} rows to {OUT_SWEEP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
