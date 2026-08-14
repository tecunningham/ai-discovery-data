# Ben Green's 100 open problems

**Domain:** mathematics
**Metric:** dated resolutions per year across 101 scored rows
**Coverage:** 2018–2026, with dated resolutions running 2019 to 2025; statuses as the list's December 2025 revision records them
**Data:** [`green-problems.csv`](green-problems.csv)
**Upstream:** <https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf>
**Verdict:** no acceleration — under two dated resolutions per year since the list circulated, none dated 2026, and none AI-attributed

![Dated resolutions per year.](discovery-math-green.png)

## The problem

Ben Green's "100 open problems" is a working mathematician's list: one hundred
questions in additive combinatorics, number theory, discrete geometry and
harmonic analysis, circulated since 2018 and revised roughly yearly, with the
statuses updated by the list's own author as problems fall. It sits between the
prestige lists and the Erdős catalogue in character — broader and more personal
than [Hilbert](../math-hilbert/README.md) or
[Millennium](../math-millennium/README.md), but curated by one expert rather
than crowd-assembled — and it earns a place here because Green marks his own
scoreboard: a problem's heading carries "(Solved)" when he judges it solved,
and a dated update note names what solved it.

A "discovery" in this series is a row carrying Green's solved marker together
with the year of the update note recording the solution, which in every case
but one is also the year the resolving work first appeared; the exception is
Problem 9(i), where the update note is dated a year after the Kelley–Meka
preprint and the row carries the preprint's year. The document self-dates its
most recent revision to December 2025, so the ledger is a snapshot of his
scoring as of that revision, read on 2026-08-13.

There are 101 scored rows rather than 100 problems because Problem 9's part
(i) carries its own solved marker while parts (ii) and (iii) stand open, so it
is split into two rows, following how the [Smale ledger](../math-smale/README.md)
handles its split row 11.

## What the chart shows

Of the 101 scored rows, 13 of them carry a dated resolution, running 2019 to
2025: 2 in 2019, 2 in 2021, 1 in 2022, 4 in 2023, 1 in 2024, and 3 in 2025.
One row is scored partial — Problem 11, which Green marks "mostly solved" —
and 87 rows stand open. That is 13 resolutions in 7 years, a steady rate of
just under two per year, with no upward bend at the agent era and no dated
resolution in 2026 at all in this snapshot.

The names on the resolutions are the small circle familiar from the
[Erdős catalogue's](../math-erdos/README.md) recent surge — Sah and Sawhney
appear on three rows, Bedert on one, and Green himself on two — and every one
of them is human. The one AI event Green's document records is not a
resolution: a 2025 update to Problem 35 notes that an "AI-based approach" —
AlphaEvolve [@novikov2025alphaevolve] — improved the upper bound on the
autoconvolution constant $c_\infty$ from 0.75049 to 0.75026, the same family
of constants whose lower-bound ladder is tracked in
[math-sums-autoconvolution](../math-sums-autoconvolution/README.md).

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
ledger as rows remaining, declining as dated resolutions arrive:

![Rows remaining without a dated resolution.](cumulative-math-green.png)

## How the chart was built

[`figure.py`](figure.py) calls the shared `problem_list_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), reading
`green-problems.csv`, keeping rows with `status` equal to `resolved` and a
non-empty `resolved_year`, and counting resolution events by year from the
2018 `list_year` to the present. The cumulative view is the shared
`ledger_remaining_chart()`.

There is no `fetch.py`. The rows are hand-scored from the PDF itself: the
status column follows the "(Solved)" and "(Mostly solved)" markers Green puts
on problem headings, the year comes from his dated update notes, and the
resolver from the names those notes credit. The scoring rule is deliberately
his, not this repository's — a problem counts as resolved exactly when the
list's own author marks it so — which makes the ledger rebuildable by anyone
reading the same PDF, at the cost of the lag documented below.

## What it cannot support

- **The ledger lags the mathematics by up to a revision cycle.** Green updates
  roughly once a year, so a problem solved after December 2025 still reads
  open here. This is not hypothetical: Problem 90 was resolved by Ma, Tang and
  Xu in May 2026 (arXiv 2605.13454), and its row keeps the document's open
  status with a note. The zero at 2026 on the chart is an artifact of the
  revision cycle, not a measurement of 2026.
- **An update year is not a solution date.** The rule dates each resolution to
  Green's update note, which usually matches the resolving preprint's year but
  is his bookkeeping, not the event itself.
- **Marker judgments are one mathematician's.** Problem 22's 2025 bound
  "arguably addresses the original formulation" in Green's own words, and
  Problem 87's solution was announced at Oberwolfach in November 2025 by
  Sawhney in joint work with Green himself — yet neither heading is marked
  solved, so neither is counted. A different scorer would draw the line
  elsewhere.
- **Thirteen events cannot set a slope.** At under two resolutions per year,
  a one-year gap or cluster is noise; the flat verdict is a reading of scale,
  not a fitted trend.
- **Selection is personal.** The list is what one expert found beautiful and
  plausibly attackable around 2018, which is not a sample of mathematics, and
  several rows overlap the Erdős catalogue and the
  [FrontierMath list](../math-frontiermath-open/README.md) (Problems 72 and 81
  appear on the latter), so the ledgers are correlated.
- **Resolution landmarks are not effort-adjusted discovery rates**, here as on
  every ledger in this collection.

## LLM contributions

None, on the resolution ledger — every solved marker credits human
mathematicians. The document's one AI event is the AlphaEvolve bound
improvement on Problem 35 noted above [@novikov2025alphaevolve]: a numerical
record on a continuous quantity, exactly the shape of contribution the
[AlphaEvolve records series](../math-alphaevolve-records/README.md) tracks,
and not a resolution. Around the list rather than on it, Google DeepMind's
formal-conjectures project maintains a milestone formalizing these problems'
statements in Lean (<https://github.com/google-deepmind/formal-conjectures/milestone/2>),
the same statement-formalization infrastructure whose growth the
[Erdős catalogue](../math-erdos/README.md) charts — a marker that AI groups
treat this list as a target set, which makes the zero on its scoreboard the
interesting number. The contrast with the Erdős catalogue is the point: on
that neighbouring corpus, AI systems resolved dozens of problems in 2026 under
a cheap-verification selection; on this list, whose problems ask for bounds
and structural understanding rather than machine-checkable objects, the AI
column is empty.

## Related literature

The list and every status in this ledger are Green's own document
[@green2025openproblems]; the AlphaEvolve note it carries is documented by the
system's paper [@novikov2025alphaevolve]. The Kelley–Meka bound behind row
9(i) and the Gowers–Green–Manners–Tao resolution of Marton's conjecture behind
row 49 are the two results here with their own literatures. The neighbouring
instruments are the [Erdős catalogue](../math-erdos/README.md) and its
[top-10 subset](../math-erdos-top10/README.md), where AI activity is intense,
and the prestige ledgers ([Hilbert](../math-hilbert/README.md),
[Landau](../math-landau/README.md), [Thurston](../math-thurston/README.md),
[Smale](../math-smale/README.md), [Millennium](../math-millennium/README.md),
[TOPP](../math-topp/README.md)), which move less than this list does.
