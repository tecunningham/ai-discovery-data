# Millennium Prize Problems

- **Domain:** mathematics
- **Role:** prestige ledger
- **Metric:** dated resolutions per year across 7 scored rows
- **Coverage:** list posed 2000; one dated resolution, 2003; one claim, 2026; Clay statuses read 2026-08-14, the claim read 2026-09-13
- **Data:** [`millennium-problems.csv`](millennium-problems.csv)
- **Upstream:** <https://www.claymath.org/millennium-problems/>
- **Verdict:** no acceleration — 0 resolutions in 2026; 1 dated resolution (2003) over 2000–2025

![Dated resolutions per year.](discovery-math-millennium.png)

## Definition

The Clay Mathematics Institute named seven problems in 2000 and attached a
US$1 million prize to each [@clay2000millennium]. A "discovery" in this
series is a row moving to `resolved`, dated by the year of the resolving
work. The list needs no subproblem splitting: seven problems, one resolved,
one claimed, five open. A `claimed` row is a resolution its authors have
announced that the Institute has not accepted and no journal has refereed;
it carries the announcement year and contributes nothing to the series.

The one resolved row is the Poincaré conjecture. The ledger dates it 2003,
the year of the last of Perelman's arXiv preprints; the row's `notes` column
records that the preprints ran 2002 to 2003 and that the prize was announced
in 2010.

## Facts

- **rows:** 7 scored; 1 resolved with a dated year; 1 claimed; 5 open
- **by-year:** 2003: 1
- **ai-attributed:** 0 of 1 dated resolutions
- **claimed rows:** navier_stokes (2026)
- **open rows:** bsd, hodge, p_vs_np, yang_mills, riemann

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

### navier_stokes — Navier–Stokes existence and smoothness
- **status:** claimed
- **resolved:** 2026
- **resolver:** OpenAI internal multi-agent system; Lean-checked; announced 2026-09-08
- **notes:** finite-time blow-up with smooth forcing on R^3 and on the torus,
  Clay alternatives C and D; manuscript and Lean certificates published
  2026-09-08; not refereed; Clay page unchanged

> "For every positive viscosity, we prove two results: Whole space ℝ³: There
> exist smooth initial data and forcing for which no global smooth solution
> with uniformly bounded kinetic energy exists. Periodic torus ℝ³/ℤ³: There
> exist smooth periodic initial data and forcing for which no global smooth
> solution exists."
> — OpenAI, NavierStokesAndEuler repository README, read 2026-09-13 [@openai2026navierstokes]

> "These are alternatives (C) 'Breakdown of Navier–Stokes solutions on ℝ³'
> and (D) 'Breakdown of Navier–Stokes Solutions on ℝ³/ℤ³' in the Clay
> Mathematics Institute's official problem description of the Navier–Stokes
> existence and smoothness Millennium Prize Problem."
> — OpenAI, NavierStokesAndEuler repository README, read 2026-09-13 [@openai2026navierstokes]

## Method

The seven rows are hand-scored; the `source` column names the page each
row's status rests on, the Clay Mathematics Institute's own pages for six of
them and, for the claimed row, the repository OpenAI published its proof
certificates in; there is no `fetch.py`. The Institute's site lists the
Poincaré conjecture under solved problems and the other six as open. Of the
three candidate dates for the one resolution — preprints 2002–2003, prize
announced 2010 — the `resolved_year` takes 2003, the end of the preprint
span. The claimed row's `resolved_year` is the announcement year, 2026; the
status moves to `resolved` or `contested` when the Institute's own listing
does, and the row is re-read each time the ledger is.

[`figure.py`](figure.py) calls the shared `problem_list_chart()` in
[`../../lib/families.py`](../../lib/families.py), which keeps the rows whose
`status` is `resolved` with a non-empty `resolved_year` and counts
resolution events by year from the 2000 `list_year` to the present. No
`ai_problem` argument is passed, because no dated resolution carries an AI
credit. The cumulative view is the shared `ledger_remaining_chart()`, whose
drawn line ignores the claimed row; the data file it writes beside the PNG
also carries a tentative line that steps down at 2026 as if the claim held,
which the collection's comparison page shows on request.
[`check.py`](check.py) recomputes the fact lines and the register entries
from the CSV.

## Limitations

- **sample size.** One dated resolution in 26 years; no rate or trend is
  estimable from this series.
- **dating.** Preprints 2002–2003, prize announced 2010; the ledger dates
  the event 2003, and a different defensible choice moves the only step by
  up to seven years.
- **acknowledgement lag.** Seven years passed between the 2003 preprints and
  the 2010 prize announcement, so a recent resolution of another row could
  predate its appearance here by years.
- **claim status.** The Navier–Stokes row rests on its authors' announcement
  and machine-checked certificates, not on refereeing or on the Institute's
  acceptance; the Institute's page for the problem was not re-read after
  2026-08-14 for this entry.
- **overlap.** riemann is Hilbert row 8a and Smale row 1; p_vs_np is Smale
  row 3. The prestige ledgers are not independent samples.
- **effort.** Resolution landmarks are not effort-adjusted discovery rates.

## AI attribution

The one dated resolution is Perelman's, dated 2003, with no AI credit. The
claimed row names an AI system: its `resolver` column reads "OpenAI internal
multi-agent system; Lean-checked; announced 2026-09-08", and the register
entry above quotes the result as the repository's README states it
[@openai2026navierstokes]. The claim is not a dated resolution in this
series and the **ai-attributed** fact line counts 0 of 1. No AI credit
appears on the Clay Mathematics Institute's problem pages as of the
2026-08-14 read.

## Sources

- [@clay2000millennium] — the Institute's own list and status pages, the
  ledger source for six rows and the Poincaré register quote.
- [@openai2026navierstokes] — OpenAI's repository of Lean certificates for
  its Navier–Stokes and Euler results, first committed 2026-09-08; the
  source of the claimed row and its register quotes.
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
