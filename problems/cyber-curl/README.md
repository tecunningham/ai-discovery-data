# curl vulnerability disclosures

**Domain:** vulnerabilities
**Metric:** vulnerabilities disclosed per year, split by finder credit
**Coverage:** 2000–2026, partial through 2026-06-24
**Data:** [`curl-vulnerabilities.csv`](curl-vulnerabilities.csv) (severity detail in the same file), [`curl-vulnerabilities-quarterly.csv`](curl-vulnerabilities-quarterly.csv), [`curl-finders.csv`](curl-finders.csv)
**Upstream:** <https://curl.se/docs/vuln.json> (human-readable at <https://curl.se/docs/security.html>)
**Verdict:** accelerating

![Annual curl vulnerability disclosures, split by explicit AI credit.](discovery-cyber-curl.png)

## The problem

curl is a small, extremely widely deployed C library that has been audited for
twenty-six years. The project publishes a machine-readable record of every
vulnerability it has ever disclosed, with a severity rating set by the
maintainers and a credit naming who found it.

That combination is rare, and it is why this series carries so much weight here.
The codebase is effectively fixed, so the stock of findable bugs should be
*depleting*: a searcher of constant ability should find fewer over time, not
more. There is no growing population of software to confound the count, as there
is in the aggregate CVE series. And because finders are named, the share of
discovery attributable to AI can be read off the record rather than inferred.

A "discovery" here is one disclosed vulnerability. That is a disclosure count,
not a count of bugs introduced or bugs remaining.

## What the chart shows

Roughly twelve disclosures a year from 2017 through 2025, then 36 through
24 June 2026 alone — with 15 of those crediting an AI system or an AI-security
firm. Annualized from that exact date, 2026 is running near 75 a year against
13.1 a year across 2014–2023.

This is the clearest bend in any series in the collection, and the one place
where a collective-progress curve visibly changes slope in the agent era.

Two things cut the finding down, both visible in the data rather than argued.
The AI-credited issues are shallower: within 2026, 80% are rated Low and none
High or Critical, against 48% Low for the other finders. But the drift toward
low-severity findings started well before AI — across 2010–2022 curl's
disclosures were 18% Low and 28% High or Critical, and by 2023–2025 the non-AI
finds were already 67% Low. So AI intensifies a pre-existing trend on a
hardening codebase rather than starting it.

## How the chart was built

[`figure.py`](figure.py) calls the shared `cyber_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), which draws stacked annual bars
from `curl-vulnerabilities.csv`: `other_attributed`
in blue, `ai_attributed` in red, with the `partial_year` row outlined rather
than filled so an incomplete 2026 cannot be misread as a full one. January 2026
onward is shaded, as in every figure here.

The axis is linear and nothing is normalized, so a bar twice as tall is twice as
many vulnerabilities. A log axis was avoided deliberately: it would flatten
exactly the 2026 step the series exists to show.

The CSVs are built by [`fetch.py`](fetch.py), which reads curl's JSON, buckets by publication year, and classifies a report as
AI-credited when any `FINDER` credit string matches an explicit AI marker — a
named system (Big Sleep, Mythos), a firm whose stated business is AI code
security (Aisle Research, AntAISecurityLab), or the word "agent". The marker list
is `CURL_AI` in [`../../lib/credits.py`](../../lib/credits.py), shared with the
other vulnerability folders, and should be read before quoting the 42% share.

## What it cannot support

- **The AI share is a floor.** Classification is by explicit textual marker, so a
  researcher who used a model and did not say so counts as human here.
- **2026 is a part-year**, and curl publishes in batches at releases, so the
  within-year path is lumpy. The quarterly file is the finer-grained view.
- **No denominator of effort.** A credit records who reported, not how much
  search anybody spent, so this cannot separate better tools from more attention.
- **Severity is one small team's judgment** applied over twenty-six years, and
  may not be consistent across that span.
- **Triage, not discovery, became the binding constraint.** curl closed its bug
  bounty in January 2026 after AI-assisted submissions reached about 20% of
  entries while genuine yield fell, so the rise in confirmed disclosures and a
  flood of low-quality reports are the same phenomenon seen from two ends.

## LLM contributions

The 2026 credits name identifiable efforts rather than a diffuse capability:
Google's Big Sleep, an entry crediting Anthropic's Mythos, a Trail of Bits
report made in collaboration with OpenAI, Microsoft's Autonomous Code Security
team, several HackerOne handles crediting AntAISecurityLab, and six from Aisle
Research. Alex Gaynor of Anthropic appears both here and on OpenSSL, so the
AI-credited discovery visible across these codebases is substantially a few
well-resourced people pointed at high-value targets
[@googlebigsleep2024; @anthropicmythos2026; @aisle2026].

## Related literature

Reporting on the 2026 surge in disclosures treats it as an AI effect
[@bloomberg2026recordflaws]; the aggregate series in
[all software: disclosed](../cyber-nvd-disclosed/README.md) is the check on that reading.
The depletion logic — a fixed codebase yielding less to constant effort — is the
apple-picking mechanism this collection is built to test, and its
non-AI baseline is the heterogeneity Sherry and Thompson measure across
algorithm families [@sherry2021fast]. curl's own maintainers have written about
the triage cost of AI-assisted reports [@stenberg2026bounty].
