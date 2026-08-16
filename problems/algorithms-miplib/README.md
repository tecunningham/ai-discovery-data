# MIPLIB 2017 solution frontier

- **Domain:** algorithms
- **Role:** discovery series
- **Metric:** better feasible incumbents, first feasible solutions and
optimality updates announced in MIPLIB 2017 solufile releases
- **Coverage:** 2019-08-26 through 2026-01-26, 28 releases with explicit
solution counts
- **Data:** [`miplib-solution-releases.csv`](miplib-solution-releases.csv), one
public solufile release per row
- **Upstream:** <https://miplib.zib.de/news.html> and
<https://miplib.zib.de/download.html>
- **Verdict:** no acceleration — 40 announced updates in the single 2026
release against 13 in 2025 and a 90.1/year mean over 2019–2025

![Annual MIPLIB incumbent, first-feasible and optimality updates.](discovery-algorithms-miplib.png)

## Definition

MIPLIB is a standard public library of mixed-integer programs. Its
maintainers accept new solutions to open instances and periodically publish a
new solution file, announcing each release in the site's News Log. This
series treats the 2017 collection as a maintained frontier: a better
incumbent improves a known feasible objective, a first feasible solution
closes an instance with no prior incumbent, and an optimality update proves
or records that the frontier cannot be improved.

The three kinds are counted separately because they record different work. A
"discovery" is one announced update, dated by the release announcement; the
unit is the count stated in each announcement, not a solver run and not the
number of changed lines in a downloaded solution file.

## Facts

- **releases:** 28 releases with explicit solution counts, 2019-08-26
  through 2026-01-26
- **totals:** 599 better incumbents, 44 optimality updates and 28 first
  feasible solutions
- **by-year (all update kinds):** 2019: 146 · 2020: 227 · 2021: 11 ·
  2022: 49 · 2023: 40 · 2024: 145 · 2025: 13 · 2026: 40
- **2024:** 137 better incumbents across 7 releases
- **2026:** the single 2026 release, solufile 36 of 2026-01-26, reports 40
  better incumbents

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as cumulative announced solution updates to date:

![Cumulative announced solution updates to date.](cumulative-algorithms-miplib.png)

## Method

The News Log was transcribed by hand into
[`miplib-solution-releases.csv`](miplib-solution-releases.csv). For
announcements that give a total and say how many were first-known or optimal,
the categories are made disjoint: the 91 improved incumbents in February 2020
become 86 ordinary improvements, two first feasible solutions and three
optima. Open-to-hard/easy status changes are counted as first feasible;
"marked optimal" entries are kept in `optimal_status_only`.

[`figure.py`](figure.py) aggregates releases by year and stacks the three
update kinds without treating them as the same event type.
[`fetch.py`](fetch.py) is a staleness probe rather than a fetcher, because
the classification depends on prose; it checks whether the live log has
advanced beyond solufile 36. [`check.py`](check.py) recomputes the fact lines
above from the CSV.

## Limitations

- **publication dates, not discovery dates.** A year with one large release
  does not mean every improvement was found on that release date; annual
  counts are publication cadence as well as discovery cadence.
- **vocabulary drift.** The news prose changes vocabulary across releases, so
  category boundaries require the explicit rules stated in Method.
- **unweighted counts.** Counts do not measure objective magnitude or
  instance difficulty.
- **the collection is substantially but not perfectly fixed.** Corrected
  instances and status tags exist; the library is cleaner than annual
  benchmark scores, not immutable.
- **category overlap.** A newly optimal solution can overlap conceptually
  with an improved incumbent; the CSV makes categories disjoint to avoid
  double-counting.

## AI attribution

No AI system or language model is credited in the release-log entries
transcribed here, through the 2026-01-26 release. Submitters and solver
provenance are not recorded consistently enough in these aggregate
announcements to infer whether an AI tool contributed, so the absence of an
AI label is not evidence of absence.

## Sources

- [News Log](https://miplib.zib.de/news.html) — the release announcements
  every row is transcribed from.
- [Download page](https://miplib.zib.de/download.html) — preserves old
  solution files and fixed collection lists, allowing a future
  instance-level reconstruction of objective magnitudes.
- [MIPLIB history](https://miplib.zib.de/history.html) — the sequence of
  MIPLIB editions.
- [MIPLIB 2017 paper](https://doi.org/10.1007/s12532-020-00194-3) — documents
  collection and benchmark selection for the 2017 edition.
- Sibling series: [CVRPLIB X instances](../algorithms-cvrplib/README.md)
  counts posted record events for a different fixed instance cohort;
  [Gurobi MILP speed](../algorithms-gurobi/README.md) measures solver
  release speedups on the same problem class.
