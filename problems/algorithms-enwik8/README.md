# Hutter Prize compression: enwik8

**Domain:** algorithms
**Metric:** total size in bytes of decompressor plus archive for a fixed 100 MB text corpus, under a CPU-time and memory cap
**Coverage:** 2006-03-24 baseline to the last awarded record on 2017-11-04; retired when the prize moved to enwik9 in February 2020
**Data:** [`enwik8-records.csv`](enwik8-records.csv)
**Upstream:** <http://prize.hutter1.net/>
**Verdict:** baseline — a pre-agent record cadence for comparison, not a test of recent acceleration

![The four awarded enwik8 Hutter Prize records from 2006 to 2017, ending before the agent era.](discovery-algorithms-enwik8.png)

## The problem

The original form of the Hutter Prize: compress the first 10^8 bytes of a fixed
XML dump of English Wikipedia, scored on the compressed size including the
decompression program, under the same resource cap the prize still applies —
about fifty hours on a single CPU core, under 10 GB of RAM, under 100 GB of disk.
In February 2020 the prize expanded its corpus tenfold and this series stopped;
the live version is the [enwik9 series](../algorithms-enwik9/README.md).

Everything about the task is fixed: one frozen corpus, one scoring rule, one
resource cap, and one administrator applying them for eleven years. That is what
makes it worth keeping after it stopped moving. This series exists here as a
comparator, and the question it answers is not whether AI accelerated anything —
it ends nine years before the agent era — but what the record cadence on a live,
cash-rewarded, fixed compression task looks like with no AI anywhere in it.

A "discovery" is an awarded record, meaning one that cleared the prize's minimum
improvement and was paid.

## What the chart shows

Four awarded records over eleven years, all by one person. The 2006 baseline is
paq8f -7 by Matt Mahoney at 18,324,887 bytes; then paq8hp5 -7 on 2006-09-25,
paq8hp12 -7 on 2007-05-14, decomp8 on 2009-05-23, and phda9 on 2017-11-04 at
15,284,944 bytes, every one of them by Alexander Rhatushnyak. Computing the steps
over the vendored series gives 6.83%, 3.46%, 3.23% and 4.17%, for a total
reduction of 16.6%.

The most useful feature is the gap. Between the third awarded record in May 2009
and the fourth in November 2017 nothing was awarded for eight and a half years,
on a task with standing prize money, a fixed target, and public scoring. Then a
record arrived. A long flat stretch followed by a step is the ordinary shape
here, which is the reason to be careful reading any single quiet period in the
agent-era series as an exhausted frontier, and any single step inside it as an AI
effect.

The steps on this series are also two to four times larger than the 1.0 to 1.6%
steps on enwik9. That is consistent with an earlier and less picked-over point on
the same kind of curve, or with a different hurdle in the prize rules of the time,
and nothing in the vendored data distinguishes the two explanations.

## How the chart was built

The same generator as its successor: [`figure.py`](figure.py) calls
`compression_chart()` in [`../../lib/families.py`](../../lib/families.py), which
reads `enwik8-records.csv`, keeps the rows whose `series` column is
`hutter_enwik8`, and plots `total_bytes` divided by 10^6 against the year fraction
of `date` as a step function in megabytes on a linear axis. No row in this series
has `award` set to `pending`, so no open markers are drawn, and the dashed
uncapped comparator is not drawn either: that branch of the function is keyed to
the enwik9 series, because the Large Text Compression Benchmark measured the 1 GB
corpus and its rows sit in that folder. The legend still carries the collection's shared key,
including the open "pending or uncertain" handle it does not use here, so that a
reader moving between figures reads one visual language.

January 2026 onward is shaded, as in every figure here. On this series the shaded
band contains no data, which is the honest picture of a series that ended before
the period under test.

There is no `fetch.py` in this folder. The rows were transcribed by hand, and the
prize page now carries only the live enwik9 records, so there is nothing upstream
left to probe: the [enwik9 folder](../algorithms-enwik9/README.md) holds the
staleness check for the series that is still moving.

## What it cannot support

- **There is no LLM contribution to look for.** The last record predates the
  agent era by nine years, so this series can neither support nor contradict a
  claim about AI, and its only role is as a cadence comparator.
- **Four records by one person is one searcher's cadence.** Rhatushnyak holds
  every awarded record here, so the gaps between them may reflect one
  individual's attention rather than the difficulty of the problem.
- **enwik8 and enwik9 cannot be joined into one curve.** They are different
  corpora with different totals, and the prize switched between them; the two
  series share a document family and a generator, not an axis.
- **The step sizes are this repository's arithmetic** over the vendored byte
  counts, and are not percentages the prize site prints.
- **The rows were transcribed by hand.** The upstream is a prose page with an HTML
  table, read over plain HTTP because its TLS certificate has expired, and typed
  into the CSV.
- **A retired series cannot show whether the task got harder or the searchers
  left.** The prize moved the goalposts in 2020, so the absence of records after
  2017 mixes exhaustion with a change of rules.

## LLM contributions

None, and none is possible: the series closes in 2017. Its value is as the
counterfactual for the live series. On [enwik9](../algorithms-enwik9/README.md) the awarded
records continued through 2024 at their historical cadence with no AI credit, a
2026 entry is pending, and the uncapped frontier has not moved since October 2023
— and the eight-and-a-half-year gap recorded here is the evidence that gaps of
that length happened before any of this. Where AI has entered record series in
this domain it is on the machine-learning speedruns, at roughly one percent a
step on [modded-nanogpt](../algorithms-nanogpt/README.md) and about 23% once on the
[CIFAR-10 speedrun](../algorithms-cifar10/README.md), not on compression.

## Related literature

The prize's own record table is the source [@hutter2026prize], with the
successor series scored on the same page and on the uncapped leaderboard
[@mahoney2026ltcb]. That a fixed problem yields a few large gains and long
stretches of nothing is the measured shape across 113 algorithm families, where
about half never improve at all and improvements average 1.44 per family since
1940 [@sherry2021fast]; the same jumpiness appears in SAT solvers rerun on
identical hardware, where jumps arrive every three to five years
[@biere2023satmuseum].
