# Stockfish development builds on fixed hardware

**Domain:** algorithms
**Metric:** Elo relative to Stockfish 15, from 20,000 games per build on one fixed machine and time control
**Coverage:** 2013-04-30 to 2026-07-26, 2,542 tested development builds
**Data:** [`stockfish-ncm-elo.csv`](stockfish-ncm-elo.csv)
**Upstream:** <https://nextchessmove.com/dev-builds>
**Verdict:** no acceleration

![Stockfish development-build Elo against Stockfish 15 from 2013 to 2026, with releases marked and the first LLM-credited commit open.](discovery-algorithms-stockfish.png)

## The problem

Stockfish is an open-source chess engine whose every development build is played
by a third party, nextchessmove.com, against one frozen opponent. In the
measurer's own description, "NCM plays each Stockfish dev build 20,000 times
against Stockfish 15", on "Dell R7515 128-thread EPYC 7702 dedicated servers",
each playing "16 games concurrently with 30+0.3 time controls" with hash at 128MB
and threads at 8.

Everything that could confound the comparison is held: the opponent, the
hardware, the time control, the engine settings, and the number of games. What
remains is software, which is why this is the densest efficiency series in the
collection — thirteen years of dated builds on one Elo scale.

A "discovery" here is not a discrete record. The series measures every build, so
progress appears as a rise in the standing level, and the natural unit is Elo per
year rather than records per year.

## What the chart shows

Stockfish 3 measures −537.61 ± 7.82 against Stockfish 15 on 2013-04-30, and the
newest build in the series measures +137.27 ± 1.97 on 2026-07-26. That is about
675 Elo of pure software progress, averaging 51 Elo a year across the whole
span.

The largest single move is one architecture change, not a trend. Calendar 2020
gained about 121 Elo and 2021 about 114, around the NNUE merge of 2020-08-06.
The project's own regression tables put one patch at roughly 58 Elo — master
against Stockfish 11 measured +25.49 six days before and +83.42 just after — and
the announcement described the gain as "currently on > 80 Elo" at faster time
controls. A good ordinary year is 30 to 50 Elo, so a single patch was worth more
than a year.

The agent era runs at or below the rate immediately preceding it. The source log
reports roughly 47 Elo a year across 2022–23 against 18 to 31 a year in 2024–26.
Recomputing year-end to year-end from this CSV gives 49 in 2022, 41 in 2023, 25
in 2024, 32 in 2025, and 14 through 2026-07-26, which annualizes to about 24.
The two sets of figures differ because the series is sampled irregularly and the
year boundaries can be drawn in more than one place; both readings put 2024–26
below 2022–23 and far below the NNUE years. For an external benchmark, chess was
rated at "around fifty Elo points per year over the last four decades" in a 2013
survey [@grace2013algorithmic], so the current rate is at or under a rate stated
before any of this.

The open red marker is the first master commit whose message credits a language
model, merged 2026-07-26. It is a 0.6% speed patch, not an Elo record.

## How the chart was built

[`figure.py`](figure.py)
reads `stockfish-ncm-elo.csv` and draws `elo_vs_sf15` against the year fraction
of `date` as one thin line through all 2,542 builds. Rows with a non-empty
`release` column are additionally drawn as points, so the twenty tagged releases
from Stockfish 3 to Stockfish 18 are visible against the development noise. The
axis is linear, since Elo is already a ratio scale and nothing needs
normalizing. January 2026 onward is shaded.

The LLM-credited commit is drawn as one open red marker placed at the year
fraction of 2026-07-26 and at the last measured Elo value, annotated "first
LLM-credited master commit: 0.6% speed patch, not an Elo record". The open style
is used here for the same reason as elsewhere in the collection: the point marks
something that is not a record on the plotted axis. The `elo_err` column is
carried in the CSV but is not drawn.

The series was extracted by hand from a JavaScript data array on the dev-builds
page, with the release tags matched to builds afterwards, so
[`fetch.py`](fetch.py) is a staleness probe rather than a fetcher: it reports if
the page carries a build later than the last vendored one.

## What it cannot support

- **The LLM marker is a date, not a measured effect.** It is placed at the last
  measured point, so its height carries no information about what the patch did.
  The patch's own effect is the 0.6% speed figure quoted in its commit message.
- **A fixed opponent gets less informative as the gap grows.** Stockfish 15 is
  now about 137 Elo weaker than master, and Elo measured against a much weaker
  opponent compresses.
- **The confidence intervals are in the data and not in the picture.** They run
  near ±8 Elo at the start of the series and near ±2 at the end.
- **The per-year rates depend on where the year is cut.** They are arithmetic
  over an irregularly sampled series, which is why the source log's 18 for 2024
  and this repository's 25 are both defensible.
- **The project's own regression tables cannot be read across 2023.** Stockfish
  changed opening books that year, which roughly doubles measured gaps — one
  release cycle measures +18.30 on the old book and +47.03 on the new one on the
  same day. This series avoids the problem by holding one setup throughout, and
  the official tables should not be spliced onto it.
- **One credited commit is not a measurement of AI contribution.** A repository
  search found no other commit crediting a language model, which is a statement
  about commit messages rather than about what tools contributors used.

## LLM contributions

Exactly one, and its own author describes the division of labour. Commit
db98633b of 2026-07-26 reads: "The first version of this patch was coded up by
gpt-5.5-high. I made many changes, but probably most of the lines of code are
LLM-written" [@stockfish2026llmcommit]. So a human maintainer substantially
rewrote it before it was merged. It is a non-functional speed patch, measured at
"speedup % = +0.60 +/- 0.08", which passed the project's standard statistical
gate. No other commit in the repository credits a language model, and no Elo gain
in thirteen years of this series is AI-attributed.

That size is the same order as the AI-set records on
[modded-nanogpt](../algorithms-nanogpt/README.md), where four of 86 records are AI-credited
at roughly one percent each. The one deeper AI step anywhere nearby is on the
[CIFAR-10 speedrun](../algorithms-cifar10/README.md), at about 23%.

## Related literature

The measurement is a third party's [@nextchessmove2026devbuilds], and the
architecture change that dominates the series is documented by the project
[@stockfish2020nnue]. Jumps every few years with slow progress between them is
the standard shape in this kind of series: historic SAT solvers rerun on one
machine improve mostly slowly with "performance jumps in some years, which
arguably happen with a frequency of 3 to 5 years" [@biere2023satmuseum], and
across 113 algorithm families the distribution of improvement is bimodal rather
than centred on its mean [@sherry2021fast]. The pre-AI rate for chess
specifically comes from a 2013 survey of six domains [@grace2013algorithmic].
