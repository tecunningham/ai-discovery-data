# Millennium Prize Problems

**Domain:** mathematics
**Metric:** cumulative prize problems scored resolved, out of 7
**Coverage:** 2000–2026, with one dated resolution in 2003
**Data:** [`millennium-problems.csv`](millennium-problems.csv)
**Upstream:** <https://www.claymath.org/millennium-problems/>
**Verdict:** no acceleration

![Cumulative resolved Millennium Prize Problems, flat at one since Perelman's 2003 Poincaré result.](discovery-math-millennium.png)

## The problem

The Clay Mathematics Institute named seven problems in 2000 and attached a
million dollars to each. They are what the public means by open mathematics, and
that is the whole of their value here: the list is a ceiling check, the place to
look when someone claims AI is solving the great problems.

A "discovery" in this series is a prize problem being resolved. Unlike the other
ledgers scored in this collection, the list needs no subproblem splitting and has
no contested rows: seven problems, one resolved, six open. That cleanliness is
also what makes it useless as a rate.

It is the worst instrument in the collection for measuring anything, and it is
worth being explicit about why, because the low count is easy to misread. The
list has seven rows, so its finest possible resolution is one seventh. The
problems were selected for depth. And verification is extremely expensive:
Perelman's Poincaré work reached arXiv in 2002 and 2003, and the prize was not
announced until 2010, which is the checking cost made visible. Under any story in
which AI results arrive first where a candidate answer can be scored cheaply, the
predicted AI count here is zero, and the observed count of zero therefore
discriminates between almost nothing.

## What the chart shows

One step, in 2003, and a flat line for twenty-three years either side of it. Of
the seven rows, one is resolved and six are open: Birch–Swinnerton-Dyer, the
Hodge conjecture, Navier–Stokes existence and smoothness, P versus NP,
Yang–Mills existence and mass gap, and the Riemann hypothesis. No marker is red,
because no row carries an AI attribution.

There is nothing else in the reading. A single event cannot show a slope, and the
absence of events since cannot distinguish a hard frontier from a short window: at
one resolution per twenty-six years, a twenty-three-year gap is what the series
looks like when nothing has changed.

The one thing the chart does establish is a bound on the strongest possible claim.
Whatever AI has contributed to mathematics through mid-2026, it has not resolved
a Millennium problem, and no credible claim to have done so exists in the sources
behind this collection.

## How the chart was built

[`figure.py`](figure.py) calls the shared `problem_list_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), which reads
`millennium-problems.csv`, keeps the rows whose `status` is
`resolved` with a non-empty `resolved_year`, and draws the cumulative count as a
step function from the 2000 `list_year` to the present. The header text reports
the status breakdown, and the source note names the `source` column, which for
every row here is the Clay Mathematics Institute.

The resolution year is 2003, taken from the arXiv postings; the row's `notes`
field records that the preprints ran 2002 to 2003 and that the prize was
announced in 2010. Which of those three dates counts as the resolution is a real
choice, and the chart takes the earliest defensible one. On a series with one
event, that choice moves the only step by up to seven years.

No `ai_problem` argument is passed, because there is no such row. The y-axis is
forced to integers and the axis limits leave room for two, so the flatness is
visible as flatness rather than as a chart that has been zoomed until nothing
moves.

There is no `fetch.py`. Seven rows, hand-scored from the Clay Mathematics Institute's own pages; a feed would be more machinery than a list that has moved once in twenty-six years deserves.

## What it cannot support

- **Seven rows cannot carry a rate.** The finest change this series can register
  is one seventh, and it has registered one event in its lifetime.
- **Verification is expensive**, so the lag between a solution and its
  acknowledgement is measured in years, and any recent result would not yet be
  visible here.
- **The resolution date is a choice.** Preprints 2002–2003, prize 2010; the chart
  uses 2003.
- **The rows overlap other lists.** Riemann appears on [Hilbert](../math-hilbert/README.md)
  and [Smale](../math-smale/README.md) too, and P versus NP on Smale, so this is not an
  independent sample of hard problems.
- **Selection against cheap verification makes the zero uninformative.** These
  problems are chosen to be deep, and depth here means no mechanical check
  exists, which is the condition under which every AI result in this collection
  has failed to appear.

## LLM contributions

None, and none claimed. The list stands where it stood in 2003.

Where a series has no AI step at all, the useful question is whether the absence
is informative, and here it mostly is not. A zero on seven problems selected for
depth and expensive verification is the predicted outcome under both the
optimistic and the pessimistic readings of AI's mathematical ability, so it
cannot separate them. The place where the same question does get an informative
answer is [Smale](../math-smale/README.md), where one row fell in 2026 to an AI-assisted
finite counterexample that could be machine-checked, and [Erdős](../math-erdos/README.md),
where the problems are numerous enough and cheap enough to verify that a flow can
be measured at all.

## Related literature

The seven problems and their status are the Institute's own
[@clay2000millennium]. The argument that scored mathematical progress lives where
verification is cheap is made explicitly by benchmark designers who selected
problems on that basis and found frontier models scoring near zero even so
[@arxiv2026horizonmath]. That flat stretches in record series are normal, with no
AI anywhere in them, is Sherry and Thompson's finding across algorithm families
[@sherry2021fast]. The companion ledgers are [Hilbert](../math-hilbert/README.md),
[Smale](../math-smale/README.md) and [TOPP](../math-topp/README.md).
