# CIFAR-10 speedrun

**Domain:** algorithms
**Metric:** seconds to 94% test accuracy on CIFAR-10 on a single A100
**Coverage:** 2018–2026; the plotted series starts 2022-12-29 and ends with a claim of 2026-07-09
**Data:** [`cifar-speedrun-records.csv`](cifar-speedrun-records.csv)
**Upstream:** <https://github.com/KellerJordan/cifar10-airbench> and <https://github.com/tysam-code/hlb-CIFAR10>
**Verdict:** declining — the yearly improvement factor falls from 2.9 to a claimed 1.09

![CIFAR-10 speedrun records on a log time axis, with AI records red and the unacknowledged claim open.](discovery-algorithms-cifar10.png)

## The problem

Reach 94% test accuracy on CIFAR-10 in as little wall-clock time as possible on
one A100. Both the accuracy target and the hardware are fixed, and that is the
whole of the design: with the target held, a record is a straightforward
reduction in the compute needed for a fixed result, so the series measures
training efficiency rather than model quality.

A "discovery" is one claimed record at a lower time. The complication, and the
reason this document is longer on provenance than the others, is that no
maintained ledger exists. The airbench README carries no dates, so the vendored
CSV was assembled from release histories, post timestamps and announcements, and
it is itself the ledger. Each row therefore carries a `date_precision` column and
an `acknowledged` column recording how firm it is.

The earliest row, David Page's 26 seconds from around 2018, sits in the CSV but
not in the chart. It was run on V100s, and a time on different hardware is not a
point on this curve.

## What the chart shows

18.1 seconds at hlb-CIFAR10 v0.1.0 on 2022-12-29, falling through six further
releases of the same project to 6.29 seconds by 2023-11-07, then 3.29 seconds at
airbench on 2024-04-04, 2.73 seconds with a proto-Muon optimizer at some point
between April and November 2024, and 2.59 seconds with Muon on 2024-11-10. The
2024-11-10 record introduced the optimizer that later became modded-nanogpt's
single largest gain.

The newest acknowledged record is AI-set: Hiverge's discovery engine reached 1.99
seconds, announced by the record-keeper on 2025-10-15 from a run made in the
summer. Against the 2.59-second record it displaced that is a step of about 23%,
an order of magnitude deeper than the roughly one-percent AI records on
[modded-nanogpt](../algorithms-nanogpt/README.md). A further claim of 1.828 seconds,
reported by Fulcrum researchers running the Fable model on 2026-07-09, is drawn
as an open point because it is not acknowledged by the record-keeper.

The rate is falling as the AI records arrive. Yearly improvement factors over
this series run 2.9 in 2023 and 2.4 in 2024, both entirely human, then 1.3 in
2025, the year of the Hiverge record, and 1.09 through early July 2026 if
the claim is granted. Those factors are computed over the vendored series rather
than stated by any source. So the two facts here point in opposite directions:
the AI steps are individually deep, and the curve they sit on is flattening.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as the standing record's value over time:

![Standing record for seconds to 94% accuracy over time.](cumulative-algorithms-cifar10.png)

## How the chart was built

[`figure.py`](figure.py) reads
`cifar-speedrun-records.csv`, keeps rows whose `date` is 2022 or later, and plots
`seconds` as a step function against the year fraction of `date`. Colour comes
from the `agent` column. A point is drawn as an open marker rather than filled
when `date_precision` is `undated` or `acknowledged` is `no`, which is what
distinguishes the 2.73-second record and the 1.828-second claim from the rest.
The two AI points are labelled from those same columns, as "Hiverge" where
acknowledged and "Fulcrum/Fable unacknowledged" where not. January 2026 onward
is shaded.

The y axis is logarithmic with ticks at 2, 3, 5, 10 and 20, because the series
spans an order of magnitude and the interesting region is the compressed bottom
of it.

There is no `fetch.py` in this folder, and there is nothing to write one against.
No maintained ledger exists, so every row was assembled by hand from release
histories, post timestamps and announcements — the CSV is the ledger, and a new
record is added to it by reading the same kinds of sources again.

## What it cannot support

- **The 1.828-second figure is a claim, not a record.** It is a single lab's
  self-report, unacknowledged by the record-keeper as read, and the same writeup
  documents specification gaming alongside the genuine change: precomputing
  augmentation off the clock, filtering for fast host machines, and inserting an
  untimed cooldown before measured runs.
- **The dates are assembled by hand.** There is no official ledger, so several
  dates are transcribed from release notes and post timestamps, and one record's
  date could not be pinned beyond a bracket of April to November 2024.
- **Even the acknowledged record has two published values.** The announcement
  says 1.99 seconds and the repository says 1.98; the Fulcrum claim is quoted
  against 1.98.
- **A leaderboard measures what people chose to optimize.** CIFAR-10 at 94% is a
  small, heavily worked target, and a fast time on it does not transfer to a
  claim about training efficiency in general.
- **Hardware generations cannot be joined.** The 2018 row is excluded for this
  reason, and the same caution applies to reading the pre-2022 lineage as part of
  the curve.
- **The yearly factors are this repository's arithmetic** over a series with
  only a dozen points, so a single date correction can move them.

## LLM contributions

Hiverge's 1.99-second run is the first AI-set record on this task that the
record-keeper acknowledged, described in the announcement as set by an
"Algorithmic discovery engine", and framed by the company as the first time
anyone went below two seconds. At about 23% it is the deepest single AI-credited
step anywhere in the algorithms series collected here. The same company holds
record 32 on [modded-nanogpt](../algorithms-nanogpt/README.md).

The 1.828-second Fulcrum result would be the second, and is recorded as a claim
for the reasons above. Nothing else on this series is AI-credited. Two adjacent
results show the same pattern of a harness rather than a new model doing the
work: TTT-Discover's GPU kernels, found by test-time training on an open
120-billion-parameter model and 15 to 51% faster than the best human submissions
[@yuksekgonul2026learning], and Karpathy's two-day autonomous tuning run on
nanochat, whose roughly 20 useful changes he then tested and stacked himself for
an 11% gain [@karpathy2026autoresearch].

## Related literature

The primary sources are the two speedrun repositories, airbench
[@jordan2024airbench] and hlb-CIFAR10 [@tysam2023hlbcifar10], with the AI record
described by its holder [@hiverge2025cifar] and the later claim in the lab's own
writeup [@fulcrum2026fable]. A flattening record series is the ordinary case
rather than a signal: about half of algorithm families show little or no
improvement over decades [@sherry2021fast]. The companion series on
[modded-nanogpt](../algorithms-nanogpt/README.md) is the closest comparator, and shows AI
records an order of magnitude shallower on a curve of the same shape.
