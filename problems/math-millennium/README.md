# Millennium Prize Problems

- **Domain:** mathematics
- **Role:** prestige ledger
- **Metric:** dated resolutions per year across 7 scored rows
- **Coverage:** list posed 2000; one dated resolution, 2003; statuses read 2026-08-14
- **Data:** [`millennium-problems.csv`](millennium-problems.csv)
- **Upstream:** <https://www.claymath.org/millennium-problems/>
- **Verdict:** no acceleration — 0 resolutions in 2026; 1 dated resolution (2003) over 2000–2025

![Dated resolutions per year.](discovery-math-millennium.png)

## Definition

The Clay Mathematics Institute named seven problems in 2000 and attached a
US$1 million prize to each [@clay2000millennium]. A "discovery" in this
series is a row moving to `resolved`, dated by the year of the resolving
work. The list needs no subproblem splitting and has no contested rows:
seven problems, one resolved, six open.

The one resolved row is the Poincaré conjecture. The ledger dates it 2003,
the year of the last of Perelman's arXiv preprints; the row's `notes` column
records that the preprints ran 2002 to 2003 and that the prize was announced
in 2010.

## Facts

- **rows:** 7 scored; 1 resolved with a dated year; 6 open
- **by-year:** 2003: 1
- **ai-attributed:** 0 of 1 dated resolutions
- **open rows:** bsd, hodge, navier_stokes, p_vs_np, yang_mills, riemann

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws the
ledger as rows remaining:

![Rows remaining without a dated resolution.](cumulative-math-millennium.png)

### poincare — Poincaré conjecture
- **status:** resolved
- **resolved:** 2003
- **resolver:** Perelman
- **notes:** arXiv 2002–2003; Clay prize announced 2010

> "Nearly a century passed between its formulation in 1904 by Henri Poincaré
> and its solution by Grigoriy Perelman, announced in preprints posted on
> ArXiv.org in 2002 and 2003."
> — Clay Mathematics Institute, Poincaré Conjecture page, read 2026-08-14 [@clay2000millennium]

## Method

The seven rows are hand-scored from the Clay Mathematics Institute's own
pages, which the `source` column names for every row; there is no
`fetch.py`. The Institute's site lists the Poincaré conjecture under solved
problems and the other six as open, and the ledger mirrors that split. Of
the three candidate dates for the one event — preprints 2002–2003, prize
announced 2010 — the `resolved_year` takes 2003, the end of the preprint
span.

[`figure.py`](figure.py) calls the shared `problem_list_chart()` in
[`../../lib/families.py`](../../lib/families.py), which keeps the rows whose
`status` is `resolved` with a non-empty `resolved_year` and counts
resolution events by year from the 2000 `list_year` to the present. No
`ai_problem` argument is passed, because no row carries an AI credit. The
cumulative view is the shared `ledger_remaining_chart()`.
[`check.py`](check.py) recomputes the fact lines and the register entry from
the CSV.

## Limitations

- **sample size.** One dated resolution in 26 years; no rate or trend is
  estimable from this series.
- **dating.** Preprints 2002–2003, prize announced 2010; the ledger dates
  the event 2003, and a different defensible choice moves the only step by
  up to seven years.
- **acknowledgement lag.** Seven years passed between the 2003 preprints and
  the 2010 prize announcement, so a recent resolution of another row could
  predate its appearance here by years.
- **overlap.** riemann is Hilbert row 8a and Smale row 1; p_vs_np is Smale
  row 3. The prestige ledgers are not independent samples.
- **effort.** Resolution landmarks are not effort-adjusted discovery rates.

## AI attribution

No row in [`millennium-problems.csv`](millennium-problems.csv) names an AI
system in its `resolver` or `notes` columns; the one dated resolution is
Perelman's, dated 2003. No AI credit appears on the Clay Mathematics
Institute's problem pages as of the 2026-08-14 read.

## Sources

- [@clay2000millennium] — the Institute's own list and status pages, the
  ledger source for every row and the register quote.
- [@arxiv2026horizonmath] — a 2026 benchmark of over 100 predominantly
  unsolved problems chosen so that "verification is computationally
  efficient and simple"; frontier models score near 0% on it.
- [@sherry2021fast] — measured improvement rates across algorithm families,
  including multi-decade stationary stretches, with no AI involved.
- Sibling ledgers of the same instrument type:
  [Hilbert](../math-hilbert/README.md), [Landau](../math-landau/README.md),
  [Thurston](../math-thurston/README.md), [Smale](../math-smale/README.md)
  and [TOPP](../math-topp/README.md).
- [Erdős](../math-erdos/README.md) — a catalogue ledger over a different
  corpus, counting a different unit (catalogue problems with imputed
  solution years).
