# ai-discovery-data

Vendored datasets and figure code behind measurements of how much LLMs have
contributed to discovery, in the three domains where somebody keeps a public,
dated, finder-attributed score: **software vulnerabilities**, **mathematics**,
and **algorithms**.

This repository is the canonical home for that data. It exists so the charts in
[LLMs' Contribution to Discovery](https://tecunningham.github.io/posts/2026-08-08-llm-contribution-to-discoveries.html)
can be checked and rebuilt from public sources by someone who did not write them.

## Layout

| Path | What is in it |
|---|---|
| `data/` | One CSV per series, vendored from a public source. The canonical copy. |
| `figures/` | One PNG per series, generated from `data/`. Committed, never hand-edited. |
| `problems/` | One markdown file per series: what the problem is, how the chart was built, what the data cannot support, and the literature. |
| `tools/make_figures.py` | Generates every figure in `figures/` from `data/`. |
| `tools/fetch/` | Scripts that rebuild the CSVs from their upstream sources. |
| `tools/check.py` | Consistency checks: every series has a doc, a figure, and a source. |
| `references.bib` | Bibliography for the problem documents. |

## Reproducing

Figures need only Python and matplotlib, and no network:

```bash
make figures      # data/*.csv -> figures/*.png
make check        # every series has a figure, a doc, and an upstream source
```

Rebuilding the data itself needs the network, and is deliberately a separate
step because several upstream sources rate-limit, change shape, or require
judgment to transcribe:

```bash
make fetch        # refetch the automatable series from upstream
```

`make fetch` does not cover everything. Series whose upstream is a prose page
rather than a feed — the Hutter Prize table, the AlphaEvolve problem write-ups,
the Gurobi release notes, the matrix-multiplication record chronology — are
transcribed by hand, with the source URL recorded per row in the CSV. The
per-problem document says which category each series is in.

One file is not this repository's to regenerate. `famous-open-problem-lists.csv`
holds the Hilbert, Smale, Millennium and TOPP status ledgers, which are
transcribed by hand inside the blog repository's own figure code and written out
from there. What is here is a vendored snapshot to plot from, and `make sync`
deliberately skips it so a transcription made in the blog cannot be reverted by
a sync from here.

## What the numbers are and are not

Three conventions run through every series here, and reading a chart without
them will mislead you.

**A finder credit is a floor, not a measurement.** Where a project records who
found a vulnerability, this data classifies a report as AI-credited only when
the credit string explicitly names an AI system, an AI-security firm, or an
agent. A researcher who used a model and did not say so counts as human. So
every AI share here is a lower bound by an unknown margin.

**A disclosure is not a discovery, and a status change is not a solution.**
Vulnerability series count what got published, on the date it got published.
The Erdős catalogue records the date a status was edited, which is not the date
a problem was solved.

**Records are lumpy with no AI in them.** Half of all algorithm families never
improve at all [@sherry2021fast], solver records jump every few years, and a
century-scale exponent can sit still for eighty years and then move by hand. A
staircase inside the agent era is not by itself an AI signature, and a flat
stretch is not by itself an exhausted frontier.

## Series

Each row links to its own document. The verdict column asks only whether the
series shows an acceleration in the rate of discovery, not whether AI
contributed anything.

<!-- BEGIN GENERATED: series-index -->
| Series | Domain | Metric | Coverage | Acceleration? |
|---|---|---|---|---|
| [curl vulnerability disclosures](problems/cyber-curl.md) | vulnerabilities | vulnerabilities disclosed per year, split by finder credit | 2000–2026, partial through 2026-06-24 | accelerating |
| [Firefox vulnerability disclosures](problems/cyber-firefox.md) | vulnerabilities | advisory CVEs per year, split by AI, fuzzer, or other reporter credit | 2016–2026, partial through late July 2026 | accelerating — though disclosures roughly doubled from 2021 to 2025 with essentially no AI credit |
| [All software: vulnerabilities known exploited](problems/cyber-kev-exploited.md) | vulnerabilities | CVEs added per year to CISA's Known Exploited Vulnerabilities catalogue | 2021–2026, from the catalogue's November 2021 launch, partial through 2026-07-28 | no acceleration — additions annualize to about +22% in 2026 against +59% for disclosures |
| [All software: vulnerabilities disclosed](problems/cyber-nvd-disclosed.md) | vulnerabilities | CVEs published per year in the US National Vulnerability Database | 2016–2026, partial through 2026-07-28 | accelerating — but growth was already +32% and +23% in 2024 and 2025, and no disclosure here is attributed to anyone |
| [OpenSSL vulnerability disclosures](problems/cyber-openssl.md) | vulnerabilities | vulnerabilities disclosed per year, split by finder credit | 2002–2026, partial through 9 June 2026 | accelerating — but the same shape appeared in 2015–2016 from a purely human cause |
| [OSS-Fuzz vulnerability discoveries](problems/cyber-oss-fuzz.md) | vulnerabilities | vulnerability records published per year by an automated fuzzing programme | 2020–2026, partial through late July 2026 | declining |
| [Finite construction records around AlphaEvolve](problems/math-alphaevolve-related-records.md) | mathematics | cumulative record steps in five groups of finite construction and packing problems | 1949–2026, 22 record steps across the five groups | inconclusive — the 2025 cluster is real, but these five groups were selected because an AI system worked on them |
| [ANTEDB analytic-number-theory exponents](problems/math-antedb.md) | mathematics | cumulative slice-level record changes across 58 exponent slices in the three families $\mu$, $A$ and $\beta$ | 1920–2024 in the underlying literature; extracted from the database as of 2026-07-26 | no acceleration |
| [Erdős problems catalogue](problems/math-erdos.md) | mathematics | problems catalogued, statuses marked solved, and statements formalized in Lean, at monthly site snapshots | 2025-08-31 to 2026-08-08, thirteen snapshots | inconclusive — the comparable window is about eleven months, and a status edit is not a solution |
| [Hilbert's problems](problems/math-hilbert.md) | mathematics | cumulative ledger rows scored resolved, out of 28 scored rows | 1900–2026, with dated resolutions running 1900–1998 | no acceleration |
| [Kissing number in dimension 11](problems/math-kissing-11.md) | mathematics | best known lower bound on the kissing number $K(11)$ | 1971–2026, five record steps | accelerating — a burst on one dimension of one problem, not a field-wide rate |
| [Millennium Prize Problems](problems/math-millennium.md) | mathematics | cumulative prize problems scored resolved, out of 7 | 2000–2026, with one dated resolution in 2003 | no acceleration |
| [Smale's problems](problems/math-smale.md) | mathematics | cumulative ledger rows scored resolved, out of 19 scored rows | 1998–2026, with dated resolutions running 2002–2026 | inconclusive — one AI-attributed fall in 2026, and a single event cannot set a slope |
| [Sphere-packing lower-bound ladder](problems/math-sphere-packing.md) | mathematics | cumulative improvements to the asymptotic lower bound on sphere-packing density in high dimension | 1905–2025, eight recorded steps | accelerating — and every step is human, which is what this series is here to show |
| [Sums-and-differences and autoconvolution constants](problems/math-sums-autoconvolution.md) | mathematics | best known lower bounds on two additive-combinatorics constants, $C_{6.44}$ and $C_{6.3}$ in the AlphaEvolve numbering | 2007–2025, twelve record steps across the two ladders | inconclusive — AI steps are visible in 2025, and a human retook one of the two ladders within months |
| [The Open Problems Project](problems/math-topp.md) | mathematics | cumulative entries whose own status line says solved, settled, or closed, out of 78 | 2001–2026, with dated resolutions running 2000–2024 | no acceleration |
| [CIFAR-10 speedrun](problems/algorithms-cifar10.md) | algorithms | seconds to 94% test accuracy on CIFAR-10 on a single A100 | 2018–2026; the plotted series starts 2022-12-29 and ends with a claim of 2026-07-09 | declining — the yearly improvement factor falls from 2.9 to a claimed 1.09 |
| [Hutter Prize compression: enwik8](problems/algorithms-enwik8.md) | algorithms | total size in bytes of decompressor plus archive for a fixed 100 MB text corpus, under a CPU-time and memory cap | 2006-03-24 baseline to the last awarded record on 2017-11-04; retired when the prize moved to enwik9 in February 2020 | baseline — a pre-agent record cadence for comparison, not a test of recent acceleration |
| [Hutter Prize compression: enwik9](problems/algorithms-enwik9.md) | algorithms | total size in bytes of decompressor plus archive for a fixed 1 GB text corpus, under a CPU-time and memory cap | 2019 baseline to 2026; the prize moved to enwik9 on 2020-02-21, and the uncapped comparator runs 2019 to 2023 | no acceleration |
| [Gurobi mixed-integer programming speed](problems/algorithms-gurobi.md) | algorithms | cumulative vendor-reported MILP speedup across releases, every version rerun on one machine | releases 10 through 13, announced 2022-11-14 to 2025-11-18, baselined at version 9.5 | no acceleration |
| [modded-nanogpt training speedrun](problems/algorithms-nanogpt.md) | algorithms | minutes of training to a fixed target validation loss, per accepted record | 2024-05-28 to 2026-05-27, all 86 records listed in the repository README | no acceleration |
| [Stockfish development builds on fixed hardware](problems/algorithms-stockfish.md) | algorithms | Elo relative to Stockfish 15, from 20,000 games per build on one fixed machine and time control | 2013-04-30 to 2026-07-26, 2,542 tested development builds | no acceleration |
| [Matrix-multiplication exponent ω](problems/matrix-omega.md) | algorithms | best proved upper bound on the asymptotic exponent ω of n×n matrix multiplication; lower is better | 1969 to 2024, fifteen recorded steps | declining — the asymptotic record is slowing, and no step in it is AI-attributed |
<!-- END GENERATED: series-index -->

## Provenance and licence

Every CSV records where its rows came from, either in a per-row source column
or in the header of the fetch script that built it. The underlying facts belong
to their publishers — the curl project, Mozilla, OpenSSL, NIST, CISA, Google
OSS-Fuzz, the Erdős problems community, ANTEDB, Google DeepMind, the Hutter
Prize, nextchessmove.com, and the speedrun leaderboards — and are collected
here under the terms each publisher offers. The aggregation, classification,
and arithmetic are this repository's, and are the part that can be wrong.
