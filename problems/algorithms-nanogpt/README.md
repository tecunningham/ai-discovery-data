# modded-nanogpt training speedrun

- **Domain:** algorithms
- **Role:** discovery series
- **Metric:** minutes of training to a fixed target validation loss, per
accepted record
- **Coverage:** 2024-05-28 to 2026-08-30, all 92 records listed in the
repository README, read 2026-10-05; open pull requests claiming a faster time
as of 2026-09-28
- **Data:** [`nanogpt-records.csv`](nanogpt-records.csv)
- **Upstream:** <https://github.com/KellerJordan/modded-nanogpt> (record table
in the README at
<https://github.com/KellerJordan/modded-nanogpt/blob/master/README.md>)
- **Verdict:** accelerating — the standing record fell 2.8× in 2026 (36
records through 2026-08-30) against 1.9× in 2025 (39 records) and 12.6× in
2024 (17 records)

![All 92 modded-nanogpt records on a log time axis, with the five AI-credited records in red, the three AI-assisted records in pale red, and the post-record-21 re-timings marked.](discovery-algorithms-nanogpt.png)

## Definition

modded-nanogpt is a public competition to train a GPT-2-scale language model
to a fixed target validation loss in as little wall-clock time as possible.
The target is fixed by the rules, so a record is the same capability reached
with less compute — an efficiency series rather than a capability series —
and an AI-set record is directly comparable with a human one.

A "discovery" is one record accepted into the README's table, dated and
credited to a named entrant. Every record carries a day-precise date and an
author, which is what allows the AI share to be counted rather than
estimated. The fixed-hardware assumption comes from the leaderboard's own
rules; the vendored CSV carries only the record number, date, minutes, agent,
credited AI system, and a note, so nothing in the data itself pins the
machine.

## Facts

- **span:** 45.0 minutes at the llm.c baseline of 2024-05-28, down to 0.665
  minutes at record 92 on 2026-08-30 — a reduction of about 68 times
- **records per period:** 17 records in 2024, 39 in 2025, and 36 in 2026
  through 2026-08-30
- **standing-record falls:** over the same three periods the standing record
  fell by a factor of 12.6, then 1.9, then 2.8
- **ai-records:** 5 records out of 92: record 32 to hiverge.ai at 2.625
  minutes (2025-09-11), record 60 to Locus at 1.765 (2026-01-16), record 69
  to Aster at 1.528 (2026-02-02), record 72 to Station at 1.496
  (2026-02-10), and record 87 to Recursive at 1.256 (2026-06-11)
- **ai-step-sizes:** measured against the record each displaced, the five AI
  steps are 1.2%, 0.9%, 0.5%, 1.3% and 0.8% — this repository's arithmetic
  over the vendored series, not figures the README prints
- **ai-assisted records:** record 82 at 1.353 minutes (2026-04-29) with
  Claude Opus 4.7; record 91 at 1.126 minutes (2026-08-06) with Claude Opus
  5; record 92 at 0.665 minutes (2026-08-30) with Claude Fable 5 — the first
  two read from a `Co-authored-by` trailer on the record's merge commit, the
  third from its author, none from the README table
- **largest 2026 step:** record 92 at 0.665 minutes, 41% below record 91's
  1.126, from a sampled-softmax training loss, an 84.6M-row hashed n-gram
  embedding table and full-stack FP8
- **deep human steps (README figures):** the Muon optimizer at about 21% and
  U-Net skip connections at about 8%
- **pending:** 1 open pull request claiming a time below the standing record
  with the evidence the rules ask for: #367 at 0.359 minutes, opened
  2026-09-17 — a claim, not a record, until the maintainer accepts it into
  the table
- **unvetted claims:** none

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as the standing record's value over time:

![Standing record for training minutes over time.](cumulative-algorithms-nanogpt.png)

## Method

The record rows are transcribed by hand, since attributing a record needs
judgment the README states only in prose. For those, [`fetch.py`](fetch.py)
is a staleness probe rather than a fetcher: it reads the upstream README and
reports if a record past the vendored series has been accepted. Open claims
it does write: every open Track 1 pull request whose title claims a time —
in minutes or seconds — below the standing record, opened on or before the
snapshot date, becomes a row whose `record` is `PR<number>`, whose `date` is
the day the request was opened and whose `agent` and `ai_system` are empty,
since attribution waits for acceptance. A claim that is merged becomes a
transcribed record row; one that is closed drops out at the next run.

Which kind of row a claim becomes follows the leaderboard's own acceptance
rules, read from the files the pull request adds. It is `kind=pending` if a
statistics file states p < 0.01 that mean validation loss is at most 3.28,
the runs are on 8xH100, its baseline file names a merged record rather than
another open pull request, and no reviewer's latest review requests changes;
otherwise it is `kind=claim`, with the tests it failed in `note`. The size of
the claimed step is deliberately not a test, since record 92 cut the time by
41% and was accepted. Neither kind enters a fact line other than **pending**
and **unvetted claims**, or any figure in this folder; the collection's
cumulative comparison page draws the pending rows on request as a tentative
extension of the standing-record line.
[`check.py`](check.py) recomputes the fact lines above from the CSV.

[`figure.py`](figure.py) reads `nanogpt-records.csv`, converts each `date` to
a year fraction, and draws `minutes` as a step function through all 92 rows
with `kind=record`. Each record is a point coloured by the `agent` column,
red where it is `ai`, pale red where it is `ai_assisted` and blue where it is
`human`, with the AI points drawn larger and labelled from the `ai_system`
column. The y axis is logarithmic, with ticks set explicitly at 0.7, 1, 1.5,
2, 3, 5, 10, 20 and 45; a linear axis would
compress the whole 2025–2026 stretch into the bottom of the frame. January
2026 onward is shaded, as in every figure here.

One discontinuity in the series has a documented cause. Records 22 to 24, in
May 2025, are slower than record 21 of January 2025 as printed in the
README's own table, because the leaderboard changed how it times a run after
record 21: ten formerly untimed warmup steps became timed, worth about 850ms,
and `torch._inductor.config.coordinate_descent_tuning` was banned, worth
about three seconds. Upstream re-timed record 21 under the new rules at 2.997
minutes and again on the then-current torch at 3.014. Against 3.014, records
22 to 24 at 2.990, 2.979 and 2.966 are improvements rather than a regression.
Both re-timings are vendored as `kind=retiming` rows and drawn as open
markers. Apart from the two re-timings, nothing is plotted with an open
marker on this series, because every record row carries a firm date and an
acknowledged holder.

## Limitations

- **a leaderboard measures what people chose to optimize.** Ninety-two
  records on one training task say nothing about the value of the
  improvement, or about how much of it transfers to a model anybody ships.
- **the AI share is a floor.** The `agent` column reflects the README's own
  labels, the co-author trailers on each record's merge commit and, for
  record 92, its author's account, so a record set with undisclosed model
  assistance counts as human.
- **the step sizes are this repository's arithmetic.** The README prints
  standing times, not per-record deltas; only the Muon and U-Net figures
  come from the source log.
- **nothing separates better ideas from more attention.** There is no
  denominator of effort, spend, or attempts, so a faster cadence cannot be
  split into better tools and more entrants.
- **approaching a floor is not the same as exhausting ideas.** Time to a
  fixed loss has a hard lower bound, so flattening is the expected shape
  late in any speedrun.

## AI attribution

Five of the 92 records are credited to AI-agent companies: hiverge.ai,
Locus, Aster, Station and Recursive, at the dates and times listed in the
fact lines above, each measuring roughly one percent against the record it
displaced. The README's entry for record 60 (Locus) is an explicit fused
Triton kernel [@kellerjordan2026moddednanogpt], and the CSV note for record
87 records a faster ReLU^2 kernel "credited to @cong_ml and AI System
Recursive". hiverge.ai also holds the first acknowledged AI record on the
[CIFAR-10 speedrun](../algorithms-cifar10/README.md), so the AI-set records
on the two ML speedruns partly belong to the same small set of firms. No
other record in the CSV carries an `agent` value of `ai`.

Three more are `ai_assisted`: entries by named people who worked with a
model. Record 82 (learnable XSA gated layers, PR #264) carries
`Co-authored-by: Claude Opus 4.7` on its merge commit, and record 91
(canonical token masking, PR #350) carries `Co-authored-by: Claude Opus 5`.
Record 92 (ANVIL2, PR #360), the largest step of 2026, names no model in its
own commit — the Claude Opus 5 trailer on its merge commit came in with PR
#350's commits — but its author reports having built it with Claude Fable 5
(personal communication to this repository's maintainer, 2026-10-05). It is
the one attribution here not readable from the public record.

Two adjacent results are AI-credited off this leaderboard. TTT-Discover's
test-time-training harness, running the open gpt-oss-120b model, found TriMul
GPU kernels 15 to 51% faster than the best human submission depending on GPU
type [@yuksekgonul2026learning]. Karpathy left an agent tuning nanochat for
about two days in March 2026; it worked through roughly 700 changes, about 20
of which improved validation loss, after which Karpathy himself tested,
transferred and stacked them and measured an 11% cut in time to GPT-2
[@karpathy2026autoresearch].

## Sources

- [@kellerjordan2026moddednanogpt] — the leaderboard README: the record
  table every row is transcribed from, and the Muon and U-Net step figures.
- [@yuksekgonul2026learning] — the TTT-Discover kernel result in the
  AI-attribution register.
- [@karpathy2026autoresearch] — Karpathy's self-reported nanochat tuning run
  in the AI-attribution register.
- [@epoch2026driver] — Epoch AI's stated estimate of the labs' own
  unpublished training-efficiency curve: about 10 times a year inside an 80%
  interval of 2 to 50 times.
- [@sherry2021fast] — the published base rate across 113 algorithm families:
  half never improve at all, while 14% improve more than a thousandfold per
  year.
- Sibling series: the [CIFAR-10 speedrun](../algorithms-cifar10/README.md)
  measures seconds to a fixed test accuracy on the same kind of fixed-target
  training task.
