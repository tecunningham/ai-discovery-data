# Sums-and-differences and autoconvolution constants

- **Domain:** mathematics
- **Role:** discovery series
- **Metric:** best known lower bounds on two additive-combinatorics constants, $C_{6.44}$ and $C_{6.3}$ in the AlphaEvolve numbering
- **Coverage:** 2007–2025, twelve record steps across the two ladders
- **Data:** [`sums-autoconvolution-records.csv`](sums-autoconvolution-records.csv), the problem 6.44 and 6.3 rows of the AlphaEvolve record transcription
- **Upstream:** <https://arxiv.org/abs/2511.02864> and the follow-on sources recorded per row in the CSV's `ref` and `note` columns
- **Verdict:** inconclusive — 0 record steps in 2026 against 7 in 2025; the other 5 fall in 2007 and 2010

![Record lower bounds on the sums-and-differences and autoconvolution constants, with AI and human steps distinguished.](discovery-math-sums-autoconvolution.png)

## Definition

Two constants from the AlphaEvolve problem set, both bounded below by
exhibiting a finite object whose score can be computed exactly. For
$C_{6.44}$, in sums and differences of sets, the object is a set of
integers: taking $U = \{0,1,3\}$ gives
$C_{6.44} \geq 1 + \log(7/6) / \log 7 \approx 1.0792$, and later records
come from larger sets found by search. For $C_{6.3}$, an autocorrelation
inequality, the object is a step function, and the recorded bracket at the
start of the series is $0.88922 \leq C_{6.3} \leq 1$.

A "discovery" here is a construction that moves one of those bounds, one
row of the vendored CSV. Both quantities carry AI and human record steps in
2025, with each kind overtaking the other at least once.

## Facts

- **steps:** 12 record steps: 8 on $C_{6.44}$ (2007–2025) and 4 on $C_{6.3}$
  (2010–2025)
- **by-year:** 2007: 4 · 2010: 1 · 2025: 7
- **ai steps:** 4 of 12, all AlphaEvolve, all in 2025, two on each ladder
- **c-6.44 ladder:** 1.07921778 → 1.1078 → 1.1165 → 1.14465 (all 2007,
  Gyarmati, Hennecart and Ruzsa) → 1.1479 → 1.1584 (2025, AlphaEvolve) →
  1.17305 → 1.173077 (2025, human)
- **c-6.3 ladder:** 0.88922 (2010) → 0.8962 (2025, AlphaEvolve) → 0.901564
  (2025, Boyer and Li) → 0.961 (2025, AlphaEvolve)
- **step sizes, c-6.44:** AI +0.28% and +0.91%; human +2.6%, +0.79% and
  +2.5% in 2007, +1.26% and +0.002% in 2025
- **step sizes, c-6.3:** AI +0.78% and +6.6%; human +0.60%
- **parent-frame medians:** +0.98% per AlphaEvolve step against +2.52% for
  human computer search and +2.83% for human work by hand, pooled over every
  record step in
  [`../math-alphaevolve-records/alphaevolve-records.csv`](../math-alphaevolve-records/alphaevolve-records.csv)

The largest AI step, $C_{6.3}$'s move to 0.961 from a step function of
50,000 parts, was built after the Boyer–Li result, per the CSV's
`attribution` column; on that step the paper states:

> "We believe that with even more parts, this lower bound can be further
> improved."
> — Georgiev, Gómez-Serrano, Tao and Wagner, arXiv 2511.02864, 2025 [@georgiev2025mathexploration]

The 2025 human step to 1.17305 is Gerbicz's, in a paper the arXiv 2511.02864
bibliography lists with the title

> "Sums and differences of sets (improvement over AlphaEvolve)"
> — Robert Gerbicz, arXiv:2505.16105, 2025

and the further step to 1.173077 is cited there as

> "Fan Zheng. Sums and differences of sets: a further improvement over
> AlphaEvolve, 2025. arXiv:2506.01896."
> — arXiv 2511.02864v1 bibliography, entry [302], read 2026-08-14

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as two standing-record ladders over time:

![Standing records for the C_6.44 and C_6.3 lower bounds over time.](cumulative-math-sums-autoconvolution.png)

## Method

`sums-autoconvolution-records.csv` is generated, not separately maintained.
The whole hand transcription lives in
[the AlphaEvolve record sequences](../math-alphaevolve-records/README.md),
whose [`fetch.py`](../math-alphaevolve-records/fetch.py) writes this slice
along with its own file, so the two cannot drift apart.
[`check.py`](check.py) recomputes the fact lines from this CSV and the
parent transcription.

[`figure.py`](figure.py) calls the shared `alphaevolve_value_chart()` shape
in [`../../lib/families.py`](../../lib/families.py), which filters
`sums-autoconvolution-records.csv` to those two `problem` values with a
non-empty `value` and `is_record` equal to `yes`, groups by problem, sorts
each group by `year` then `step`, and draws each as a grey step function
with markers coloured by author. `record_marker()` is the scoring rule: red
for any `agent` beginning `ai_`, which here means the four `ai_evolution`
rows, blue for `human_analytic` and `human_search`, and an unfilled marker
where `date_certain` is `no` — a case that does not arise on these two
ladders, so every marker here is filled. Three annotations are keyed to
`step` values and read "AlphaEvolve", "human retakes record", and
"AlphaEvolve" again. Legend labels are taken from the `quantity` column, so
they appear as the bare identifiers `C_6.44` and `C_6.3`. The two ladders
share one linear y-axis.

## Limitations

- **within-year order is lost.** The x-axis is the year: four steps share
  2007 and four share 2025 on $C_{6.44}$, so the chart cannot show which
  came first; the `step` column carries that order. The two 2025 human
  points at 1.17305 and 1.173077 are indistinguishable at this scale.
- **unrelated quantities on a shared axis.** The two ladders share one
  y-axis only because both constants lie near 1; the vertical distance
  between the two lines carries no information.
- **one step's provenance is incomplete in the CSV.** The reference for the
  1.173077 step did not parse from the source paper's bibliography during
  transcription, so the CSV records its authorship and year as unconfirmed;
  the paper's arXiv v1 HTML lists the cited entry as Fan Zheng,
  arXiv:2506.01896 (quoted above, read 2026-08-14).
- **relative gains are this repository's arithmetic** over consecutive
  values, not figures any source states; a percentage on a bound near 1 is
  not a measure of mathematical significance.
- **the AI steps are self-selected.** Both quantities entered this
  collection because an AI system was pointed at them, so the AI steps exist
  by construction and only the human steps are an unselected sample.
- **the largest AI step is stated as improvable.** The paper's authors state
  the 50,000-part construction can be pushed further with more parts (quoted
  above), so the recorded level is not stated as optimal.

## AI attribution

AlphaEvolve took two record steps on each ladder in 2025
[@novikov2025alphaevolve; @georgiev2025mathexploration]. On $C_{6.44}$ its
1.1479 and 1.1584 were overtaken in the same year by Gerbicz's 1.17305 — in
the paper titled as quoted above — and by the further 1.173077, by methods
the paper describes as closer to the original 2007 constructions. On
$C_{6.3}$ the sequence alternated: AlphaEvolve's 0.8962, Boyer and Li's
0.901564 by gradient methods, then AlphaEvolve's 0.961 from a 50,000-part
step function built after the Boyer–Li result. Tao's account of the
mathematics paper covers the wider run these two ladders sit in
[@tao2025exploration]; the dated precedent for AI-set records on recognised
open mathematical problems is FunSearch's cap-set improvement of December
2023 [@deepmind2023funsearch].

## Sources

- [@georgiev2025mathexploration] — the mathematics paper whose appendix the
  steps and prior bounds are transcribed from; quoted above, and the source
  of the Gerbicz and Zheng bibliography entries.
- [@novikov2025alphaevolve] — the AlphaEvolve system paper.
- [@deepmind2025problems] — the companion problem repository.
- [@tao2025exploration] — Tao's account of the mathematics paper.
- [@deepmind2023funsearch] — FunSearch, which in December 2023 improved the
  cap-set lower bound by evolving programs under an automated evaluator.
- The parent record series is
  [the finite-construction groups](../math-alphaevolve-records/README.md);
  century-scale series with no AI step are
  [analytic-number-theory exponents](../math-antedb/README.md) and
  [sphere packing](../math-sphere-packing/README.md).
