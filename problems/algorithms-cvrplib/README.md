# CVRPLIB X-instance record frontier

**Domain:** algorithms
**Metric:** better best-known objectives and later optimality proofs recorded for a fixed cohort of 100 CVRP X instances
**Coverage:** 2015–2026, 289 event rows posted through 2026-07-04
**Data:** [`cvrplib-x-frontier.csv`](cvrplib-x-frontier.csv), one instance–posting-date–objective–event tuple per row
**Upstream:** <https://galgos.inf.puc-rio.br/cvrplib/index.php/en/updates/>
**Verdict:** declining — objective improvements are concentrated in 2015–2021; later activity is mostly proof

![Annual better objectives and optimality proofs in the fixed CVRPLIB X cohort.](discovery-algorithms-cvrplib.png)

## The problem

The capacitated vehicle-routing problem asks for minimum-cost routes that serve
customers without exceeding vehicle capacity. CVRPLIB accepts improved
solutions, checks them, and posts each change to its chronological Updates
ledger. That makes the site unusually close to a public record book rather than
an annual competition snapshot.

This series freezes the 100 X instances introduced as one designed cohort. A
discovery is either a newly posted lower objective or a later proof that the
standing objective is optimal. Those are kept separate: finding a better route
and proving no better route exists are different algorithmic achievements.

## What the chart shows

The vendored extract contains 267 better-objective events and 22
optimality-proof events, or 289 event rows in total, over 2015–2026. Activity is
very bursty: large batches were posted in 2015, 2016 and especially 2020. The
last X-objective changes before the current year were posted in June 2021.

The frozen cohort also corrects a claim that is easy to make from the whole
site: 2024 has no event for an X instance. Proofs of already-standing objectives
produce the only X-cohort entries in 2022, 2023 and 2025. Three objective rows
appear in the July 2026 posting: one for X-n979-k58 and two successive values for
X-n1001-k43. On this fixed cohort, the record-improvement rate is declining,
not continuously dense.

## How the chart was built

[`fetch.py`](fetch.py) walks all five pages of the Updates ledger, selects
instance names matching the X convention, normalizes two historical omissions
of the `n`, and writes a row for each objective improvement or proof phrase.
Combined “improved and proven optimal” announcements intentionally create two
rows for an instance. [`figure.py`](figure.py) counts those rows by posting year
and stacks proofs above objective changes without treating them as the same
event type. [`check.py`](check.py) recomputes the totals quoted here.

The 2026 announcement reports receipt dates inside a July 4 posting. The data
uses the public ledger date consistently for every row; it does not silently mix
receipt, paper and posting dates.

## What it cannot support

- The update ledger begins after the X instances were introduced; it is not a
  reconstruction of their pre-ledger initial solutions.
- A batch posting can contain work performed over a longer interval, so annual
  counts are publication cadence as well as discovery cadence.
- The parser classifies the page's words. It does not independently verify that
  every “improved” value beats the previous value, although CVRPLIB says it
  checks submissions.
- Freezing X avoids benchmark-composition drift but excludes later Loggi, ORTEC,
  XML and XL records—including the large 2026 BKS Challenge.
- Event counts do not weight the magnitude or difficulty of improvements.

## LLM contributions

None are identified in the update text for this fixed cohort. The 2026 entries
are attributed to named optimization researchers, not to a language model or
agent. This is an authorship statement about the ledger, not a claim that no AI
component was used anywhere in a solver.

## Related literature

The X cohort and its design are described by Uchoa and collaborators in
[New benchmark instances for the Capacitated Vehicle Routing Problem](https://doi.org/10.1016/j.ejor.2016.08.012).
The source ledger states that submitted improvements are checked and that an
optimality claim requires a citable method. The separate 2026
[BKS Challenge overview](https://galgos.inf.puc-rio.br/cvrplib/index.php/en/bks_challenge/overview)
explains why its new XL instances are not joined to this fixed-cohort curve.
