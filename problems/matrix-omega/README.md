# Matrix-multiplication exponent ω

**Domain:** algorithms
**Metric:** best proved upper bound on the asymptotic exponent ω of n×n matrix multiplication; lower is better
**Coverage:** 1969 to 2024, fifteen recorded steps
**Data:** [`matrix-multiplication-omega.csv`](matrix-multiplication-omega.csv)
**Upstream:** <https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm#Sub-cubic_algorithms> (recorded per row in the CSV); the finite small-matrix results are in the AlphaEvolve paper at <https://arxiv.org/abs/2506.13131>
**Verdict:** declining — the asymptotic record is slowing, and no step in it is AI-attributed

![Best proved upper bound on the matrix-multiplication exponent from 1969 to 2024, every step human.](discovery-matrix-omega.png)

This is the one series in the collection that
[LLMs' Contribution to Discovery](https://tecunningham.github.io/posts/2026-08-08-llm-contribution-to-discoveries.html)
cites from both its mathematics section and its algorithms section, and the
duplication is deliberate: ω is a complexity bound that both fields keep score
on. Mathematicians prove it and algorithm designers are bounded by it, so the
same staircase answers a question in each domain. The document is filed under
algorithms because the object being improved is an algorithm's running time.

## The problem

ω is the smallest exponent such that two n×n matrices can be multiplied in
n^(ω+ε) operations for every ε > 0. The naive algorithm gives 3, Strassen's 1969
result was the first to beat it, and the conjectured limit is 2. What is fixed
here is the problem itself — one exactly stated asymptotic quantity, unchanged for
fifty-seven years — which is what lets a single number be tracked across a
century of methods without any question of benchmark drift.

A "discovery" is a published proof of a smaller upper bound. Two consequences
follow and both matter for reading the chart. The series records what has been
proved rather than what is computed in practice, and it is a series of bounds, so
a step means somebody's analysis improved, not that anyone's matrix multiplication
got faster.

The asymptotic exponent and a fast algorithm for one fixed matrix size are
different objects, and this is the distinction the series exists to hold. A
procedure that multiplies two 4×4 complex-valued matrices in 48 scalar
multiplications rather than Strassen's 49 is a real improvement on a finite
problem. It is not a point on this curve, and it does not move ω. Conversely,
the absence of an AI step on this curve is not evidence that AI has contributed
nothing to matrix multiplication.

## What the chart shows

2.8074 for Strassen in 1969, falling through a rapid two decades to 2.3755 for
Coppersmith and Winograd in 1990 — a drop of 0.43 in twenty-one years — and then
almost nothing. The seven steps the CSV records from 2010 onward are 2.3737
(Stothers, 2010), 2.3729 (Williams, 2012), 2.3728639 (Le Gall, 2014), 2.3728596
(Alman and Williams, 2020), 2.371866 (Duan, Wu and Zhou, 2022), 2.371552
(Williams and co-authors, 2024) and 2.371339 (Alman and co-authors, 2024). That is
a total movement of 0.0024 in fourteen years, two orders of magnitude smaller
than the first two decades bought, and the record has not moved since 2024.

Every step in the series is a human proof. There is no AI-attributed entry, and
the flat 2026 shaded band is the point of drawing it.

The chart's own corner note counts the improvements since 2010 and their combined
size at plot time, so it cannot fall out of step with the vendored chronology. It
currently reads seven improvements worth 0.0042 together.

## How the chart was built

[`figure.py`](figure.py)
reads `matrix-multiplication-omega.csv` and plots the `omega` column against
`year` as a step function, extended flat to the present so the standing record is
visible as a plateau rather than ending in mid-air, with every row also drawn as
a point in human blue. A dotted horizontal line at 2 is labelled "conjectured
limit = 2". Three rows are annotated by matching the `discoverer` column against
Strassen, Coppersmith–Winograd and Alman et al. The axis is linear and clipped to
1.96 to 2.9, which is what makes the post-1990 stretch readable at all; January
2026 onward is shaded, and the legend carries the collection's shared human and
AI key even though only human points exist.

There is no `fetch.py` here. The chronology is transcribed by hand from a
published record list, one `source_url` per row, so the CSV is edited directly.

One artefact of the annotation is worth knowing before reading labels off the
figure. `discoverer` is matched with a first-match lookup and the name
Coppersmith–Winograd appears twice, at 2.496 in 1981 and 2.3755 in 1990, so the
label lands on the earlier row.

## What it cannot support

- **This is a secondary chronology.** The rows reproduce a published record list
  and the source log's earlier transcription of it, one URL for every row, rather
  than fifteen primary papers read in turn.
- **Bounds are not implementations.** None of the post-Strassen algorithms in this
  series is used in practice; the constants and crossover sizes make them
  galactic. A falling curve here is not a falling cost of multiplying matrices.
- **Two 2024 rows cannot be ordered.** The CSV carries year precision only, so
  the last two steps are drawn in file order and their sequence within the year is
  not established here.
- **Sixth-decimal-place movements are not comparable with percentage speedups**
  elsewhere in this collection. Nothing converts a change in an exponent into a
  quantity that can be set beside an 8% solver release or a 23% speedrun step.
- **The label placement is a first-match lookup,** as noted above, so a
  discoverer who set two records is labelled at the earlier one.
- **An absence of AI steps on this axis says nothing about the finite problem.**
  The 4×4 complex result exists and is not plotted, by design.

## LLM contributions

None to the asymptotic exponent. The AI results in this area are all on finite
matrix sizes, and there are two, neither of which is a language-model result in
the same sense.

AlphaTensor, published in 2022, used reinforcement learning with no language model
involved and found faster algorithms for multiplying small matrices, the first
improvement in that setting on Strassen-era results [@fawzi2022alphatensor]. It is
the useful control for this whole collection: a system with no language model in
it produced genuine algorithmic improvements, so a 2026 result should not be
credited to model capability by default. AlphaEvolve, in 2025, extended the same
line, finding a procedure for two 4×4 complex-valued matrices in 48 scalar
multiplications and describing it as "the first improvement, after 56 years, over
Strassen's algorithm in this setting" [@novikov2025alphaevolve].

Both are on the finite object, not on ω. Where AlphaEvolve was pointed at the
kind of asymptotic, structure-heavy mathematics this exponent belongs to, the
result was negative: Tao's account of the system's run across 67 mathematical
problems reports that on analytic number theory it "struggled to take advantage of
the number theoretic structure in the problem, even when given suitable expert
hints", while it "does seem to do well when the constructions have some algebraic
structure" [@tao2025exploration]. That is a statement about problem form rather
than difficulty, and it is the best available explanation of why a bound like this
one has no AI step in it.

## Related literature

The chronology is a published record list, recorded per row in the CSV
[@wikipedia2026matmul]. The two AI results on finite matrices are AlphaTensor
[@fawzi2022alphatensor] and AlphaEvolve [@novikov2025alphaevolve], with Tao's
assessment of where the latter works and where it does not
[@tao2025exploration]. For the base rate, a slow-then-stalled exponent is
unremarkable: across 113 algorithm families about half improve little or not at
all, and the average family records 1.44 improvements since 1940
[@sherry2021fast].
