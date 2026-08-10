# Gurobi mixed-integer programming speed

**Domain:** algorithms
**Metric:** cumulative vendor-reported MILP speedup across releases, every version rerun on one machine
**Coverage:** releases 10 through 13, announced 2022-11-14 to 2025-11-18, baselined at version 9.5
**Data:** [`gurobi-milp-speedups.csv`](gurobi-milp-speedups.csv)
**Upstream:** <https://www.gurobi.com/misc/lp/all/unmatched-performance> (per-release announcement URLs are carried row by row in the CSV, for example <https://www.gurobi.com/whats-new-gurobi-13-0/>)
**Verdict:** no acceleration

![Cumulative Gurobi MILP speedup across releases 10 to 13, drawn in vendor grey.](discovery-algorithms-gurobi.png)

## The problem

Mixed-integer programming is the workhorse of applied optimization, and solver
speed on it is one of the oldest measured algorithmic-progress series there is.
The measurement design is the good part: every released version is recompiled and
rerun on one bank of identical machines, so the ratio between versions is
machine-independent by construction rather than by regression. Gurobi states the
setup as a test set of 9,423 models, of which 960 are discarded for inconsistent
answers and 2,641 because no version solves them, with the speedup measured on
the bracket of models taking over 100 seconds, leaving 3,517; a 10,000-second time
limit; and an Intel Xeon E3-1240 v5 at 3.50 GHz with 4 cores, 8 hyper-threads and
32 GB of RAM.

That design is Robert Bixby's, from the canonical measurement of solver progress
[@bixby2012history], now run by the company he founded. A "discovery" here is a
released version that solves the same models faster, so the unit is a release
rather than a paper or a record.

## What the chart shows

Four annual releases and four single-digit-to-low-double-digit gains: 13% for
version 10 on 2022-11-14, 8.6% for version 11 on 2023-12-04, 13.1% for version 12
on 2024-11-19, and 8.2% for version 13 on 2025-11-18. Multiplied together that is
a cumulative factor of 1.50 since version 9.5, and the per-release figures show
no trend within the window: the two largest gains are the first and the third.

The comparison that matters is with the same problem's earlier history. A 2013
survey recorded MIP algorithms as having "roughly doubled in speed each year"
[@grace2013algorithmic], and Bixby's own fixed-hardware test over CPLEX versions
released between 1991 and 2007 multiplied out to a machine-independent factor of
over 29,000 [@bixby2012history]. Against either, 8 to 13% a year is an order of
magnitude slower or worse, on the vendor's own numbers. The vendor's cumulative
claim tells the same story from the other end: its performance page moved from
"a more than 75x speedup on MILP since version 1.1" in the version-10 era to
"A 92x speed-up over version 1.1" by the version-13 era, which is most of a
lifetime's progress already banked.

None of the version 11, 12 or 13 announcements credits AI or a language model
with any solver improvement. The largest recent gains the vendor highlights are
in nonconvex problem classes, such as a 5.8-fold speedup on nonconvex MIQCP in
version 11.

## How the chart was built

[`figure.py`](figure.py) reads
`gurobi-milp-speedups.csv` and takes the running product of the
`release_speedup` column in row order, so the plotted quantity is cumulative
rather than per-release. The line starts at 1.0 at the beginning of 2022, steps
at the year fraction of each `date`, and each point is labelled from the `release`
column. The whole series is drawn in the collection's vendor grey rather than the
human blue, because the figures are the vendor's own and were not independently
rerun; the corner note states the cumulative factor and that no AI credit appears
in the release notes. The axis is linear and January 2026 onward is shaded.

Each row also carries `credit`, `source` and `source_url`, so the provenance of
every percentage is in the data rather than only in this document.

There is no `fetch.py` in this folder. The four percentages are hand-transcribed
from prose release announcements, some of them through archive captures, and each
new release is read and typed in the same way.

## What it cannot support

- **The figures are vendor-run on a vendor-selected test set.** Nothing here was
  independently rerun, the models are the vendor's choice, and thousands are
  discarded by the vendor's own rules before the ratio is computed.
- **Independent benchmarking ended in 2024.** Hans Mittelmann's public benchmark
  page records that IBM and FICO demanded removal after 2018 and that "In August
  2024 Gurobi decided to withdraw from the benchmarks as well"
  [@mittelmann2024benchmarks]. So over exactly the window in which an agent-era
  bend would appear, the only surviving MIP series is the one the vendor runs.
- **The chart cannot show the early history it is compared against.** The
  per-version charts for versions 2 through 9 are images that were not
  transcribed, so this series starts at version 9.5 as 1.0; the doubling-per-year
  and 29,000-fold figures come from the cited literature, not from these rows.
- **Percentages transcribed by hand from prose announcements.** The four
  `release_speedup` values are read off release pages, some through archive
  captures, and a cumulative product of four vendor point estimates carries no
  error bar.
- **The headline percentages are aggregates.** Each is an overall geometric-mean
  figure and each is larger on the over-100-second bracket, so the same release
  can be quoted at two different sizes.
- **One date upstream is unverified.** Version 1.0's commonly cited 2009 release
  is not confirmed on any primary Gurobi page; the vendor's own support table
  starts at version 7.0 in 2016. Nothing in this chart depends on it, but the
  cumulative "since version 1.1" claims do.

## LLM contributions

None credited on this series. The four releases plotted here span the whole
period of frontier-agent deployment and their announcements attribute nothing to
AI.

The nearest AI result in classical combinatorial optimization is on a different
instrument. AE-Kissat-MAB, a solver evolved with a language-model loop, won the
2025 SAT Competition's Main Sequential Track, solving 327 of 400 instances
against 321 for the human-written Kissat lineage it descends from
[@satcompetition2025results]. That is a margin of about 2%, the same order as the
AI steps on the machine-learning speedruns, and it is deliberately excluded from
the curves in this collection because the competition changes its benchmark set
every year, so a win cannot be placed on a fixed-hardware long-run curve. The
other adjacent result is AlphaEvolve's data-centre scheduling heuristic, self
reported to recover about 0.7% of fleet-wide compute [@novikov2025alphaevolve],
which is a scheduling heuristic in production rather than a solver record.

## Related literature

Bixby's fixed-hardware CPLEX measurement is the methodological parent and the
source of the historical rate [@bixby2012history]; the 2013 six-domain survey
supplies the doubling-per-year figure and, unusually, warns that MIP was singled
out precisely because it improved fast [@grace2013algorithmic]. The independent
benchmark that no longer covers Gurobi is Mittelmann's
[@mittelmann2024benchmarks], and the vendor's standing claims are on its
performance page [@gurobi2026performance] and its version 13 announcement
[@gurobi2025release13]. For how unusual a plateau is not, half of all algorithm
families show little or no improvement at all [@sherry2021fast], and the SAT
Museum finds progress "mostly rather slow, except for performance jumps in some
years" [@biere2023satmuseum].
