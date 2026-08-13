# Finite construction records around AlphaEvolve

**Domain:** mathematics
**Metric:** cumulative record steps in five groups of finite construction and packing problems
**Coverage:** 1949–2026, 22 record steps across the five groups
**Data:** [`alphaevolve-records.csv`](alphaevolve-records.csv), with the sampling frame in [`../math-alphaevolve-inventory/alphaevolve-inventory.csv`](../math-alphaevolve-inventory/alphaevolve-inventory.csv)
**Upstream:** <https://github.com/google-deepmind/alphaevolve_repository_of_problems> and <https://arxiv.org/abs/2511.02864>, with per-step sources recorded in the CSV's `ref` and `note` columns
**Verdict:** inconclusive — the 2025 cluster is real, but these five groups were selected because an AI system worked on them

![Cumulative record steps in five finite construction and packing problem groups, with AI steps in red.](discovery-math-alphaevolve-related-records.png)

## The problem

Five groups of finite problems from the AlphaEvolve problem set, each with a
standing record held by an explicit construction: the Erdős minimum-overlap type
constant (6.5), the difference-basis constant (6.7), Heilbronn-style triangle
packing (6.48) and convex packing (6.49), and a max-min packing ratio (6.50).

They belong together because they share a shape rather than a subject. In each
case the record is a finite object — a step function, a difference set, a packing
of $n$ shapes — that can be scored exactly, and the incumbent record often lives on
a community page maintained by continuous computer search rather than in a journal.
A "discovery" in this series is one such record being improved.

The instrument is deliberately weak in one direction and useful in another. It
cannot measure a discovery rate, because these five groups exist in the data
precisely because an AI system was pointed at them: the 2025 cluster is guaranteed
by construction. What it can do is show what an AI record step looks like next to
the human steps on the same quantity, and how much of the human baseline is itself
machine search.

The frame is worth naming, because it is what stops the selection from being
arbitrary. `alphaevolve-inventory.csv` covers the 65 problems the paper numbers,
of which the companion repository's own classification marks 19 as ones where
AlphaEvolve holds the record, 11 where it matched a known optimum, 8 where it came
in below the record, 4 where its result has since been surpassed, and 23
unclassified. The 31 in the first, third and fourth groups are the ones with a live
numeric record, and these five come from there.

## What the chart shows

Twenty-two record steps, of which seven are AI-set and all seven fall in 2025. By
group: minimum-overlap has five steps from 1955 to 2025, difference basis four from
1949 to 2025, triangle packing two (2006 and 2025), convex packing four (two
Cantrell constructions in 2007 and two AlphaEvolve improvements in 2025), and
max-min packing seven (two Cantrell constructions in 2009, two AlphaEvolve steps
and two solver steps in 2025, and one human step in 2026).

The AI step sizes, from the CSV's `relative_gain_pct`, are mostly tiny: +1.44% on
triangle packing, +0.98% and +0.47% on convex packing, +0.69% on difference basis,
+0.052% and +0.0057% on the two max-min slices, and +0.00075% on minimum-overlap.
The last of those is the fourth-decimal-place nudge that secondary coverage of the
paper described, moving the Erdős minimum-overlap upper bound from roughly 0.380927
to 0.380924.

Two features of the 2025 column cut the reading down, and both are in the data. The
difference-basis record had stood since Golay in 1972, which is the oldest record
with an AI step anywhere in this collection — but the paper reports the system was
not able to beat it unaided, and the improvement came only after it was given
working Singer difference-set code, which is what the chart's callout says. And both
max-min records fell within a month to FICO's Xpress global solver, run by its own
account with no custom algorithm and verified with the vendor's own tool. A record an
unmodified commercial solver retakes in weeks says more about how contested the
quantity was than about discovery.

![Three contested record sequences, and the pooled distribution of step sizes by who made each step.](alphaevolve-record-steps.png)

The second figure covers the whole file rather than the five groups. Its left
three panels plot the best known value against record step, not against year,
because several steps share a year: problem 6.44's sums-and-differences bound
over eight steps, problem 6.3's autoconvolution constant over four, and problem
6.8's kissing number in dimension 11 over five. Marker colour is who made the
step — AlphaEvolve, AI-guided search, an agent platform, human computer search,
human work by hand, or a community records page — and each point is annotated
with its year. The right panel pools every record step in the file that has a
computable size and an `is_record` of `yes`, one row per kind of agent on a
symmetric log axis, with a vertical bar at each row's median and the median
printed above it.

## How the chart was built

[`figure.py`](figure.py) draws both figures from `alphaevolve-records.csv`. For
the first it holds the five problem ids
in a hardcoded `selected` set, keeps rows with a non-empty `year` and `is_record`
equal to `yes`, groups by `problem`, sorts each group by `year` then `quantity`
then `step`, and plots the cumulative step count per group. The group labels in the
legend are hardcoded in the function, not read from the data.

The y-axis is a count because the values are not commensurable: an area, a squared
radius, and two dimensionless constants cannot share a numeric axis. So this figure
plots discoveries rather than levels, the same choice the
[sphere-packing ladder](../math-sphere-packing/README.md) makes for the same reason.

Step markers are colour-coded by who set them. `record_marker()` reads `agent`,
draws red for anything beginning `ai_` and blue otherwise, and draws an unfilled
marker where `date_certain` is `no`. Note that the FICO solver steps and the 2026
step are blue: the coding distinguishes AI from non-AI rather than automated from
manual, and much of the blue here is computer search.

Two rows in the same CSV are flagged `is_record: no` and are therefore excluded
from figures, including this one. Both are spherical-design constructions the paper
described as improving on the literature bounds it cited, where a 2016 result the
paper does not cite was already better. They are worth knowing about when reading
any record claim from this source, even though they are not in this group.

The CSV is built by [`fetch.py`](fetch.py), which carries the hand transcription
itself: the values, the quoted sentence each was read from, the reference, and
the agent coding are all literals in that file, and the relative gains are
computed from consecutive values as it writes. It is the only place any of these
records is maintained, and it also writes the slice that
[sums and autoconvolution](../math-sums-autoconvolution/README.md) plots, so
that child dataset cannot drift from the file it is drawn out of.

This folder keeps the full transcription rather than a slice of it because
`alphaevolve-record-steps.png` pools every record step in the frame, across all
the problems the paper numbers, not only the five plotted in the first figure.

## What it cannot support

- **The groups are selected because an AI system worked on them.** The 2025 cluster
  is an artifact of that selection, so nothing about a rate can be read from it.
- **The axis counts steps, not sizes**, and the AI steps are among the smallest in
  the series, several in the fourth or fifth decimal place.
- **A group's step count mixes quantities.** Convex packing pools $n=13$ and
  $n=14$, and max-min pools two slices, so a group reaching seven steps is not one
  record improving seven times.
- **Points from different groups land on the same coordinates.** Two groups both
  take their second step in 1956, and the minimum-overlap one — whose date rests on
  secondary sources only, and which is therefore drawn as an open marker — is hidden
  underneath the other group's filled marker.
- **The human baseline is itself continuous computer search.** Several incumbent
  records come from Erich Friedman's packing pages, whose "+" convention truncates
  values and so slightly understates prior records and overstates AI gains; one page
  now shows AlphaEvolve's value for the $n=13$ convex case while still crediting
  Cantrell in 2007, so page and paper disagree about who holds it.
- **One value is missing.** The 2026 max-min step has an empty `value`, because the
  community page truncates the figure and the exact number could not be established;
  the step is counted, the level is not recorded.
- **The deepest-looking result was hint-dependent.** The 53-year difference-basis
  record and the supplied Singer-code hint belong in the same sentence.

## LLM contributions

Seven of the twenty-two steps, all AlphaEvolve, all in 2025
[@novikov2025alphaevolve; @deepmind2025problems]. Their sizes run from +1.44% down
to +0.00075%, and their durability varies: two were retaken within a month by an
off-the-shelf commercial solver, and one was set only after the system was handed
the key construction as code.

That mixture is the honest summary of what this part of mathematics has received —
real improvements on genuinely standing records, concentrated on problems where a
candidate can be scored exactly, mostly small, and in several cases matched or
beaten quickly by conventional search. The wider assessment from the same source
agrees: rediscovery of known solutions was the modal outcome across the problem
set and improvement the exception, and on named conjectures the system located the
already-known extremal candidates and nothing beyond them
[@tao2025exploration]. The line of work began with FunSearch's cap-set improvement
in December 2023, which is where the era of AI-set mathematical records should be
dated from [@deepmind2023funsearch].

## Related literature

The 2025 steps and the bounds they were measured against come from the
mathematics paper's appendix [@georgiev2025mathexploration], with the AlphaEvolve
white paper and its companion repository supplying the status
classification used as the frame here [@novikov2025alphaevolve;
@deepmind2025problems]. Tao's account of the mathematics paper is the source for
the modal-rediscovery finding, for the verifier-gaming caveat, and for the observation
that the method needs a computable objective rather than an easier problem
[@tao2025exploration]. FunSearch is the ancestor [@deepmind2023funsearch]. That a
benchmark can compare AI output to the current record while carrying no historical
dimension at all — which is the gap this series exists to fill — is visible in the
design of HorizonMath [@arxiv2026horizonmath]. That records in any field arrive in
bursts with long gaps, so a cluster is not by itself a signature, is Sherry and
Thompson's [@sherry2021fast]. The individually plotted child series from the same
frame is [sums and autoconvolution](../math-sums-autoconvolution/README.md).
