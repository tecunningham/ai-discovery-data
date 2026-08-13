# Open-source CVEs represented in OSV

**Domain:** vulnerabilities
**Metric:** distinct CVE IDs linked to at least one active affected-package record in OSV, per quarter by earliest OSV publication date
**Coverage:** 2016–2026, partial through 2026-08-10
**Data:** quarterly [`osv-cves-by-quarter.csv`](osv-cves-by-quarter.csv); annual [`osv-cves-by-year.csv`](osv-cves-by-year.csv); severity labels in [`osv-severity-by-year.csv`](osv-severity-by-year.csv); finder credits in [`osv-credits-by-year.csv`](osv-credits-by-year.csv); every AI-marked CVE with its credit strings in [`osv-ai-cves.csv`](osv-ai-cves.csv)
**Upstream:** <https://storage.googleapis.com/osv-vulnerabilities/all.zip> (documentation at <https://google.github.io/osv.dev/data/>)
**Verdict:** accelerating — 2026 annualizes to about 2.3 times 2025, though source growth and disclosure processes can also bend this aggregate

![Quarterly distinct CVEs represented by active affected-package records in OSV.](discovery-cyber-osv-cves.png)

## The problem

OSV aggregates machine-readable vulnerability records from open-source package
ecosystems, project databases, Linux distributions, GitHub advisories and a
converted subset of NVD [@osv2026data]. That makes it a useful second
all-open-source view beside the all-software NVD count.

This series does not require a finder credit. Its purpose is to ask a prior,
simpler question: under one stable rule, did the volume of published
vulnerabilities accelerate? If it did, attribution and alternative mechanisms
are a separate interpretive step. Requiring every event to name an AI system
would discard most of the usable evidence before asking whether a bend exists.

A counted event is one distinct CVE identifier linked by at least one
non-withdrawn OSV record to an affected package. It is dated to the earliest
`published` date among all such records for that CVE.

## What the chart shows

The deduplicated count rises from 1,472 in 2016 to 5,317 in 2020, 10,821 in
2022, 12,269 in 2024 and 15,146 in 2025. There are 21,321 through 10 August
2026. Scaling that part-year mechanically gives about 35,100, or 2.3 times the
2025 count. The quarterly bars localize the rise: 2026-Q2 alone holds 10,193
distinct CVEs, more than any full year before 2022.

That is acceleration under this instrument, but not a clean structural break.
The history is uneven: 2022 rose sharply, 2023 fell, and growth resumed in 2024
and 2025 before the larger 2026 rise. A growing source population, backfills,
more CVE assignment, and faster advisory publication can all raise the bars
without a matching rise in newly discovered underlying flaws.

![OSV CVEs by ecosystem severity label, with the Unrated majority drawn as its own row.](severity-cyber-osv-cves.png)

Severity is the first cut at whether the extra volume is consequential, and
here it mostly cannot say: 34,163 of the 96,695 CVEs (35%) carry an ecosystem
severity label, and the heatmap draws the Unrated majority as its own row
rather than silently dropping it. The rated mix is also not a random sample.
Labels come from whichever upstream databases choose to assign them — GitHub's
advisory database does, the converted NVD subset and several distributions do
not — and that composition shifts over time, so a drift in the rated mix can be
a drift in which sources publish labels rather than in the vulnerabilities
themselves.

![OSV CVEs with finder credits; the uncredited majority is not drawn.](credits-cyber-osv-cves.png)

Finder credits are thinner still: 1,129 CVEs (1.2%) carry any credit, so the
credits chart draws that sliver alone and its note says the uncredited 99% is
not drawn. Within the sliver sit 24 AI-marked CVEs — two with an explicitly
stated AI method, the rest carrying an AI-lab affiliation only — each kept
with its full credit strings in [`osv-ai-cves.csv`](osv-ai-cves.csv) so the
classification can be re-audited. Nearly all come from the few projects whose
maintainers write credit strings at all, curl and Erlang/OTP above the rest.
These counts are a floor set by which ecosystems publish credits, not a
measurement of AI's share of discovery.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative distinct CVEs to date:

![Cumulative distinct CVEs to date.](cumulative-cyber-osv-cves.png)

## How the chart was built

[`fetch.py`](fetch.py) downloads OSV's official full-database archive, then
applies the same inclusion rule to every JSON record:

1. exclude withdrawn records and records with no affected package;
2. retain only CVE identifiers appearing as the record ID or an alias;
3. count each distinct CVE once, at its earliest valid `published` date.

The second step deliberately excludes OSV's malicious-package reports,
non-security distribution updates, and advisories that have no CVE. The third
collapses the multiple distribution and ecosystem advisories that often point
to the same flaw. If one advisory legitimately names several CVEs, each CVE
still counts once. CVEs first published after the repository's snapshot date
(lib/chart.py's `AS_OF_DATE`) are dropped, so a refetch reproduces the
committed window.

The merged per-CVE entries feed five CSVs: quarterly and annual counts, the
severity and credits cuts, and the AI-marked ledger. Severity is the
`database_specific.severity` label an ecosystem database assigns (GHSA-style
LOW/MODERATE/HIGH/CRITICAL, with MEDIUM folded into Moderate), taken at the
highest label across a CVE's records; records carrying only a CVSS vector stay
Unrated rather than being scored by a calculator this repository would then
have to defend. Credits are OSV `credits` names unioned across a CVE's records
and classified with the shared lib/credits.py rules; a CVE with no credit on
any record is uncredited, which is the majority and is its own column.

The plotted series starts in 2016. Earlier years in the present export contain
only tens or low hundreds of matching CVEs, a clear coverage discontinuity
rather than a credible measure of open-source disclosure volume. The current
quarter is outlined and labelled partial. [`figure.py`](figure.py) draws the
main chart from the quarterly CSV in the shared periodic-bar shape, in the
unattributed colour because the headline count carries no finder split; the
severity heatmap and the credits chart come from their annual CSVs, with the
coverage percentages in their subtitles and notes computed from the data at
draw time. [`check.py`](check.py) recomputes the numbers this document states
from the vendored CSVs.

## What it cannot support

- **The count does not attribute discoveries.** The headline series has no
  finder field, and the credit columns cover 1.2% of CVEs — a floor set by
  which ecosystems publish credits, not an attribution of the rest.
- **The severity mix is a coverage artifact first.** Most CVEs are Unrated,
  and which sources assign labels changes over time, so composition shifts can
  masquerade as severity shifts.
- **It is publication, not discovery.** The date is an advisory's publication
  date; discovery, CVE assignment and publication can be far apart.
- **The denominator is not fixed.** OSV adds sources and packages while the
  open-source software population itself grows.
- **The snapshot can revise history.** A newly imported or corrected record can
  add a CVE to an earlier publication year on the next fetch.
- **CVE-only is a conservative slice of OSV.** Valid GHSA-only, ecosystem-only
  and project advisories are omitted so that duplicate records can be collapsed
  with a simple, auditable identifier rule.
- **Annualization is only arithmetic.** The 2026 projection assumes an even
  publication rate and is not a forecast.

## LLM contributions

The aggregate count remains unattributable, and that does not disqualify the
series: the chart is a detector for a change in a consistently defined output,
not an estimator of what share AI caused. The credits view adds a thin evidence
ledger on top — the 24 AI-marked CVEs in
[`osv-ai-cves.csv`](osv-ai-cves.csv) — but at 1.2% credit coverage that is a
floor, not a share. A bend can motivate comparison with finder-credited
fixed-codebase series and contemporaneous evidence about tools and disclosure
pipelines; it cannot supply causation by itself.

That distinction also works in the other direction. A flat OSV series would
count against a broad acceleration claim even if a handful of individual
records carried strong AI attribution.

## Related literature

OSV documents both the full export and its mix of native and converted data
sources [@osv2026data]. The broader comparator is
[all CVEs published by NVD](../cyber-nvd-disclosed/README.md); the narrower
programme-level slice is [OSS-Fuzz](../cyber-oss-fuzz/README.md). Dense finder
credits live in the project-level [curl](../cyber-curl/README.md),
[OpenSSL](../cyber-openssl/README.md) and
[Firefox](../cyber-firefox/README.md) series; here they exist only for the
1.2% sliver above.
