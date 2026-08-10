# Sphere-packing lower-bound ladder

**Domain:** mathematics
**Metric:** cumulative improvements to the asymptotic lower bound on sphere-packing density in high dimension
**Coverage:** 1905–2025, eight recorded steps
**Data:** [`sphere-packing-lower-bound-records.csv`](sphere-packing-lower-bound-records.csv)
**Upstream:** per-row `source_url` values, chiefly the survey at <https://arxiv.org/abs/2606.13313>, with the two most recent steps at <https://arxiv.org/abs/2312.10026> and the Klartag preprint recorded in the same survey
**Verdict:** accelerating — and every step is human, which is what this series is here to show

![Cumulative improvements in the asymptotic sphere-packing lower-bound ladder, 1905 to 2025.](discovery-math-sphere-packing.png)

## The problem

How densely can equal spheres be packed in dimension $d$ as $d$ grows? The upper
bounds and the lower bounds are separate literatures, and this series is the lower
bounds: each step exhibits or proves the existence of packings at least as dense
as some function of $d$. Saturation gives $2^{-d}$ for free; everything since has
been an argument for a factor on top of it.

The ladder, with the forms as the vendored rows record them. Minkowski–Hlawka
(1905, in Hlawka's general form 1943) gives
$\theta(d) \geq 2\zeta(d)\,2^{-d}$, a factor of about 2. Rogers (1947) gives the
first asymptotically growing improvement, $\theta(d) \geq c\,d\,2^{-d}$ with
$c = 2/e$; Davenport and Rogers raise $c$ to 1.68 the same year, Ball (1992) to 2,
and Vance (2011) to $6/e$ for dimensions divisible by four. Venkatesh (2013) gets
the first super-linear factor, $d\log\log d$, but only along a sparse sequence of
dimensions. Campos, Jenssen, Michelen and Sahasrabudhe (2023) prove
$(1-o(1))\,d\log d\,2^{-(d+1)}$, the first asymptotically growing improvement on
Rogers valid for all $d$, after seventy-six years. Klartag (2025) gains another
whole power, $c\,n^{2}2^{-n}$, by a new probabilistic method.

A "discovery" here is a published improvement to that form or to its constant. The
series is in this collection as a control rather than a test. It has no AI step at
all, and its two largest steps in eighty years land in 2023 and 2025, immediately
before the period this collection shades. It is the cleanest available warning
against reading proximity to the agent era as an AI effect.

## What the chart shows

Eight steps in 120 years, four of them in the twentieth century and four between
2011 and 2025 — and the last two are the largest since 1947. On the count axis the
recent bend is unmistakable: three steps in the twelve years to 2025 against one in
the forty-five years to 1992.

Every one of them is a human proof, and the chart says so in a callout. None of
the papers involves a machine-learning system. Set against the flat
[analytic-number-theory exponents](../math-antedb/README.md) over the same window, this is
the collection's demonstration that "century-scale bound series do not move much"
is a fact about particular quantities and not about mathematics.

What cuts the reading down is that eight rows is a very small sample, and the
grouping into "four in the twentieth century, four since 2011" is this
repository's arithmetic over those rows rather than a claim any source makes. The
axis also counts rather than measures: a change of constant from 1.68 to 2 and a
gain of a whole power of $n$ are one step each.

## How the chart was built

[`figure.py`](figure.py) reads
`sphere-packing-lower-bound-records.csv`, plots the cumulative step index against
`year` as a step function, and annotates the `finder` for the rows whose year is
one of 1905, 1947, 1992, 2013, 2023 or 2025.

There is no `fetch.py` here. The ladder is transcribed by hand from a survey and
the primary papers it cites, since no upstream publishes it as a machine-readable
series, so the CSV is edited directly and every row carries its own `source_url`.

The design choice that matters is the y-axis. The bound changes functional form
along the ladder — $c\,d\,2^{-d}$ for the mid-century entries, then
$d\log\log d$, then $d\log d$, then $n^{2}$ — so no single scalar runs the length
of the series and there is nothing to plot on a numeric axis. Counting steps is
the honest alternative, and it is the same reason the
[finite-construction groups](../math-alphaevolve-records/README.md) are counted
rather than plotted.

Two consequences of that choice are visible. Both 1947 rows, Rogers and
Davenport–Rogers, sit at the same x position, so their annotations overlap; and
Vance's 2011 step carries no label because 2011 is not in the annotation set. The
`constant_c` column carries the mid-century constants for readers who want the
magnitudes, and the `bound_asymptotic` column carries each form in plain text.

Every row carries its own `source_url`, and the figure records the set of them as
its source rather than naming a single upstream.

## What it cannot support

- **The axis counts steps, not sizes.** A constant nudged from 1.68 to 2 and a
  gain of a whole power of $n$ are one unit each, so the visible slope is a
  frequency and not a rate of improvement.
- **The forms are not comparable.** The constants are only comparable within the
  mid-century $c\,d\,2^{-d}$ family; across families there is no shared unit.
- **Eight rows is a small sample**, and the split into pre- and post-2011 halves is
  this repository's reading of them.
- **The ladder is as the recent literature records it**, not as this collection
  reconstructed it independently, and the 1947 and 1992 constants were not checked
  against those primaries.
- **Two steps are qualified in ways the chart cannot show.** Vance's constant holds
  only for dimensions divisible by four, and Venkatesh's factor only along a sparse
  sequence of dimensions, so neither improves the bound for all $d$ in the way the
  2023 step does.
- **No denominator of effort**, as everywhere in this collection.
- **This is the lower-bound side only.** The upper bounds are a separate
  literature, and the one AI claim in this area is on that side.

## LLM contributions

None in this ladder. Every step from 1905 to 2025 is a human proof, and the two
largest steps in eighty years arrive in the three years immediately before the
agent era.

That absence is the point of including the series. It is a standing counterexample
to inferring an AI effect from timing: a bound series can bend sharply just before
2026 for reasons that have nothing to do with AI, and only per-step attribution
distinguishes the two cases.

The one relevant AI claim sits on the other side of the problem. Astra's August
2026 package claims new sphere-packing upper bounds reaching the Cohn–Elkies
threshold, with Lean certificates and peer review pending. Those are upper bounds;
they do not touch the lower-bound ladder plotted here, and they cannot explain the
2023 and 2025 steps, which predate them and are attributed to named human papers.

## Related literature

The ladder's dates, finders and bound forms are recorded in a recent survey
[@arxiv2026spherepacking], with the 2023 step as its own preprint
[@campos2023sphere]. The comparison this series exists to support is with the
[analytic-number-theory exponents](../math-antedb/README.md), which are structurally the
same object — humans tightening an asymptotic constant over a century — and which
are flat through the window in which this one accelerates. That records are lumpy
and heterogeneous with no AI anywhere in them, so that neither a bend nor a
plateau is by itself a signature, is Sherry and Thompson's finding
[@sherry2021fast]. Where AI steps do appear in this domain they are on finite
constructions with cheap scoring rather than on asymptotic bounds
([kissing number](../math-kissing-11/README.md),
[finite constructions](../math-alphaevolve-records/README.md)).
