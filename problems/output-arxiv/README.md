# arXiv submissions

**Domain:** outside the three domains
**Metric:** research output; preprints submitted to arXiv per month
**Coverage:** 1991-07 to 2026-07, monthly, the last month partial
**Data:** [`arxiv-monthly.csv`](arxiv-monthly.csv)
**Upstream:** <https://arxiv.org/stats/monthly_submissions>
**Verdict:** accelerating — on volume, which is not discovery

![arXiv submissions per month, 1991 to 2026, with January 2026 onward shaded.](output-arxiv-submissions.png)

## The problem

Does the volume of research output bend upward in the agent era? arXiv is the
best-measured answer available: one organization has counted every preprint
submitted to it since 1991, publishes the series itself, and has no stake in
what the count is used to argue.

This is a contrast case, not a discovery series. Every folder in the three
domains asks whether some record, bound or vulnerability count moved. This one
asks whether the flow of artifacts moved, which is far easier to measure and a
much weaker thing to establish. A submission is not a result.

## What the chart shows

Submissions rose from 17,271 in November 2022, the month ChatGPT was released,
to 32,040 in June 2026, the last complete month: 86% in three years and seven
months, against decades in which the series took roughly a decade to double.
The bend is visible around 2023 and continues through the shaded 2026 period.

The trailing point is drawn open because the last row is the month in progress
at fetch time, and an incomplete month read as a complete one would look like a
collapse. Every figure in the chart is computed from the CSV when the chart is
drawn, so the annotation cannot survive a refetch that changes the numbers.

## How the chart was built

[`fetch.py`](fetch.py) downloads arXiv's own monthly-submissions file and keeps
two columns. The raw download carries a `historical_delta` column, nonzero only
for corrections to 1991–1997, which is dropped.

[`figure.py`](figure.py) draws the series through
[`lib/families.py`](../../lib/families.py)'s shared volume shape: years on the
x-axis, the count on the y-axis, January 2026 onward shaded, an open marker on
a part period. The five volume folders use that one shape so a difference in
appearance between any two of them is a difference in the data. It is drawn in
slate rather than the blue the other charts use for human or uncredited finders,
because this series has no authorship field at all.

## What it cannot support

- **No authorship labels.** The series does not record whether a human or a
  model wrote the paper, so no AI share can be read off it and the attribution
  of the bend is open.
- **A submission is not a discovery.** These count artifacts produced. The
  domain folders count results, and the two need not move together.
- **No denominator of effort.** Nothing here measures how many researchers were
  working, so output per unit of input cannot be separated from more input.
- **Composition is invisible.** A rise is consistent with more short papers,
  more salami-slicing, or more of the same kind of work, and the series cannot
  distinguish those from more research.
- **Field mix is not held fixed.** arXiv's growth over 35 years includes whole
  disciplines joining it, which is a change in the platform rather than in
  science.

## LLM contributions

Nothing in this series is attributable to a model, by construction, and that is
worth stating plainly rather than leaving as an omission: it is a count of
submissions with no authorship field, so the rise is consistent with models
writing the papers, with more people writing more papers, or with both.

The timing is suggestive and no more. The bend begins around 2023, which is when
general-purpose assistants became widely available, but the same period covers a
post-pandemic expansion in research employment and the continued migration of
fields onto the platform.

## Related literature

The comparison this folder exists for is with the rest of the collection: set
it against [curl](../cyber-curl/README.md), where a fixed codebase yields a step
change in disclosures, and against the mathematics folders, where the records
barely move. [Crossref](../output-crossref/README.md) is the control on this
series specifically — formal publishing rose steeply through the same period
with no clean bend, so a rising volume curve is not by itself evidence of
anything new. The same volume-against-discovery distinction appears in the
vulnerability counts: NIST reports 263% growth in CVE submissions between 2020
and 2025 while its own enrichment of nearly 42,000 CVEs in 2025 failed to keep
pace [@nist2026cvegrowth], which is a statement about throughput rather than
about what was found.
