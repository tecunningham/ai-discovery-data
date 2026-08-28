# OSS-Fuzz vulnerability discoveries

- **Domain:** vulnerabilities
- **Role:** control: no-AI baseline
- **Metric:** vulnerability records published per quarter by an automated fuzzing programme
- **Coverage:** 2020–2026, partial through 2026-08-10
- **Data:** quarterly [`ossfuzz-by-quarter.csv`](ossfuzz-by-quarter.csv); annual [`ossfuzz-by-year.csv`](ossfuzz-by-year.csv)
- **Upstream:** <https://osv-vulnerabilities.storage.googleapis.com/OSS-Fuzz/all.zip> (browsable at <https://osv.dev/list?q=ecosystem%3AOSS-Fuzz>, programme at <https://google.github.io/oss-fuzz/>)
- **Verdict:** declining — 1,041 records in 2020 to 244 in 2025; 2026 annualizes to roughly 396

![Quarterly OSS-Fuzz vulnerability records, falling from a 2020 peak to a few dozen per quarter by 2025.](discovery-cyber-oss-fuzz.png)

## Definition

OSS-Fuzz is Google's continuous fuzzing service for open-source software. It
runs automated search against the projects enrolled in it and publishes each
finding as a dated record in the OSV database. The programme states its own
scale:

> "As of August 2023, OSS-Fuzz has helped identify and fix over 10,000
> vulnerabilities and 36,000 bugs across 1,000 projects."
> — OSS-Fuzz documentation, google.github.io/oss-fuzz, read 2026-08-14 [@google2026ossfuzz]

A "discovery" in this series is one published OSV record in the OSS-Fuzz
ecosystem. The count is not severity-weighted and is not restricted to any
single codebase. Records carry an ecosystem and dates but no finder credit
and no severity field.

## Facts

- **by-year (record id):** 2020: 1,041 · 2021: 739 · 2022: 710 · 2023: 581 · 2024: 388 · 2025: 244 · 2026 (through 2026-08-10): 241
- **2026 annualized:** roughly 396 records
- **total:** 3,944 records over 2020–2026
- **clock gap:** quarters by published date sum to 247 records in 2026 against 241 by record id

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative vulnerability records to date:

![Cumulative vulnerability records to date.](cumulative-cyber-oss-fuzz.png)

## Method

Both CSVs are built by [`fetch.py`](fetch.py) from the same OSV archive, on
two different clocks. The annual `ossfuzz-by-year.csv` counts records by
the year embedded in the record identifier (`OSV-YYYY-N`); the quarterly
`ossfuzz-by-quarter.csv` buckets the same records by their `published` date.
Records predating 2020 were backfilled into OSV during 2021, so their
publication dates all land in that year; counting by identifier year avoids
assigning those 267 pre-2020 records to 2021, and the series is reported from
2020, where the two clocks agree closely (1,041 against 1,031 for 2020, 710
against 716 for 2022). The clocks can still disagree at a year boundary; the
2026 gap is stated in the facts above. Records published after the
repository's snapshot date (`AS_OF_DATE` in
[`../../lib/dates.py`](../../lib/dates.py)) are dropped, so a refetch
reproduces the committed window; that snapshot is the `data_through` date the
partial rows carry.

[`figure.py`](figure.py) calls the shared `periodic_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), drawing one amber bar per
quarter from the `discoveries` column — amber is the collection's fuzzer
colour. There is no AI/human split because the records carry no finder
credit. The partial quarter is outlined and annotated with the `data_through`
date. The axis is linear and January 2026 onward is shaded, as in every
figure here. [`check.py`](check.py) recomputes the fact lines from the
annual CSV.

## Limitations

- **publication, not discovery.** The series counts findings OSS-Fuzz
  published through OSV; a change in disclosure practice would move it, and
  nothing in the data distinguishes that from a change in yield.
- **the project set is not fixed.** Enrolment changed over the period, and no
  per-project denominator is vendored here, so the series is programme output
  rather than a per-codebase depletion curve.
- **no severity field.** Nothing in the records supports comparing the
  consequence of a 2020 finding with a 2026 one.
- **no finder attribution.** The records name no finder, so no AI/human split
  can be made from this series.
- **the 2026 annualization is this repository's arithmetic**, scaled from a
  part-year on an even-rate assumption.

## AI attribution

No OSS-Fuzz record names a finder, so no record carries an AI credit, as of
the 2026-08-10 read of the archive. One adjacent fact: OSS-Fuzz-Gen, an
LLM-assisted generator of fuzzing harnesses, appears by name in OpenSSL
credit strings vendored in [`../cyber-openssl/`](../cyber-openssl/README.md),
and this collection classifies those CVEs as fuzzing because the credit
names the fuzzer [@osv2026ossfuzz; @google2026ossfuzz].

## Sources

- [@osv2026ossfuzz] — the OSV export the CSVs are built from.
- [@google2026ossfuzz] — the programme's documentation, quoted above for its
  stated scale.
- [@darpa2016cgc] — the 2016 Cyber Grand Challenge, cited as the dated
  precedent for autonomous vulnerability discovery without language models.
- [@googlebigsleep2024] — Google's AI vulnerability-discovery work, which
  runs outside this programme; no record here is attributed to it.
- [@sherry2021fast] — measured heterogeneity of improvement rates across
  algorithm families, the published base rate for declining yields.
- Finder-credited series over codebases this programme also fuzzes:
  [curl](../cyber-curl/README.md), [OpenSSL](../cyber-openssl/README.md),
  [Firefox](../cyber-firefox/README.md).
