# Open-source CVEs represented in OSV

**Domain:** vulnerabilities
**Metric:** distinct CVE IDs linked to at least one active affected-package record in OSV, by earliest OSV publication date
**Coverage:** 2016–2026, partial through 2026-08-10
**Data:** [`osv-cves-by-year.csv`](osv-cves-by-year.csv)
**Upstream:** <https://storage.googleapis.com/osv-vulnerabilities/all.zip> (documentation at <https://google.github.io/osv.dev/data/>)
**Verdict:** accelerating — 2026 annualizes to about 2.3 times 2025, though source growth and disclosure processes can also bend this aggregate

![Annual distinct CVEs represented by active affected-package records in OSV.](discovery-cyber-osv-cves.png)

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
2022, 12,269 in 2024 and 15,145 in 2025. There are 20,747 through 10 August
2026. Scaling that part-year mechanically gives about 34,100, or 2.3 times the
2025 count.

That is acceleration under this instrument, but not a clean structural break.
The history is uneven: 2022 rose sharply, 2023 fell, and growth resumed in 2024
and 2025 before the larger 2026 rise. A growing source population, backfills,
more CVE assignment, and faster advisory publication can all raise the bars
without a matching rise in newly discovered underlying flaws.

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
still counts once.

The plotted series starts in 2016. Earlier years in the present export contain
only tens or low hundreds of matching CVEs, a clear coverage discontinuity
rather than a credible measure of open-source disclosure volume. The current
year is outlined and labelled partial. [`figure.py`](figure.py) uses the shared
annual-bar shape and the unattributed colour because OSV has no consistent
finder field.

## What it cannot support

- **It does not attribute discoveries.** Nothing in this CSV identifies a
  human, model, fuzzer, or vendor as the finder.
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

No individual contribution is separable here, and that does not disqualify the
series. The chart is a detector for a change in a consistently defined output,
not an estimator of what share AI caused. A bend can motivate comparison with
finder-credited fixed-codebase series and contemporaneous evidence about tools
and disclosure pipelines; it cannot supply causation by itself.

That distinction also works in the other direction. A flat OSV series would
count against a broad acceleration claim even if a handful of individual
records carried strong AI attribution.

## Related literature

OSV documents both the full export and its mix of native and converted data
sources [@osv2026data]. The broader comparator is
[all CVEs published by NVD](../cyber-nvd-disclosed/README.md); the narrower
programme-level slice is [OSS-Fuzz](../cyber-oss-fuzz/README.md). Finder credits
are available only in the project-level [curl](../cyber-curl/README.md),
[OpenSSL](../cyber-openssl/README.md) and
[Firefox](../cyber-firefox/README.md) series.
