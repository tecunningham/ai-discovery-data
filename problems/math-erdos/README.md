# Erdős problems catalogue

**Domain:** mathematics
**Metric:** problems catalogued, statuses marked solved, and statements formalized in Lean, at monthly site snapshots; plus an imputed solution year per solved problem
**Coverage:** 2025-08-31 to 2026-08-10, thirteen snapshots; imputed solution years 1940–2026
**Data:** [`erdos-database-history.csv`](erdos-database-history.csv), [`erdos-solution-years.csv`](erdos-solution-years.csv)
**Upstream:** <https://www.erdosproblems.com/>, with the snapshot statistics and Lean counts from <https://github.com/teorth/erdosproblems> and the AI-resolution count from <https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems>
**Verdict:** inconclusive — the imputed years show a real 2024–2026 surge, but the catalogue was assembled while it happened, and it selects for exactly these problems

![Monthly Erdős catalogue snapshots: problems catalogued, statuses marked solved, and statements formalized in Lean.](discovery-math-erdos.png)

![Imputed solution years for the solved problems in the Erdős catalogue.](erdos-solution-years.png)

## The problem

The Erdős problems catalogue is a community register of the problems Erdős
posed, one page per problem, each carrying a status and increasingly a Lean
formalization of its statement. It matters here for one reason: it is by far the
largest body of individually stated, genuinely open mathematics that AI systems
have actually been pointed at, and the project keeps a public per-problem record
of what has fallen.

A "discovery" in this series is a status edit from open to solved. That is a
bookkeeping event, not a mathematical one, and the site itself warns that the
edit can follow the underlying solution by weeks, months, or decades. It is also
a stock rather than a flow: the first chart shows how many problems currently
carry a solved status, not how many were solved in a given month.

The second chart is this folder's attempt to recover the flow. Each solved
problem's page usually states what resolved it — "Solved by Maynard [Ma16]" —
and the page's bibliography dates that reference. Imputing each solved problem
a solution year from its resolving reference turns the 556-row stock into a
per-year series running back to 1940. That series is imputed, not measured:
its rules and failure modes are documented below, and every date in it is the
publication year of the resolving work, not the day the mathematics happened.

The snapshot series remains a poor instrument for a slope change and a good one
for scale. The imputed series can say more about timing, but it inherits the
catalogue's selection: the corpus was assembled from 2023 onward, partly around
the very solutions being counted.

## What the chart shows

Between August 2025 and August 2026 the catalogue grew from 992 problems to
1,217, statuses marked solved from 355 to 559, and Lean-formalized statements
from 148 to 608. The red callout is the separate stock: about 13 full
AI-standalone resolutions recorded in the project's AI wiki at its 2026-06-30
freeze, against those 559 solved statuses. To be precise about what froze:
the wiki page attributing contributions to AI systems stopped updating on
2026-06-30, while the catalogue itself — problem statuses, the solved count,
the Lean formalizations — is still edited and still moves in these snapshots.

The project publishes its own running chart of the same statistics history this
folder's fetcher reads, kept current in the repository:

[<img src="https://raw.githubusercontent.com/teorth/erdosproblems/main/data/statistics_history_light.svg" width="600" alt="Erdős problems progress, drawn by the teorth/erdosproblems repository from its statistics history.">](https://github.com/teorth/erdosproblems)

Unlike the PNG above, that image is upstream's and live: it will keep moving
after this document's snapshot date, and its counts are the project's own.

The second chart reads the imputed years. Of the 556 solved problems, 502 carry
an imputed solution year and 54 state no dateable resolution. The dated series
runs 1940 to 2026 and holds near six resolutions per year across 2000–2023,
then jumps: 34 in 2024, 33 in 2025, and 55 in 2026 with four months of the year
still to run. The jump is the most direct flow-level evidence in this folder,
and it is also exactly where the selection caveats below bite hardest: the
catalogue grew around these solutions, and an old problem's solution enters the
series only when the literature already recorded it.

![Composition of recent Erdős-problem solutions and their position in the catalogue.](erdos-surge-anatomy.png)

The third chart is the anatomy of that jump, and it shows the surge has two
distinct phases. The 2024–2025 phase is human and preprint-shaped: the 34 rows
of 2024 trace to 31 distinct works — one paper can resolve several problems —
with 25 dated by arXiv preprints and 9 by published papers, and none by the AI
wiki. In 2025, 30 of the 33 rows are preprint-dated and one published, which is
what a wave too recent for peer review looks like. These are real papers by
real mathematicians, several written directly to the list — titles like "A
problem of Erdős-Graham-Granville-Selfridge" and "Resolution of Erdős'
problems about unimodularity" — and a small circle of names (Tao, Sawhney,
Liu, Kovač, Cambie, Steinerberger) recurs across them. The 2026 phase is the
flip: 45 of its 55 rows are dated only by the AI wiki's record of a full AI
solution, with no citable paper on the problem's page, against 10 preprints.

The right panel places each dated solution at its problem number, which is the
order the site catalogued them. For 2026 the reading is sharp: 41 of the 55
sat at numbers 1–992, catalogued by the August 2025 snapshot and standing as
open before they fell. For 2024–2025 the anchor is too late to order
cataloguing against solution — a 2024 solution at a low number may still have
been added to the site after the paper appeared — but the same panel shows the
pre-2024 pattern that keeps the whole series honest: decades-old solutions
scattered at every problem number are literature archaeology, problems entering
the catalogue with their resolutions already attached.

The catalogue count stopped changing in April 2026, which is the only part of the
window where a rise in solved status cannot be caused by adding an
already-solved historical problem. Over that fixed cohort the solved count went
from 525 on 30 April to 559 on 10 August, thirty-four rows in about a hundred
days. That arithmetic is this repository's, not the project's, and thirty-four
rows is too few and too recent to compare against anything.

One reading is worth stating because the lines cross: Lean-formalized statements
pass the solved count in the final snapshot, 608 against 559. The two count
different things. Formalizing a statement is not proving it, and the
formalization drive is a separate effort from the solving.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws the
snapshot series as open problems remaining — a line that can rise, because new
problems are catalogued faster than problems fall:

![Open problems remaining at each snapshot.](cumulative-math-erdos.png)

## How the chart was built

[`figure.py`](figure.py) draws both charts. The first plots three step series
from `erdos-database-history.csv` against `date`: `total_problems`
as a dashed grey line, `total_solved` in blue with markers, and `lean_formalized`
as a purple dotted line. The x tick labels come from the `month` column, every
second snapshot plus the last. January 2026 onward is shaded, as in every figure
here. The second chart bars the `solution_year` column of
[`erdos-solution-years.csv`](erdos-solution-years.csv) by year, blue where the
year comes from a reference on the problem's page and red where the only dated
resolution is the AI wiki's. The third chart reads the same file's
`reference_kind` column — `published` when a dating reference carries a venue
in the page's bibliography, `preprint` when every dating reference is
arXiv-only, `ai_wiki` when the date is a wiki entry — and plots each dated
solution against its problem number, with the catalogue's size at the first
snapshot marked from `erdos-database-history.csv`.

The two splits are not the same rule: the second chart keys on `basis`, what
dated the problem after review, while the third keys on `reference_kind`, what
kind of reference did the dating. Seven problems whose dates rest on the wiki
but were confirmed in review are therefore blue in the second chart and red in
the third — 40 problems rest on the wiki alone, 47 are wiki-dated.

The AI-standalone stock is drawn as a boxed callout rather than a fourth line.
About 13 against stocks of 559 and 1,217 would be a flat line on the axis, and
plotting it as a series would also imply it is measured on the same basis, which
it is not: it comes from a different source, frozen on a different date, under
its own definition of standalone contribution.

The `catalogue_count_unchanged` column flags the snapshots from April 2026 on,
where the cohort is fixed. The figure does not shade that sub-window separately;
the column is there so a reader can find it.

The imputed years come from [`fetch_solutions.py`](fetch_solutions.py), which
is run by hand rather than by `make fetch` because it downloads the LaTeX
source of every solved problem's page — about 560 throttled requests. It
imputes each solved problem a year by three rules, in order. First, review
overrides: [`erdos-solution-year-overrides.csv`](erdos-solution-year-overrides.csv)
carries 175 hand-checkable rows, each with its reference and reason, for pages
where the mechanical rule misfires. Second, the solving citation: the page's
discussion usually attributes the resolution in a sentence like "Solved by
Maynard [Ma16]", and the imputed year is the publication year of the newest
reference cited in the first such sentence, taken from the page's own
bibliography. Third, the AI wiki: problems whose only recorded resolution is an
AI system's take the date in the wiki's primary-contribution tables. Where a
citation and a wiki date both exist the earlier wins, since the question is
when the problem was first resolved.

The overrides file is the honesty layer, and how it was built matters: the
sentence rule and the wiki overlay together dated 418 of the 556 pages, and
every one of the 556 was then re-read against that output — a model-assisted
review of each page's discussion text, spot-checked by hand — which supplied a
year for 94 pages the rule had missed, corrected 71, and withdrew 10, leaving
54 problems with no dateable resolution stated anywhere on their page.
Rerunning the fetcher reapplies the overrides, so the review survives a refetch
until the underlying page text changes.

Every point in the snapshot series comes from one source, the project's GitHub
statistics history, which is what [`fetch.py`](fetch.py) rebuilds the whole
file from. An earlier
version of this series set its last point by hand from the live website's
solved-status headline, and the two sources do not agree: on 8 August the site
headline read 565 solved where the statistics history recorded 559. A hand-set
endpoint that the folder's own fetcher overwrites is not a series anybody can
rebuild, so the fetcher's value stands and the disagreement is recorded here
instead. It is worth knowing that the project's own two public counts of the
same quantity differ by about six.

The solution-years file is a third instrument again: it enumerates the 556
problems whose `problems.yaml` status read proved, disproved or solved on the
day `fetch_solutions.py` ran, where the 10 August statistics snapshot records
559 marked solved. Three counts of nominally one stock — 556, 559, 565 — each
from a different source read on a different day, which is a caution worth
carrying to any single-day reading of this catalogue.

## What it cannot support

- **Status-change dates are not solution dates.** The site says so itself, and
  the gap can run to decades. Every date on the snapshot chart is an editing
  date; the imputed years exist precisely because of this, and carry their own
  caveats below.
- **An imputed year is the publication year of the resolving reference,** not
  the date of the mathematics, and for 47 problems the only dated record is a
  wiki entry rather than a citable paper. Those 47 count full solutions in any
  of the wiki's four primary-contribution categories — a wider net than the
  roughly 13 standalone resolutions in the first chart's callout. The
  assignment of "the resolving reference" is an editorial reading of each
  page's discussion — reviewed, but not ground truth, and 54 solved problems
  resisted any dating at all.
- **Recent rows are mostly unrefereed, and they cluster.** 98 of the 502 dated
  rows rest on arXiv preprints and 47 on wiki entries; the surge years are
  almost entirely these two kinds. One paper can resolve several problems and
  a few authors account for many rows, so the recent bars count catalogue rows
  cleared, not independent discoveries — and any of the underlying preprints
  or wiki claims could yet fail review.
- **The imputed flow inherits the catalogue's selection twice over.** The
  corpus was assembled from 2023 onward, partly around solutions as they
  happened, and AI systems have been pointed at this list precisely because it
  is a list. A 2024–2026 surge in this series is evidence about these problems,
  not about mathematics at large — the prestige-list series linked below are
  the check on that.
- **The comparable window is about eleven months.** There is no before, so there
  is nothing for the agent era to be compared against.
- **The two stocks are not an AI-versus-human flow.** The roughly 13 AI-standalone
  resolutions and the 559 solved statuses are counted on different dates under
  different definitions, so subtracting one from the other does not estimate
  human output.
- **The cohort grew by 225 rows inside the window**, and problems can be added
  already solved, so most of the rise in solved status is catalogue construction
  rather than new mathematics.
- **Lean formalization counts statements, not proofs**, and is driven by a
  separate volunteer effort, so it is a measure of infrastructure rather than of
  discovery.
- **The AI-attribution wiki is frozen and downstream — the catalogue is not.**
  The wiki's AI counts stop at 2026-06-30, and its largest single input is a
  vendor's own denominator rather than an independent recount. The catalogue's
  own tracking of solved and open statuses continues past that date, so the two
  stocks drift apart: AI resolutions after June 2026 can appear as status edits
  but never in the wiki's count.

## LLM contributions

This is the one corpus in the collection where an AI-contributed flow is
measurable at all. The frozen wiki records roughly 47 AI-standalone
contributions — about 13 full resolutions, about 25 partial, and about 9
incorrect — and states both that the list "is not a benchmark" and that
"absence of past progress may reflect obscurity rather than difficulty"
[@erdosproblems2026wiki]. The one rate with a real denominator is AlphaProof
Nexus, which resolved 9 of 353 open problems, about 2.5%, at a few hundred
dollars each, two of them open for 56 years; on the more mechanically stated
OEIS corpus the same system proved 44 of 492, about 9% [@deepmind2026nexus].
Named single results run from Erdős #728 in January 2026, produced by GPT-5.2 Pro
with Aristotle and described as the first resolved autonomously, to the May 2026
disproof of Erdős's 1946 unit-distance conjecture, which nine mathematicians
digested into a human-verified account and for which Will Sawin made the exponent
explicit at greater than 1.014 [@openai2026discretegeometry]. Astra's August 2026
claims on #146, #180 and #183 post-date the wiki freeze, carry Lean certificates,
and are awaiting peer review. Tao supplies the scale without a rate: "Fifty-odd
problems have been solved with AI assistance, which is great, but there's like
six hundred to go" [@tao2026interview].

## Related literature

The catalogue and its warning about status dates are the project's own
[@erdosproblems2026catalogue]; the AI counts come from a wiki its maintainers
have stopped updating [@erdosproblems2026wiki]. The formal-proof route that
produced the only denominated rate here is documented by its vendor
[@deepmind2026nexus], and the single most consequential result by another
[@openai2026discretegeometry]. Tao's commentary is the sharpest statement of why
a solve count is not a success rate, since problem selection, effort, and failed
attempts are all unobserved [@tao2026interview]. The prestige-list series in
[Hilbert](../math-hilbert/README.md), [Landau](../math-landau/README.md),
[Thurston](../math-thurston/README.md), [Smale](../math-smale/README.md),
[Millennium](../math-millennium/README.md) and [TOPP](../math-topp/README.md) are the ceiling check
on this corpus: they move far less, and they are selected against cheap
verification. The catalogue's own curator has since named a
[top-10 subset](../math-erdos-top10/README.md), scored in this collection as
its own prestige ledger.
