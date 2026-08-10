# Thurston's 24 questions

**Domain:** mathematics
**Metric:** cumulative ledger rows scored resolved, out of 24 scored rows
**Coverage:** 1982–2026, with dated resolutions running 1993–2013
**Data:** [`thurston-questions.csv`](thurston-questions.csv)
**Upstream:** <https://en.wikipedia.org/wiki/Thurston%27s_24_questions>, cross-checked against Agol's status note at <https://mathoverflow.net/questions/265493/thurstons-24-questions-all-settled>
**Verdict:** no acceleration

![Cumulative dated resolutions among Thurston's 24 questions, clustered in 2012 and 2013 and flat since.](discovery-math-thurston.png)

## The problem

Thurston closed his 1982 survey of three-dimensional manifolds, Kleinian groups
and hyperbolic geometry with twenty-four questions, and they organized the field
for the next thirty years. Twenty-two of them have since been answered.

A "discovery" in this series is a row moving to resolved, on the year a secondary
consensus account gives. The list needs no subproblem splitting and has no
contested rows: twenty-four questions, twenty-two resolved, two open — question
19, on the topology and geometry of arithmetic quotients of hyperbolic space, and
question 23, on whether hyperbolic volumes are rationally independent.

It is in the collection as a baseline, and it is the most useful of the prestige
baselines because it is the one that moved. The other famous lists here are
mostly stationary, which makes it easy to read a flat line as a property of
famous mathematics rather than of a particular list. Thurston's questions show
what a prestige list looks like when it is being answered: a long thin start, then
a burst that nearly empties it, all of it human, all of it before the agent era.

## What the chart shows

Twenty-two resolutions between 1993 and 2013, then thirteen flat years. Twelve
had fallen by 2009; then ten arrived in 2012 and 2013 alone, the cluster
containing Brock, Canary and Minsky on the ending lamination conjecture and
Agol's virtually Haken and virtually fibered theorems. Perelman's geometrization
work, dated 2003, sits in the middle of the run rather than at its head.

Nothing lands in the shaded 2026 period and no marker is red, because no row
carries an AI attribution.

The burst is the part worth carrying away. A cluster of ten resolutions inside
two years, on a list twenty years old at the time, happened with no AI anywhere in
it — so a similar cluster inside the agent era would not by itself be an AI
signature. The thirteen years since are the other half of the same point: the two
questions still open are the ones nobody has been able to touch, and a flat right
edge is what that looks like.

## How the chart was built

[`figure.py`](figure.py) calls the shared `problem_list_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), which reads
`thurston-questions.csv`, keeps the rows whose `status` is `resolved` with a
non-empty `resolved_year`, sorts them by year and then `problem_id`, and draws the
cumulative count as a step function from the 1982 `list_year` to the present. The
header text counts the remaining rows by status, and the source note is taken from
the `source` column.

The rows are transcribed by hand from the ledger named in that column, so there is
no `fetch.py` in this folder. There is no machine-readable upstream: the status of
a question in geometric topology is a judgment in the literature rather than a
feed.

Two scoring conventions are visible in the chart and worth naming. Where the
source gives a span rather than a year — 1986–1993 for geometric tameness,
2000–2013 for the global theory of hyperbolic Dehn surgery, 2009–2012 for
Cannon–Thurston maps — the `resolved_year` is the end of the span, which pushes
those steps to the right and tightens the 2012–2013 cluster. And questions 20 to
22 ask for software rather than for theorems; they are counted resolved, as the
source counts them, against SnapPea and its successors, at a conventional year of
2000 for a process that ran through the 1990s and 2000s.

No `ai_problem` argument is passed, because no row credits an AI system.

## What it cannot support

- **Resolution landmarks are not effort-adjusted discovery rates.** The dates say
  when something fell, not how much work it took, and the 2012–2013 cluster rests
  on a decade of accumulated machinery.
- **The dates are span ends.** Three rows compress a multi-year effort into its
  final year, so the cluster is partly an artifact of the dating rule.
- **Three of the twenty-two falls are software**, not proofs, and their year is a
  convention rather than a dated event.
- **Two open rows cannot register a rate.** With twenty-two of twenty-four already
  answered, the series has almost no room left to move, so its flatness since 2013
  is close to uninformative about anything recent.
- **One secondary ledger.** Every row is transcribed from a consensus account,
  cross-checked against one expert's public status note, rather than from
  independent review of the literature.
- **The rows overlap other lists.** Question 1 contains the Poincaré conjecture,
  which is also the resolved row on the [Millennium](../math-millennium/README.md)
  list, so these series are not independent.

## LLM contributions

None. No row in this ledger is attributed to an AI system, and the most recent
resolution on it is human work from 2013, a decade before the agent era.

The absence carries little information about capability. Both remaining questions
are open-ended enough that a resolution would arrive as a research programme
rather than as a checkable object, which is the condition under which nothing in
this collection has registered an AI result.

## Related literature

The questions and their statuses come from the consensus ledger and the expert
status note linked above, neither of which has a bibliography entry here. That
record series arrive in bursts with long gaps and no AI in them, which is what
makes the 2012–2013 cluster the useful part of this series, is Sherry and
Thompson's finding across algorithm families [@sherry2021fast]. That AI results
have arrived where a candidate answer can be checked cheaply is the explicit
selection rule of benchmark designers who built a problem set on it
[@arxiv2026horizonmath], and the one place a denominated AI rate on real open
problems exists is formal proof search over the Erdős corpus
[@deepmind2026nexus]. The companion ledgers are
[Hilbert](../math-hilbert/README.md), [Landau](../math-landau/README.md),
[Smale](../math-smale/README.md), [Millennium](../math-millennium/README.md) and
[TOPP](../math-topp/README.md); the corpus with measurable AI flow is
[Erdős](../math-erdos/README.md).
