# All software: vulnerabilities disclosed

**Domain:** vulnerabilities
**Metric:** CVEs published per quarter in the US National Vulnerability Database
**Coverage:** 2016–2026, partial through 2026-08-10
**Data:** quarterly [`nvd-by-quarter.csv`](nvd-by-quarter.csv); annual totals in [`nvd-by-year.csv`](nvd-by-year.csv)
**Upstream:** <https://services.nvd.nist.gov/rest/json/cves/2.0> (human-readable at <https://nvd.nist.gov/vuln>)
**Verdict:** accelerating — but growth was already +32% and +23% in 2024 and 2025, and no disclosure here is attributed to anyone

![Quarterly CVE disclosures in the US National Vulnerability Database.](discovery-cyber-nvd-disclosed.png)

## The problem

This is the aggregate: every CVE published in the US government's vulnerability
database, across all software, for eleven years. It is the series behind the
claim that AI has bent the cyber discovery curve, and it is here so the
reporting's arithmetic can be checked against the primary source rather than
trusted.

It is the weakest instrument in this domain and the most quoted, which is why it
needs a document. There is no fixed codebase, so the population being searched
grows along with the count. There is no finder attribution, so nothing in the
series says who found anything or with what. And a CVE is published when a
vendor's process publishes it, so a single organization's internal pipeline can
move the aggregate without the world's stock of bugs changing at all.

A "discovery" here is one CVE record, counted in the quarter NVD published it.

## What the chart shows

A steep and mostly monotonic climb. Summed to years: 6,517 CVEs in 2016,
18,113 in 2017, then a slow rise through 19,222 in 2020 and 26,431 in 2022 to
40,704 in 2024 and 49,972 in 2025, which was itself a record. The 2026 count
stands at 49,838 through 2026-08-10,
day 222 of the year, which annualizes to about 82,000 — roughly 1.6 times 2025.

The quarterly grain adds a shape those annual totals hide: the 2026 surge steepens
within the year. Q1's 16,255 already topped every quarter before it, and Q2's
20,871 is another 28% above Q1 and 59% above 2025's largest quarter. Whether
that is discovery or a publication pipeline clearing is exactly what this
series cannot say.

Two things cut the reading down, and both are arithmetic on the same series.
First, the curve was already steepening before any of this: year-on-year growth
was +32% into 2024 and +23% into 2025, against about +64% annualized for 2026.
Reading 2026 against a flat baseline would overstate the change by a wide
margin. Second, the widely reported claim that 2026 is "on pace to roughly
double" 2025 does not survive the annualization, which would require about
99,900 disclosures; the count is on pace for about 1.6 times, not twice. The
reported part-year figure itself checked out at the time: 45,207 in the report
against this query's 45,601 on 28 July, and NVD is continuously amended, so a
small gap is expected. The annualization, the growth rates and the correction
are this repository's arithmetic, not a source's stated claim.

The 2016-to-2017 near-tripling is a process break — the expansion of CVE
numbering authorities — so the series is comparable only from about 2018.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative CVEs published to date:

![Cumulative CVEs published to date.](cumulative-cyber-nvd-disclosed.png)

## How the chart was built

[`figure.py`](figure.py) calls the shared `periodic_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), which
draws one bar per quarter from the `nvd_published` column of `nvd-by-quarter.csv`.
The bars are blue, the colour this collection uses for human or uncredited
finders, because nothing in this series is attributed to anyone; there is no red
band to draw. The `partial_quarter` row is outlined in dark grey and annotated with
the `data_through` value, so the bar reads as partial through 2026-08-10. The
axis is linear and January 2026 onward is shaded, as in every figure here.

The `kev_added` counts plotted in
[all software: known exploited](../cyber-kev-exploited/README.md) were once a
second column of this file and now live in that folder. The two are drawn as
separate figures rather than overlaid because they differ by two orders of
magnitude, and putting them on one axis previously required a log scale that
obscured exactly the comparison they exist to make.

The CSVs are built by [`fetch.py`](fetch.py).
NVD caps a query window at 120 days and rate-limits unkeyed callers, so each
year is fetched as four quarterly windows with a pause between calls and a
backoff for the HTML error pages the API returns when the limit is hit; the
script reads `totalResults` rather than the records themselves. Quarters are
therefore the query's native grain, and the annual file is their sum.

## What it cannot support

- **A disclosure count is not a discovery count.** It rises when vendors process
  and publish more reports, whatever produced the reports.
- **No attribution of any kind.** Not one row here is credited to AI, to a
  human, or to a tool, so any AI reading of this chart is imported from
  elsewhere.
- **The population grows with the count.** There is more software every year and
  more numbering authorities publishing about it, so this is not a depletion
  curve on a fixed target the way the curl and OpenSSL series are.
- **One vendor can move the aggregate.** Press reporting on July 2026 records
  433 Chrome fixes against 11 a year earlier, of which 401 were reported inside
  Google, which is a single internal pipeline showing up in a national count.
- **The enrichment step lags the submissions.** NIST reports enriching nearly
  42,000 CVEs in 2025, 45% more than any prior year, and still not keeping pace,
  so the published series reflects a processing constraint as well as a
  discovery one.

## LLM contributions

Nothing in this series is separable, because the series carries no finder
credit. The named AI efforts sit outside it and have to be brought in from
vendor and press claims: Oracle reporting 1,449 fixes in its July 2026 update
against 309 a year earlier, Microsoft 642 bugs disclosed in July, and Google 433
Chrome fixes against 11, with Chrome's director of engineering attributing the
"unprecedented scale and speed" to advances in AI models and a corresponding
investment. Those are the mechanism this chart is consistent with, not evidence
it contains. For attribution that can be counted, the fixed-codebase series are
the instrument [@bloomberg2026recordflaws; @anthropicmythos2026].

## Related literature

The claim that AI has doubled discovery originates in press reporting
[@bloomberg2026recordflaws], and the counts above are this repository's own
query against the government API behind it [@nvd2026api]. NIST's own account of
record CVE growth and its enrichment backlog is the operational context for
reading the series as a publication pipeline rather than a discovery rate
[@nist2026cvegrowth]. The counterweight series is
[all software: known exploited](../cyber-kev-exploited/README.md), and the
fixed-codebase alternative with named finders is
[curl](../cyber-curl/README.md). For capability measured
on a task set held fixed across a year, which no aggregate can supply, the DARPA
AI Cyber Challenge is the anchor [@darpa2025aixcc].
