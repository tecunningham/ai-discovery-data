# arXiv submissions

**Domain:** outside the three domains
**Metric:** research output; preprints submitted to arXiv per month
**Coverage:** 1991-07 to 2026-08, monthly, the last month partial
**Data:** [`arxiv-monthly.csv`](arxiv-monthly.csv); per-category [`arxiv-monthly-by-category.csv`](arxiv-monthly-by-category.csv)
**Upstream:** <https://arxiv.org/stats/monthly_submissions>, with per-category counts from <https://oaipmh.arxiv.org/oai>
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
to 29,687 in July 2026, the last complete month: 72% in three years and eight
months, a pace the series last sustained in the late 1990s; across the two
decades before ChatGPT it took seven to nine years to double.
The bend is visible around 2023 and continues through the shaded 2026 period.

The trailing point is drawn open because the last row is the month in progress
at fetch time, and an incomplete month read as a complete one would look like a
collapse. Every figure in the chart is computed from the CSV when the chart is
drawn, so the annotation cannot survive a refetch that changes the numbers.

![arXiv submissions per month by top-level field group.](output-arxiv-by-field.png)

The by-field split says where the bend lives. Computer science rose from 5,967
monthly submissions in November 2022 to 12,409 in July 2026, and has stayed
above physics every month since August 2023 — the first time in the archive's
history physics was not its largest field. Physics rose 41% over the same
window, mathematics 66%, from 3,143 to 5,216. Each paper is counted once,
under its primary category, grouped to arXiv's own top level; `math-ph` sits
with physics because arXiv puts it there.

![Monthly arXiv submissions for every mathematics subfield.](output-arxiv-math-subfields.png)

The subfield grid is the math story at full resolution: every `math.*` primary
category, one panel each, sorted by total volume and scaled independently. The
recent surge is not uniform. Combinatorics reached 743 submissions in July
2026 against a 2024 monthly average of 342, and analysis of PDEs, optimization
and control, numerical analysis and number theory show the same late spike,
while classical analysis and K-theory sit near their decade-old levels.
Mathematics as a whole ran at 1.6 times its 2024 monthly average in July 2026.
The legacy archives that predate the 1998 subfield taxonomy — `alg-geom`,
`q-alg`, `dg-ga`, `funct-an` — are mapped to their modern names, so the older
panels keep their early-1990s history.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative submissions to date:

![Cumulative submissions to date.](cumulative-output-arxiv.png)

## How the chart was built

[`fetch.py`](fetch.py) downloads arXiv's own monthly-submissions file and keeps
two columns. The raw download carries a `historical_delta` column, nonzero only
for corrections to 1991–1997, which is dropped.

[`figure.py`](figure.py) draws the total series through
[`lib/families.py`](../../lib/families.py)'s shared volume shape: years on the
x-axis, the count on the y-axis, January 2026 onward shaded, an open marker on
a part period. The three volume folders use that one shape so a difference in
appearance between any two of them is a difference in the data. It is drawn in
slate rather than the blue the other charts use for human or uncredited finders,
because this series has no authorship field at all.

The per-category file behind the two field charts is built by
[`fetch_categories.py`](fetch_categories.py), which is run by hand rather than
by `make fetch`. It counts each paper once, in the month of its first
version's submission date and under its primary (first-listed) category, and
it has two interchangeable inputs: arXiv's official metadata snapshot — the
~5 GB `arxiv-metadata-oai-snapshot.json` distributed via Kaggle, which needs a
login to download and is kept beside this document but deliberately not
committed — and a no-credentials OAI-PMH harvest of the same metadata, which
walks about 2,400 resumption pages at the pace arXiv meters out and takes the
better part of a day. Both produce the same aggregation; papers first
submitted after the repository's snapshot date are dropped. A few dozen
migrated records carry v1 dates before arXiv opened in July 1991, and the
charts start at the launch month. The field grouping and the legacy-archive
mapping live at the top of `figure.py`, and an archive the mapping does not
know fails the build rather than landing in a silent bucket.

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
- **Primary categories undercount interdisciplinary work.** Each paper counts
  once, under its first-listed category; cross-lists are ignored, so a field's
  line misses papers that touch it secondarily, and a shift in cross-listing
  habits moves no line here.
- **Category labels are the authors' and moderators' choices.** A subfield's
  rise can reflect labelling fashion as well as activity, and arXiv
  occasionally reclassifies old papers, which moves history on a refetch.

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
