# The Open Problems Project

**Domain:** mathematics
**Metric:** current status of 78 scored rows, plus dated resolutions per year
**Coverage:** 2001–2026, with dated resolutions running 2000–2024
**Data:** [`topp-problems.csv`](topp-problems.csv)
**Upstream:** <https://topp.openproblem.net/>, with the rows transcribed from the project's GitHub sources
**Verdict:** no acceleration

![Current status of the scored rows, and dated resolutions per year.](discovery-math-topp.png)

## The problem

The Open Problems Project is a maintained list of computational-geometry problems
begun in 2001 by Demaine, Mitchell and O'Rourke. Each entry carries a statement, a
bibliography, and a status line the maintainers update when something happens.

A "discovery" in this series is one of those status lines saying solved, settled,
or closed. That is the maintainers' own language rather than an independent
consensus review, and it is applied loosely in places: entry 12, dynamic planar
convex hull, is counted because the project calls it "solved (in a certain
sense)", although related worst-case questions remain open.

Among the lists scored here this is the most useful instrument, and the reason is
worth stating. Its problems are numerous, they are computational rather than
foundational, and many have answers of exactly the kind AI systems have been
producing elsewhere: an algorithm with a stated running time, or an NP-hardness
proof. It is the closest thing in the mathematics domain to a measurement corpus
rather than a prestige list, so a zero here carries more information than a zero
on the [Millennium](../math-millennium/README.md) problems. What it is not is a fixed-cohort
solve rate, because the 78 entries accumulated over the project's life and the
ledger does not record when each was added.

## What the chart shows

Seventeen resolutions between 2000 and 2024, out of 78 scored rows; 60 remain
open and one, hexahedral meshing, is recorded as partial. The pace is roughly
steady and slightly front-loaded: thirteen of the seventeen falls happen by 2010,
then 2015, 2019, 2023 and 2024. Nothing lands in the shaded 2026 period and no
event is red.

The two most recent are Wang's optimal algorithm for shortest paths among
obstacles in the plane, dated 2023, and Abrahamsen and Stade's NP-hardness proof
for packing unit squares in a simple polygon, dated 2024. Both are human work
recorded in the project's own citations.

One artifact is visible at the left edge and is not a data error. The leftmost
resolution is dated 2000, a year before the project's 2001 start, because Bezdek
and Connelly settled the pushing-disks problem in 2000 and the project's entry for
it records that resolution rather than an open status. The event panel therefore
starts one year before the list itself. It is a small instance of the larger
problem with this series: the ledger dates resolutions but not entries.

## How the chart was built

[`figure.py`](figure.py) calls the shared `problem_list_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), which reads
`topp-problems.csv`, keeps rows whose `status` is
`resolved` with a non-empty `resolved_year`, sorts by year then `problem_id`, and
draws a current-status bar above annual resolution-event bars. The upper panel
reports the 78/17/60/1 breakdown and the lower panel runs from the earliest dated
event through the present. The source note names the `source` column, which for
every row is the project's GitHub problem directory.

The `status` and `resolved_year` columns were set from the project's own
Status and Conjectures lines, and the `notes` column keeps the maintainers'
wording — "Solved: proved NP-hard", "Settled negatively, January 2004", "Now
closed: false; counterexample appeared in the 2009 CCCG proceedings" — so a reader
can see what each status rests on. Where the maintainers give a month, only the
year is scored.

No `ai_problem` argument is passed, because no entry credits an AI system.

There is no `fetch.py`. The 78 rows were transcribed by hand from the project's GitHub problem directory, keeping its maintainers' own status wording; the site publishes no machine-readable index.

## What it cannot support

- **There are no entry-addition dates.** The 78 entries accumulated after 2001 and
  the ledger does not encode when each arrived, so this is a dated-resolution
  ledger and not a fixed-cohort solve rate. A denominator that grows invisibly
  cannot support a rate.
- **One row predates the list.** The 2000 resolution sits a year before the 2001
  start, which is why the event timeline starts before the list year.
- **Statuses are the maintainers' own language**, not independent review, and some
  are qualified — entry 12 is counted on a "solved (in a certain sense)".
- **Unmaintained entries look open.** A problem whose status was never updated is
  indistinguishable here from a problem nobody has solved, so the open count is an
  upper bound on what is genuinely open.
- **Resolution landmarks are not effort-adjusted discovery rates.** Nothing
  records how much search each fall took.
- **Some `resolver` fields are empty**, because the project's status line names a
  citation rather than a person, so this series cannot be split by finder the way
  the vulnerability series can.

## LLM contributions

None. No entry in the ledger credits an LLM or an agent with a fall, and the two
most recent resolutions are human papers from 2023 and 2024.

This zero is the more informative of the prestige-list zeros. TOPP's problems are
computational-geometry questions whose answers are frequently algorithms or
hardness proofs — the kind of output agents have produced in the algorithms domain
— and the list is public, indexed, and cheap to point a system at. So the absence
here is not explained away by expensive verification in the way the
[Millennium](../math-millennium/README.md) and [Hilbert](../math-hilbert/README.md) zeros are. What
would change the reading is a denominator: nothing establishes that anybody has
pointed a system at this list, and an unattempted corpus produces a zero for
uninteresting reasons.

## Related literature

The entries, statuses, and citations are the project's own [@demaine2001topp]. The
comparison that gives this zero its force is with corpora that were deliberately
attempted: 9 of 353 open Erdős problems resolved by formal proof search
[@deepmind2026nexus], and a benchmark of over 100 unsolved problems built around
cheap automated verification on which frontier models still score near zero
[@arxiv2026horizonmath]. That records arrive in bursts with long gaps and no AI in
them is Sherry and Thompson's [@sherry2021fast]. The companion ledgers are
[Hilbert](../math-hilbert/README.md), [Landau](../math-landau/README.md),
[Thurston](../math-thurston/README.md), [Smale](../math-smale/README.md) and
[Millennium](../math-millennium/README.md); the corpus with measurable AI flow is
[Erdős](../math-erdos/README.md).
