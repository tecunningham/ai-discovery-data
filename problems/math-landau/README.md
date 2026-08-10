# Landau's problems

**Domain:** mathematics
**Metric:** unresolved scored rows remaining, out of 4 scored rows
**Coverage:** 1912–2026, with no dated resolution anywhere in that span
**Data:** [`landau-problems.csv`](landau-problems.csv)
**Upstream:** <https://en.wikipedia.org/wiki/Landau%27s_problems>
**Verdict:** no acceleration

![Unresolved scored rows over time.](discovery-math-landau.png)

## The problem

Landau named four problems about the primes at the 1912 International Congress
of Mathematicians: Goldbach's conjecture, the twin prime conjecture, Legendre's
conjecture that a prime lies between consecutive squares, and the infinitude of
primes of the form $n^2+1$. All four are still open.

A "discovery" in this series is a row moving to resolved, on the year a secondary
consensus account gives. There are four rows, no subproblem splitting, and no
contested classifications, so the ledger is as simple as a ledger gets — and as
coarse.

It is in the collection as a baseline rather than as a test. A famous list that
has not moved in one hundred and fourteen years is what the pre-AI resolution
cadence of prestige mathematics looks like at its slowest, and it is the
comparison against which a claim about AI and famous open problems has to be
read. The instrument warning that applies to [Hilbert](../math-hilbert/README.md)
applies with more force here: these are problems selected for depth, and depth
here means no candidate answer can be scored cheaply, which is the condition
under which every AI result in this collection has arrived.

## What the chart shows

Nothing, and that is the reading. The unresolved line is flat at four across the
whole span, the header text records four scored rows with none resolved, and the
chart carries an annotation saying no row has been resolved since the list was
posed. No marker is red because there are no markers at all.

The one thing this establishes is a bound. Whatever AI has contributed to
mathematics through mid-2026, it has not closed a Landau problem, and no source
behind this collection claims otherwise.

## How the chart was built

[`figure.py`](figure.py) calls the shared `problem_list_chart()` shape in
[`../../lib/families.py`](../../lib/families.py), which reads
`landau-problems.csv`, keeps the rows whose `status` is `resolved` with a
non-empty `resolved_year`, and draws the count of still-unresolved rows as a step function from
the 1912 `list_year` to the present. Here that set is empty, so the function
takes its no-resolution path: the flat line and the row-count annotation are
drawn as usual, and the marker legend is replaced by a sentence, because legend
swatches sitting on a line at zero read as resolution landmarks.

The rows are transcribed by hand from the consensus ledger named in the `source`
column, so there is no `fetch.py` in this folder. There is no machine-readable
upstream to rebuild from: the status of a famous conjecture is a judgment in the
literature rather than a feed.

No `ai_problem` argument is passed, because there is no such row.

## What it cannot support

- **Zero events cannot carry a rate.** A series with no resolutions in it has no
  slope to compare, in either direction, and the flat line through 2026 is the
  same flat line it showed in 1950.
- **Four rows is the coarsest ledger here.** The finest change it can register is
  one quarter.
- **A binary status hides real progress.** Bounded gaps between primes were
  established in 2013 by Zhang and sharpened by the Polymath follow-ons, and the
  ternary Goldbach problem was settled by Helfgott, none of which moves a row on
  this ledger. The series measures falls, not advances.
- **The rows overlap other lists.** Goldbach and twin primes are also scored on
  Hilbert's list, as its row 8b [@wikipedia2026hilbert], so this is not an
  independent draw.
- **Resolution landmarks are not effort-adjusted discovery rates**, and effort on
  the primes has certainly risen over the century.

## LLM contributions

None. No AI system has resolved a Landau problem, and none is credited with
partial progress on one in any source behind this collection.

## Related literature

The four problems and their statuses come from the consensus ledger linked above,
which has no bibliography entry here; the overlapping Hilbert row is
[@wikipedia2026hilbert]. That a record series can sit still for decades with no
AI anywhere in it, so that flatness is not evidence of an exhausted frontier, is
Sherry and Thompson's finding across algorithm families [@sherry2021fast]. That
scored mathematical progress arrives where verification is cheap — which these
four problems are the opposite of — is the explicit selection rule of the
benchmark designers who built a problem set on it [@arxiv2026horizonmath]. The
companion ledgers are [Hilbert](../math-hilbert/README.md),
[Thurston](../math-thurston/README.md), [Smale](../math-smale/README.md),
[Millennium](../math-millennium/README.md) and [TOPP](../math-topp/README.md);
the corpus where an AI-contributed flow is measurable at all is
[Erdős](../math-erdos/README.md).
