# modded-nanogpt training speedrun

**Domain:** algorithms
**Metric:** minutes of training to a fixed target validation loss, per accepted record
**Coverage:** 2024-05-28 to 2026-07-17, all 89 records listed in the repository README
**Data:** [`nanogpt-records.csv`](nanogpt-records.csv)
**Upstream:** <https://github.com/KellerJordan/modded-nanogpt> (record table in the README at <https://github.com/KellerJordan/modded-nanogpt/blob/master/README.md>)
**Verdict:** no acceleration

![All 89 modded-nanogpt records on a log time axis, with the five AI-credited records in red and the post-record-21 re-timings marked.](discovery-algorithms-nanogpt.png)

## The problem

A public competition to train a GPT-2-scale language model to a fixed target
validation loss in as little wall-clock time as possible. The target is fixed by
the rules, so a record is not a better model: it is the same capability reached
with less compute. That is what makes the series an efficiency curve rather than
a capability curve, and it is why an AI-set record here is directly comparable
with a human one.

A "discovery" is one record accepted into the README's table, dated and credited
to a named entrant. The ledger is unusually good for this collection — every
record carries a day-precise date and an author, which is what allows the AI
share to be counted rather than estimated.

The fixed-hardware assumption comes from the leaderboard's own rules. The
vendored CSV carries only the record number, date, minutes, agent, credited AI
system, and a note, so nothing in the data itself pins the machine.

## What the chart shows

45.0 minutes at the llm.c baseline of 2024-05-28, down to 1.23 minutes at
record 89 on 2026-07-17 — a reduction of about 37 times in a little over two
years. Five of the 89 records are credited to AI-agent companies: record 32 to
hiverge.ai at 2.625 minutes (2025-09-11), record 60 to Locus at 1.765
(2026-01-16), record 69 to Aster at 1.528 (2026-02-02), record 72 to Station at
1.496 (2026-02-10), and record 87 to Recursive at 1.256 (2026-06-11).

The AI records are real and small. Measuring each against the record it
displaced gives 1.2%, 0.9%, 0.5%, 1.3% and 0.8% — this repository's arithmetic
over the vendored series, not figures the README prints. The deep gains are human:
the Muon optimizer at about 21% and U-Net skip connections at about 8%.

Records arrive faster in the agent era while each one buys less: 17 records in
2024, 39 in 2025, and 33 in the first seven months of 2026. Over the same three
periods the standing record fell by a factor of 12.6, then 1.9, then 1.5. So the
flat tail is where the AI records sit, and the series does not bend upward when
they arrive.

One wrinkle in the fine structure has a documented cause. Records 22 to 24, in
May 2025, are slower than record 21 of January 2025 as printed in the README's
own table, because the leaderboard changed how it times a run after record 21:
ten formerly untimed warmup steps became timed, worth about 850ms, and
`torch._inductor.config.coordinate_descent_tuning` was banned, worth about
three seconds. Upstream re-timed record 21 under the new rules at 2.997 minutes
and again on the then-current torch at 3.014. Against 3.014, records 22 to 24
at 2.990, 2.979 and 2.966 are genuine improvements, not a regression. Both
re-timings are vendored as `kind=retiming` rows and drawn as open markers, so
the discontinuity is visible rather than inferred.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as the standing record's value over time:

![Standing record for training minutes over time.](cumulative-algorithms-nanogpt.png)

## How the chart was built

[`figure.py`](figure.py)
reads `nanogpt-records.csv`, converts each `date` to a year fraction, and draws
`minutes` as a step function through all 89 rows with `kind=record`. Each record is a point
coloured by the `agent` column, red where it is `ai` and blue where it is
`human`, with the AI points drawn larger and labelled from the `ai_system`
column. January 2026 onward is shaded, as in every figure here.

The y axis is logarithmic, with ticks set explicitly at 1.5, 2, 3, 5, 10, 20 and
45. A linear axis would compress the whole 2025–2026 stretch into the bottom of
the frame, which is exactly the region the slope question is about. Apart from
the two re-timings, nothing is plotted with an open marker on this series,
because every record row carries a firm date and an acknowledged holder.

The rows are transcribed by hand, since attributing a record needs judgment the
README states only in prose. [`fetch.py`](fetch.py) is therefore a staleness probe
rather than a fetcher: it reads the upstream README and reports if a record past
the vendored series has been accepted.

## What it cannot support

- **A leaderboard measures what people chose to optimize.** Eighty-nine records
  on one training task say nothing about the value of the improvement, or about
  how much of it transfers to a model anybody ships.
- **The AI share is a floor.** The `agent` column reflects the README's own
  labels, so a record set with undisclosed model assistance counts as human.
- **The step sizes are this repository's arithmetic.** The README prints
  standing times, not per-record deltas. Only the Muon and U-Net figures come
  from the source log; the five AI step sizes are computed here.
- **Nothing separates better ideas from more attention.** There is no denominator
  of effort, spend, or attempts, so a faster cadence in 2026 cannot be split
  into better tools and more entrants.
- **Approaching a floor is not the same as exhausting ideas.** Time to a fixed
  loss has a hard lower bound, so flattening is the expected shape late in any
  speedrun and is not by itself evidence about the supply of discoveries.

## LLM contributions

Five records out of 89, held by hiverge.ai, Locus, Aster, Station and
Recursive, each worth
roughly one percent. Where the content of an AI record is described it is
mechanical rather than conceptual: Locus's entry is an explicit fused Triton
kernel, which is kernel fusion rather than a new idea. Hiverge also holds the
first acknowledged AI record on the [CIFAR-10 speedrun](../algorithms-cifar10/README.md),
so the AI-set records on the two ML speedruns are partly the same small set of
firms.

Two adjacent results bear on this series without appearing on it. TTT-Discover's
test-time-training harness, running the open gpt-oss-120b model, found TriMul
GPU kernels 15 to 51% faster than the best human submission depending on GPU
type [@yuksekgonul2026learning]. And Karpathy left an agent tuning nanochat for
about two days in March 2026; it worked through roughly 700 changes, about 20 of
which improved validation loss, after which Karpathy himself tested, transferred
and stacked them and measured an 11% cut in time to GPT-2. Both are the same
kind of work this leaderboard rewards, done off it.

## Related literature

The lumpiness here is the field's normal shape: half of all algorithm families
never improve at all, while 14% improve more than a thousandfold per year
[@sherry2021fast]. The leaderboard itself is the primary record
[@kellerjordan2026moddednanogpt], and the two off-leaderboard demonstrations are
TTT-Discover [@yuksekgonul2026learning] and Karpathy's autoresearch run
[@karpathy2026autoresearch]. The curve this series is a proxy for — the labs'
own training efficiency — is not published; Epoch's best guess is about 10 times
a year inside an 80% interval of 2 to 50 times [@epoch2026driver], which is too
wide to show a bend.
