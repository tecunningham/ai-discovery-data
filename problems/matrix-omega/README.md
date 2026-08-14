# Matrix-multiplication exponent ω

**Domain:** algorithms
**Role:** control: no-AI baseline
**Metric:** best proved upper bound on the asymptotic exponent ω of n×n
matrix multiplication; lower is better
**Coverage:** 1969 to 2024, fifteen recorded steps; transcription current to
2026-08-10
**Data:** [`matrix-multiplication-omega.csv`](matrix-multiplication-omega.csv)
**Upstream:**
<https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm#Sub-cubic_algorithms>
(recorded per row in the CSV); the finite small-matrix results are in the
AlphaEvolve paper at <https://arxiv.org/abs/2506.13131>
**Verdict:** declining — 0 new bounds in 2026 and 0 in 2025 against 2 in
2024; movement of 0.0024 over 2010–2024 against 0.4319 over 1969–1990

![Best proved upper bound on the matrix-multiplication exponent from 1969 to 2024, every step human.](discovery-matrix-omega.png)

## Definition

ω is the smallest exponent such that two n×n matrices can be multiplied in
n^(ω+ε) operations for every ε > 0. The naive algorithm gives 3, Strassen's
1969 result was the first to beat it, and the conjectured limit is 2. The
problem itself is fixed — one exactly stated asymptotic quantity, unchanged
since it was posed — so a single number can be tracked across decades of
methods without benchmark drift. Both mathematics and algorithm design keep
score on ω: mathematicians prove the bounds and algorithm designers are
bounded by them. The page is filed under algorithms because the object being
improved is an algorithm's running time.

A "discovery" is a published proof of a smaller upper bound, dated by the
year of the proof. The series records what has been proved rather than what
is computed in practice, and it is a series of bounds: a step means an
analysis improved, not that anyone's matrix multiplication got faster.

The asymptotic exponent and a fast algorithm for one fixed matrix size are
different objects. A procedure that multiplies two 4×4 complex-valued
matrices in 48 scalar multiplications rather than Strassen's 49 is an
improvement on a finite problem; it is not a point on this curve and does
not move ω.

## Facts

- **steps:** 15 recorded steps, 1969 to 2024, all credited human
- **span:** 2.8074 (Strassen, 1969) to 2.371339
  (Alman–Duan–Williams–Xu–Xu–Zhou, 2024)
- **first two decades:** the bound fell 0.4319 from 1969 to 1990, closing at
  2.3755 (Coppersmith–Winograd, 1990)
- **post-2010 steps:** 2.3737 (Stothers, 2010) · 2.3729 (Williams, 2012) ·
  2.3728639 (Le Gall, 2014) · 2.3728596 (Alman–Williams, 2020) · 2.371866
  (Duan–Wu–Zhou, 2022) · 2.371552 (Williams et al., 2024) · 2.371339
  (Alman–Duan–Williams–Xu–Xu–Zhou, 2024)
- **since 2010:** the six steps after the 2010 record total 0.0024 over
  fourteen years
- **last step:** first posted in April 2024 and subsequently published at
  SODA 2025; the record has not moved since

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as the standing record's value over time:

![Standing record for ω over time.](cumulative-matrix-omega.png)

## Method

There is no `fetch.py` here. The chronology is transcribed by hand from a
published record list, one `source_url` per row, so the CSV is edited
directly [@wikipedia2026matmul]. [`check.py`](check.py) recomputes the fact
lines above from the CSV.

[`figure.py`](figure.py) reads `matrix-multiplication-omega.csv` and plots
the `omega` column against `year` as a step function, extended flat to the
present so the standing record is visible as a plateau, with every row also
drawn as a point in human blue. A dotted horizontal line at 2 is labelled
"conjectured limit = 2". Three rows are annotated by matching the
`discoverer` column against Strassen, Coppersmith–Winograd and Alman et al.;
when a name occurs more than once, the latest record is labelled. The axis
is linear and clipped to 1.96 to 2.9, which keeps the post-1990 stretch
readable; January 2026 onward is shaded, and the legend carries the
collection's shared human and AI key even though only human points exist.
The chart's corner note takes the 2010 record as its baseline and counts the
six further improvements after it.

## Limitations

- **a secondary chronology.** The rows reproduce a published record list and
  the source log's earlier transcription of it, one URL for every row,
  rather than fifteen primary papers read in turn.
- **bounds are not implementations.** None of the post-Strassen algorithms
  in this series is used in practice; the constants and crossover sizes make
  them galactic. A falling curve here is not a falling cost of multiplying
  matrices.
- **exponent movements are not percentage speedups.** Nothing converts a
  change in the sixth decimal place of an exponent into a quantity
  comparable with the solver-release and speedrun series in this
  collection.
- **an absence of AI steps on this axis says nothing about the finite
  problem.** The 4×4 complex result exists and is not plotted, by design.

## AI attribution

No step in the series carries an AI credit: the `credit` column is `human`
for all 15 rows, and no AI credit appears in the chronology's source list as
of the 2026-08-10 transcription [@wikipedia2026matmul].

The AI results in this area are on finite matrix sizes. AlphaTensor,
published in 2022, used reinforcement learning with no language model
involved and found faster algorithms for multiplying small matrices, the
first improvement in that setting on Strassen-era results
[@fawzi2022alphatensor]. AlphaEvolve, in 2025, extended the same line,
finding a procedure for two 4×4 complex-valued matrices in 48 scalar
multiplications and describing it as "the first improvement, after 56 years,
over Strassen's algorithm in this setting" [@novikov2025alphaevolve]. Both
results are on the finite object, not on ω. On asymptotic,
structure-heavy problems, Tao's account of AlphaEvolve's run across 67
mathematical problems reports that on analytic number theory it "struggled
to take advantage of the number theoretic structure in the problem, even
when given suitable expert hints", while it "does seem to do well when the
constructions have some algebraic structure" [@tao2025exploration].

## Sources

- [@wikipedia2026matmul] — the published record chronology, recorded as the
  per-row source in the CSV.
- [@fawzi2022alphatensor] — AlphaTensor: the finite-size reinforcement
  learning result in the AI-attribution register, with no language model
  involved.
- [@novikov2025alphaevolve] — AlphaEvolve: the 48-multiplication 4×4
  complex-matrix result quoted in the AI-attribution register.
- [@tao2025exploration] — Tao's account of AlphaEvolve across 67 problems,
  quoted in the AI-attribution register.
- [@sherry2021fast] — the published base rate: across 113 algorithm families
  about half improve little or not at all, and the average family records
  1.44 improvements since 1940.
- [LLMs' Contribution to
  Discovery](https://tecunningham.github.io/posts/2026-08-08-llm-contribution-to-discoveries.html)
  — cites this series from both its mathematics section and its algorithms
  section.
