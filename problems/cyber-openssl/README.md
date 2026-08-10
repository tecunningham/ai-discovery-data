# OpenSSL vulnerability disclosures

**Domain:** vulnerabilities
**Metric:** vulnerabilities disclosed per year, split by finder credit
**Coverage:** 2002–2026, partial through 9 June 2026
**Data:** [`openssl-vulnerabilities.csv`](openssl-vulnerabilities.csv); per-finder rows in [`openssl-finders.csv`](openssl-finders.csv)
**Upstream:** <https://openssl-library.org/news/vulnerabilities/>
**Verdict:** accelerating — but the same shape appeared in 2015–2016 from a purely human cause

![Annual OpenSSL vulnerability disclosures, split by explicit AI and fuzzer credit.](discovery-cyber-openssl.png)

## The problem

OpenSSL is a small, security-critical library that almost everything on the
internet links against, and it has published a vulnerability index since 2002.
Each CVE on that index carries a publication date, usually a severity, and a
"Found by" credit naming the finder.

That makes it the third fixed codebase in this collection with named finders,
alongside curl and Firefox, and it is the one where the AI-credited share is
largest. The value of a fixed target is that the stock of findable bugs should
be depleting rather than growing, so a rise in the count is not explained by
there being more software to search. And because finders are named, AI's share
can be read off the record instead of inferred from an aggregate.

A "discovery" here is one disclosed CVE, counted in the year the project
published it. It is not a count of bugs introduced or of bugs remaining.

The instrument has one real weakness relative to curl. OpenSSL publishes no
machine-readable feed — the JSON and XML endpoints it once offered both return
404 — so the series is parsed out of HTML, and 3 of the 275 CVEs named on the
page could not be given a date and are absent from the counts.

## What the chart shows

Single digits for most of a decade, then a step: 3 disclosures in 2020, 8 in
2021, 13 in 2022, 19 in 2023, 9 in 2024, 6 in 2025, and 38 in the first half of
2026. Of those 38, 26 credit an AI system or an AI-security firm — about two
thirds, the highest AI share of any series in this collection, against 3 of 6
in 2025 and none in any earlier year.

What cuts the reading down is visible in the same chart. The tallest bars in
the whole twenty-four-year series are not recent: 35 in 2016 and 32 in 2015,
the post-Heartbleed audit years, when a concentrated human effort was pointed at
the same library. So the 2026 shape is large but not unprecedented, and the
series supplies its own demonstration that a burst of attention can produce it
without AI. The fuzzer band, kept apart from the AI band, is small throughout
and never exceeds four CVEs in a year.

## How the chart was built

[`figure.py`](figure.py) calls the shared `cyber_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), which
draws stacked annual bars from `openssl-vulnerabilities.csv`:
`other_attributed` in blue, `fuzz_attributed` in amber, `ai_attributed` in red,
with the `partial_year` row outlined in dark grey against its `total` so an
incomplete 2026 cannot be misread as a full one. January 2026 onward is shaded,
as in every figure here.

The axis is linear and nothing is normalized, so a bar twice as tall is twice as
many CVEs. A log axis would flatten the 2026 step the series exists to show.

The CSVs are built by [`fetch.py`](fetch.py),
which parses the HTML index into one record per CVE and classifies the "Found
by" string against two regexes in [`../../lib/credits.py`](../../lib/credits.py)
shared with the finder rows of the other codebases: `ADVISORY_AI`
matches named systems and labs (Claude, Anthropic, OpenAI, GPT, Gemini, Big
Sleep, Mythos, Aisle, AntAISecurityLab, XBOW, ZeroPath) plus the bare words
"LLM" and "agent", and `FUZZ` matches "fuzz". AI is tested first, so a
credit naming both counts as AI. Keeping fuzzing separate is deliberate: a
fuzzer is automated without being a model.

## What it cannot support

- **The AI share is a floor.** Classification is by explicit textual marker, so
  a researcher who used a model and did not say so counts as human here.
- **The parse is lossy.** 272 of the 275 CVEs on the page carry a date in this
  series; the other three are dropped rather than guessed at.
- **Severity is not analysed.** The index records one, but unlike the curl
  series this collection has not compared the severity of AI-credited finds with
  the rest, so nothing here says whether the extra 2026 finds are shallower.
- **2026 is a part-year** through 9 June, and disclosures arrive in batches at
  releases, so the within-year path is lumpy.
- **No denominator of effort.** A credit records who reported, not how much
  search anybody spent, so better tools and more attention cannot be separated.

## LLM contributions

The 26 AI-credited CVEs of 2026 come from a very small group. Counting the
credit lines in `openssl-finders.csv`, 18 name Aisle Research and 9 name
Anthropic, with one line naming both, which accounts for all 26. Stanislav Fort
of Aisle Research is the single largest finder, credited alone on 5 and sharing
4 more; Alex Gaynor of Anthropic is credited on 5; Luigino Camastra of Aisle
Research on 4; Igor Morgenstern of Aisle Research on 2; and one names Claude
through Thai Duong of Calif.io. All three of 2025's AI credits are Fort's.
Gaynor also appears on the team holding most of Firefox's AI-credited CVEs, so
the AI-credited discovery visible across these codebases is substantially a few
well-resourced people pointed at high-value targets
[@aisle2026; @anthropicmythos2026].

## Related literature

Reporting on the 2026 surge treats it as an AI effect
[@bloomberg2026recordflaws], and the aggregate check on that reading is in
[all software: disclosed](../cyber-nvd-disclosed/README.md). The two other fixed
codebases, [curl](../cyber-curl/README.md) and
[Firefox](../cyber-firefox/README.md), are the
comparison that matters most: all three bend in 2026, and the same individuals
recur across them. The project's own index is the source of every count here
[@openssl2026index]. That the pre-AI series already contains a comparable jump
is the reason this document's verdict is hedged; the general point that record
series are lumpy without any AI in them is Sherry and Thompson's
[@sherry2021fast].
