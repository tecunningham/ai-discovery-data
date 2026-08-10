# Sums-and-differences and autoconvolution constants

**Domain:** mathematics
**Metric:** best known lower bounds on two additive-combinatorics constants, $C_{6.44}$ and $C_{6.3}$ in the AlphaEvolve numbering
**Coverage:** 2007–2025, twelve record steps across the two ladders
**Data:** [`sums-autoconvolution-records.csv`](sums-autoconvolution-records.csv), the problem 6.44 and 6.3 rows of the AlphaEvolve record transcription
**Upstream:** <https://arxiv.org/abs/2506.13131> and the follow-on sources recorded per row in the CSV's `ref` and `note` columns
**Verdict:** inconclusive — AI steps are visible in 2025, and a human retook one of the two ladders within months

![Record lower bounds on the sums-and-differences and autoconvolution constants, with AI and human steps distinguished.](discovery-math-sums-autoconvolution.png)

## The problem

Two constants from the AlphaEvolve problem set, both bounded below by exhibiting a
finite object whose score can be computed exactly. For $C_{6.44}$, in sums and
differences of sets, the object is a set of integers: taking $U = \{0,1,3\}$ gives
$C_{6.44} \geq 1 + \log 67 / \log 7 \approx 1.0792$, and later records come from
larger sets found by search. For $C_{6.3}$, an autocorrelation inequality, the
object is a step function, and the recorded bracket at the start of the series is
$0.88922 \leq C_{6.3} \leq 1$.

A "discovery" here is a construction that moves one of those bounds. These two
ladders are in this collection for one reason: they are the quantities on which AI
and human record steps genuinely contested the same number, in both directions,
within months. That makes them the best available head-to-head on step size in
mathematics.

As instruments they inherit the selection problem of the whole AlphaEvolve set —
they are here because a system was pointed at them — and they have the compensating
virtue that the pre-AI ladder is dated and sourced. What they cannot do is measure
a rate: twelve steps clustered in two years, 2007 and 2025, is not a series with a
slope.

## What the chart shows

Two ladders sharing one axis. $C_{6.44}$ runs from 1.07921778 in 2007 through three
further 2007 steps to 1.14465, all by Gyarmati, Hennecart and Ruzsa and their
computer searches; then AlphaEvolve takes 1.1479 and 1.1584 in 2025; then two human
steps in the same year go above it, 1.17305 by Gerbicz and 1.173077 by a further
improvement, using methods closer to the original constructions. $C_{6.3}$ runs
from 0.88922 in 2010 to AlphaEvolve's 0.8962, then Boyer and Li's 0.901564 by
gradient methods, then AlphaEvolve's 0.961 from a step function of 50,000 parts,
built after seeing the Boyer–Li result.

The step sizes are the reading, and they are in the CSV's `relative_gain_pct`
column. On $C_{6.44}$ the two AI steps are +0.28% and +0.91%, against human steps
of +2.6%, +0.79% and +2.5% in 2007 and +1.26% and +0.002% in 2025. On $C_{6.3}$ AlphaEvolve's
two steps are +0.78% and +6.6% against the human +0.60%. The largest AI step in
either ladder is the one taken after seeing a competitor's method, and its authors
describe it as compute-bounded rather than idea-bounded: "We believe that with even
more parts, this lower bound can be further improved."

What the chart makes hard to read is the within-year order. All eight $C_{6.44}$
steps fall in just two years, and three of $C_{6.3}$'s four fall in 2025, so most
points stack vertically at two x positions, and the two 2025 human points at
1.17305 and 1.173077 are indistinguishable.

## How the chart was built

[`figure.py`](figure.py) calls the shared `alphaevolve_value_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), which filters
`sums-autoconvolution-records.csv` to those two `problem` values with a non-empty `value`
and `is_record` equal to `yes`, groups by problem, sorts each group by `year` then
`step`, and draws each as a grey step function with markers coloured by author.

`sums-autoconvolution-records.csv` is generated, not separately maintained. The
whole hand transcription lives in
[the AlphaEvolve record sequences](../math-alphaevolve-records/README.md), and
its [`fetch.py`](../math-alphaevolve-records/fetch.py) writes this slice along
with its own file, so the two cannot drift apart. Edit it there.

`record_marker()` is the scoring rule: red for any `agent` beginning `ai_`,
which here means the four `ai_evolution` rows, blue for `human_analytic` and
`human_search`, and an unfilled marker where `date_certain` is `no` — a case that
does not arise on these two ladders, so every marker here is filled. Three
annotations are keyed to `step` values and read "AlphaEvolve", "human retakes
record", and "AlphaEvolve" again. Legend labels are taken from the `quantity`
column, so they appear as the bare identifiers `C_6.44` and `C_6.3`.

The two ladders share one linear y-axis, which works only because both constants
happen to lie near 1. They are different quantities and the vertical distance
between the two lines means nothing.

## What it cannot support

- **The x-axis is the year, so within-year order is lost.** Four steps share 2007
  and four share 2025 on $C_{6.44}$, and the chart cannot show which came first;
  the `step` column carries that order.
- **The two ladders are unrelated quantities on a shared axis.** Nothing should be
  read from one line sitting above the other.
- **One step's provenance is incomplete.** The reference for the 1.173077 step did
  not parse from the source paper's bibliography, so its authorship and year are
  unconfirmed and its 2025 placement is the surrounding text's.
- **Relative gains are this repository's arithmetic** over consecutive values, not
  figures any source states, and a percentage on a bound near 1 is not a measure of
  mathematical significance.
- **The AI steps are self-selected.** Both quantities entered this collection
  because an AI system was pointed at them, so the AI step exists by construction
  and only the human steps are an unselected sample.
- **Compute-bounded steps are not a capability level.** The authors say the largest
  AI step could be pushed further with more parts, so where the record sits is a
  statement about who last spent compute.

## LLM contributions

AlphaEvolve took two steps on each ladder in 2025, and the human responses are what
make the sequences informative [@novikov2025alphaevolve]. On $C_{6.44}$ a human
overtook it within months, in a paper Gerbicz titled "Sums and differences of sets
(improvement over AlphaEvolve)", and a second human improvement followed by methods
closer to the 2007 constructions. On $C_{6.3}$ the two approaches leapfrogged:
AlphaEvolve's quick experiment, then Boyer and Li's gradient methods above it,
then — in the authors' account, having seen that result — AlphaEvolve's much larger
step to 0.961.

Set against the pooled step sizes assembled from the wider record frame, these are
ordinary: about +0.98% per AlphaEvolve step against +2.52% for human computer search
and +2.83% for human work by hand. The safe reading is that AI and human steps on
these quantities are the same order of magnitude, with the AI steps somewhat
smaller, and that insight-led human work overtook search-led AI work on the one
quantity where a real contest developed [@tao2025exploration].

## Related literature

The 2025 steps and the prior bounds they were measured against are in the
AlphaEvolve white paper [@novikov2025alphaevolve] and its companion problem
repository [@deepmind2025problems]; Tao's account of the mathematics paper is the
source for the wider pattern, including that rediscovery was the modal outcome and
improvement the exception, and that scoring functions had to use exact or interval
arithmetic because the system otherwise games the score
[@tao2025exploration]. The direct ancestor of this line of work is FunSearch, which
in December 2023 improved the cap-set lower bound by evolving programs under an
automated evaluator [@deepmind2023funsearch]. The other two record series from the
same frame are [kissing number](../math-kissing-11/README.md) and
[the finite-construction groups](../math-alphaevolve-records/README.md); the
century-scale series with no AI step are
[analytic-number-theory exponents](../math-antedb/README.md) and
[sphere packing](../math-sphere-packing/README.md).
