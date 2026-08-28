# OpenSSL vulnerability disclosures

- **Domain:** vulnerabilities
- **Role:** discovery series
- **Metric:** vulnerabilities disclosed per quarter, split by finder provenance: corroborated AI method, AI affiliation with method unverified, conventional or fuzzing credit, or no reporter credit
- **Coverage:** 2002–2026, partial through 2026-08-05
- **Data:** CVE-level [`openssl-cves.csv`](openssl-cves.csv); annual [`openssl-by-year.csv`](openssl-by-year.csv); per-finder [`openssl-finders.csv`](openssl-finders.csv)
- **Upstream:** <https://github.com/openssl/release-metadata/tree/main/secjson>
- **Verdict:** accelerating — 39 CVEs by 2026-08-05 against 6 in all of 2025; the largest prior full years were 35 in 2016 and 32 in 2015

![Quarterly OpenSSL vulnerability disclosures, separating corroborated AI discovery from affiliation-only credits.](discovery-cyber-openssl.png)

## Definition

OpenSSL is a widely deployed, security-critical cryptographic library. Its
official security metadata provides a publication date, project severity,
reporter and remediation credits, affected version ranges and references for
each CVE.

OpenSSL is a fixed *project*, not a fixed body of code. Code size, features,
supported versions and bug surface change, and new bugs continue to be
introduced: the January 2026 QUIC cipher-handling vulnerability
CVE-2025-15468 affected code added with QUIC support in OpenSSL 3.2. The
series therefore cannot assume that a fixed stock of findable bugs should
deplete, or rule out more software to search as an explanation for a rising
count.

A disclosure here is one CVE in the year of OpenSSL's `datePublic`. It is
not a discovery date, a count of bugs introduced or a measure of bugs
remaining. Finder provenance identifies who reported a CVE and, when
separately corroborated, the reported method; it does not measure search
effort. In this folder, "corroborated AI" means CVE-level evidence that an
AI system produced the finding, and 27 of 39, or 69%, of the 2026 CVEs
carry an AI-lab affiliation or an explicit AI method marker — a wider band
than the corroborated one, because affiliation alone is not counted as
method evidence.

## Facts

- **2026 (through 2026-08-05):** 39 CVEs; 18 corroborated AI, 9
  AI-affiliated with method unverified, 12 with conventional or fuzzing
  credits, 0 uncredited
- **prior full-year peaks:** 35 in 2016 and 32 in 2015
- **same-period comparison (1 January to 5 August):** 39 in 2026 versus 27
  in 2015, 19 in 2016 and 16 in 2023, the three largest prior same-period
  counts
- **2025:** 6 CVEs; 3 corroborated AI
- **2026 publication batches:** coordinated publications on 27 January, 13
  March, 7 April, 9 June and 5 August contained 12, 1, 7, 18 and 1 CVEs
- **2026 severity by provenance (OpenSSL's own ratings):**

| Finder provenance | Critical | High | Moderate | Low |
|---|---:|---:|---:|---:|
| Corroborated AI | 0 | 2 | 1 | 15 |
| AI-affiliated, method unverified | 0 | 0 | 3 | 6 |
| Conventional/fuzzing | 0 | 0 | 3 | 9 |
| No reporter credit | 0 | 0 | 0 | 0 |

- **baseline severity (2015–2025):** half of all rated CVEs were Low and
  15% were High or Critical
- **2026 Low shares by cohort:** 75% for conventional or fuzzing credits,
  67% for affiliation-only credits, and 83% for the corroborated-AI set,
  which also holds both High-severity CVEs of 2026

![OpenSSL disclosures by severity: counts by year and finder provenance since 2015.](severity-cyber-openssl.png)

The severity chart draws the table's cohorts in their multi-year trend: one
grid per finder-provenance cohort, years across, OpenSSL's ratings down,
every cell printing how many CVEs it holds. It starts in 2015 because the
structured metadata carries no severity before 2014, and an unrated record
is missing data rather than a low-severity one. Annual sizes run from three
to thirty-five CVEs, so the annual mix swings widely on small counts.

![OpenSSL vulnerabilities by coordinated 2026 publication batch.](batches-cyber-openssl.png)

The batch chart shows the 2026 total arriving on five coordinated
publication dates rather than at a steady seven-month rate.
Publication-batch size can reflect release coordination and remediation
timing as well as the rate at which bugs were found.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as cumulative disclosures to date:

![Cumulative disclosures to date.](cumulative-cyber-openssl.png)

## Method

[`fetch.py`](fetch.py) downloads one tarball for OpenSSL release-metadata
commit
[`597a9a75044f`](https://github.com/openssl/release-metadata/commit/597a9a75044fb94b2823d111fd96ad9607a38189),
the final metadata correction on 5 August 2026. The pin makes the vendored
snapshot reproducible. It parses all 273 `secjson/CVE-*.json` records and
fails on a missing publication date or severity; coverage is 273 of 273
structured records, with no silent omissions. Reporter/finder credits are
kept separate from remediation developers.

[`openssl-cves.csv`](openssl-cves.csv) is the auditable, one-row-per-CVE
source for both aggregates. It records:

- CVE, publication date, OpenSSL severity and reporter;
- independent `explicit_ai`, `ai_affiliated` and `fuzz` booleans;
- the finding-level AI evidence URL, affected version ranges and OpenSSL's
  structured `source.discovery` value;
- a pinned source URL, SHA-256 of the source JSON and metadata commit.

Here `explicit_ai` means *corroborated AI method*, not employment at an AI
company. It is `yes` only in these cases:

1. A separate source enumerates the CVE as produced by an AI system:
   Aisle's three September 2025 findings, all 12 January 2026 findings, and
   five April 2026 findings [@aisleopenssl2025; @aisleopenssljan2026;
   @aisleopensslapr2026].
2. The official reporter text itself names the method, which applies to
   CVE-2026-45447, quoted in AI attribution below.

The Aisle evidence is external to OpenSSL but is still the vendor's own
finding-level claim, not a neutral replication. OpenSSL independently
confirms the reporter identities but records `source.discovery` as
`UNKNOWN`; that field is not converted into AI attribution. Bare Aisle or
Anthropic affiliations without CVE-level method evidence remain
`ai_affiliated=yes`, `explicit_ai=no`.

AI and fuzz are independent booleans, so a future AI-guided fuzzing credit
can be true in both columns. The mutually exclusive chart bands are only a
display rule, applied in this order: corroborated AI; affiliation-only;
credited conventional/fuzzing; no reporter.

[`figure.py`](figure.py) derives the four-band quarterly chart, the
event-level 2026 batch chart and the severity chart from the CSVs; quarters
come from each CVE's publication date, so the main chart and the CVE ledger
cannot disagree. The severity chart refuses to draw if any CVE from 2015 on
lacks a rating. [`check.py`](check.py) runs offline semantic checks: unique
CVEs, complete dates, category sums, CVE-to-annual and CVE-to-reporter
aggregation, evidence for every AI classification, pinned source hashes,
and the fact lines above. For a network-backed verification that every
vendored field still exactly matches the pinned OpenSSL snapshot, run:

```sh
python3 problems/cyber-openssl/fetch.py --check
```

## Limitations

- **no causal estimate.** The series has no denominator for researcher
  time, compute, audit intensity or code added; AI capability and increased
  attention cannot be separated.
- **changing target.** Project identity is stable, but features, versions
  and newly introduced bugs are not.
- **self-reported method evidence.** Aisle's CVE-specific disclosures are
  stronger evidence than inference from its name, but they remain
  first-party claims.
- **unknown tools elsewhere.** "Conventional/fuzzing" means no corroborated
  AI method in the collected sources; it does not establish that every such
  researcher used only manual methods.
- **publication is batched.** `datePublic` tracks coordinated releases, not
  when each issue was discovered.
- **partial year.** The 2026 observation ends on 5 August. The same-period
  comparison addresses exposure time, not seasonality or future releases.
- **small cohorts.** A spread of 67% to 83% Low across 2026 cohorts of nine
  to eighteen CVEs rests on small counts, as does any single year's
  severity mix.

## AI attribution

- **corroborated set:** 21 CVEs. 20 are enumerated by Aisle's CVE-level
  accounts — 3 published 2025-09-30 [@aisleopenssl2025], 12 on 2026-01-27
  [@aisleopenssljan2026] and 5 on 2026-04-07 [@aisleopensslapr2026] — and 1
  carries a reporter credit naming the method:

> "Thai Duong (Calif.io in collaboration with Claude and Anthropic
> Research)"
> — OpenSSL reporter credit for CVE-2026-45447, published 2026-06-09, vendored in [`openssl-cves.csv`](openssl-cves.csv), read 2026-08-14

- **published by year:** 18 of the 21 corroborated CVEs were published in
  2026, 3 in 2025.
- **affiliation-only:** 9 further 2026 CVEs name Aisle or Anthropic
  affiliations without finding-level method evidence in the sources
  collected here; they are `ai_affiliated=yes`, `explicit_ai=no`.
- **Mythos:** Anthropic's disclosure dashboard records vulnerabilities
  attributed to Mythos and names Alex Gaynor on the project team; no
  OpenSSL CVE was identified in the dashboard snapshot consulted
  [@anthropicmythos2026; @anthropiccvd2026]. CVE-2026-28386 is in the
  corroborated set because Aisle's CVE-specific account says its autonomous
  system found it; the same account describes Gaynor's later co-report as
  "likely using Mythos", which is not method evidence for his other OpenSSL
  reports [@aisleopensslapr2026].
- **before 2025:** no CVE row carries an AI marker of either kind, as of
  the pinned 2026-08-05 snapshot.

## Sources

- [@openssl2026index] — the release-metadata repository; the authoritative
  source for every count, severity and official credit here.
- [@aisleopenssl2025] — Aisle's first-party, CVE-level claim to three of
  the four OpenSSL vulnerabilities of 2025.
- [@aisleopenssljan2026] — Aisle's first-party enumeration of the twelve
  January 2026 CVEs.
- [@aisleopensslapr2026] — Aisle's first-party enumeration of five April
  2026 CVEs, and the source of the "likely using Mythos" description.
- [@anthropicmythos2026] — Anthropic's Mythos preview.
- [@anthropiccvd2026] — Anthropic's coordinated-disclosure dashboard; no
  OpenSSL CVE identified in the snapshot consulted.
- [@bloomberg2026recordflaws] — press reporting on the 2026 surge; context
  only, not a substitute for CVE-level provenance.
- [@sherry2021fast] — measured heterogeneity of improvement rates across
  algorithm families; the 2015–2016 disclosure burst here is a pre-LLM
  record in the same spirit.
- Sibling series:
  [all software: disclosed](../cyber-nvd-disclosed/README.md) is the
  aggregate comparison; [curl](../cyber-curl/README.md) and
  [Firefox](../cyber-firefox/README.md) are the closest finder-attributed
  project series.
