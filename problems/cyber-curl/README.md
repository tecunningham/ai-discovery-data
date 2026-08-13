# curl vulnerability disclosures

**Domain:** vulnerabilities
**Metric:** vulnerabilities disclosed per quarter, split by finder credit
**Coverage:** 2000–2026, partial through 2026-06-24
**Data:** [`curl-vulnerabilities.csv`](curl-vulnerabilities.csv) (severity detail in the same file), [`curl-vulnerabilities-quarterly.csv`](curl-vulnerabilities-quarterly.csv), [`curl-finders.csv`](curl-finders.csv)
**Upstream:** <https://curl.se/docs/vuln.json> (human-readable at <https://curl.se/docs/security.html>)
**Verdict:** accelerating

![Quarterly curl vulnerability disclosures, split by explicit AI credit.](discovery-cyber-curl.png)

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

Those 15 are mostly an employer, not a method. Reading the credit strings in
[`curl-finders.csv`](curl-finders.csv), one names a system — Andrew Nesbitt
"powered by Mythos" — and the other fourteen name a person at Aisle Research,
AntAISecurityLab, OpenAI or Microsoft's Autonomous Code Security team without
saying how the bug was found. curl's own credits therefore support "researchers
at AI-security companies reported a record number of curl flaws in 2026" and do
not by themselves support "AI found them". The 2025 Big Sleep credit is the
other case where the system is named.

This is the clearest bend in any series in the collection, and the one place
where a collective-progress curve visibly changes slope in the agent era.

Two things cut the finding down, both visible in the data rather than argued.
The AI-credited issues are shallower: within 2026, 80% are rated Low and none
High or Critical, against 48% Low for the other finders. But the drift toward
low-severity findings started well before AI — across 2010–2022 curl's
disclosures were 18% Low and 28% High or Critical, and by 2023–2025 the non-AI
finds were already 67% Low. So AI intensifies a pre-existing trend on a
hardening codebase rather than starting it.

![curl disclosures by severity: counts by year and finder credit since 2010.](severity-cyber-curl.png)

The severity chart puts those four numbers next to the trend they sit in, as
counts a reader can take a number straight out of: one grid per finder-credit
cohort, years across, curl's ratings down, every cell printing how many
disclosures it holds. Shading is scaled within each panel, since the all-finders
grid dwarfs the AI-marked one and a shared scale would blank everything but the
largest; a dark cell is a lot for that cohort, not a lot outright. The drift is
plain in the top grid and it starts around 2017, years before any AI credit:
the High and Critical rows go quiet while the Low row fills.

The two lower grids are the comparison, the same rows split by credit so the
AI-marked cells are read against the right baseline. The gap between 48% and
80% Low in 2026 is real, but the gap that matters is between 18% across
2010–2022 and 67% for non-AI credits in 2023–2025, which is most of the way to
the AI figure and contains no AI at all.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative disclosures to date:

![Cumulative disclosures to date.](cumulative-cyber-curl.png)

## How the chart was built

[`figure.py`](figure.py) calls the shared `periodic_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), which draws stacked quarterly
bars from `curl-vulnerabilities-quarterly.csv`: `other_attributed` in blue,
`ai_attributed` in red, with the final quarter outlined rather than filled —
the annual table's `data_through` says where its data stops — so a short last
bar reads as incomplete rather than as a collapse. January 2026 onward is
shaded, as in every figure here.

The axis is linear and nothing is normalized, so a bar twice as tall is twice as
many vulnerabilities. A log axis was avoided deliberately: it would flatten
exactly the 2026 step the series exists to show.

The severity figure comes from the same script through the shared
`severity_heatmap()` shape, which OpenSSL also draws: one annotated grid per
finder cohort, built from the annual table's severity columns, most severe at
the top. Every cell prints its count, so nothing rests on reading a shade by
eye. The shading itself reuses the severity hue — deliberately neither the red
nor the amber the disclosure chart spends on finder identity — so a severity
grid cannot be misread as a finder band, and it is normalized within each
panel, as the note on the figure says.

The CSVs are built by [`fetch.py`](fetch.py), which reads curl's JSON and
buckets by publication year and quarter. The shared classifier in
[`../../lib/credits.py`](../../lib/credits.py) reads three independent signals
off each `FINDER` string: whether it names an AI system or method (Big Sleep,
Mythos, Claude, "agent"), whether it names an AI-security employer (Aisle
Research, AntAISecurityLab, OpenAI, Anthropic), and whether it names fuzzing.
The per-finder table [`curl-finders.csv`](curl-finders.csv) records which band
each credit falls in, so the affiliation-only rows can be counted separately.

The annual and quarterly tables keep a single combined `ai_attributed` column,
which is true when a credit carries either AI signal. That column is not a
statement about method, and the chart's red band inherits the same caveat. It is
kept combined rather than split because these two files are read directly by the
blog, and the split can be recovered from the finder table without redefining a
column already in use.

## What it cannot support

- **The AI share is not a floor.** Classification is by textual marker, and it
  errs in both directions: a researcher who used a model and did not say so
  counts as human, while fourteen of 2026's fifteen AI-marked reports name only
  an employer and may or may not have involved a model on that finding.
- **Severity is compared across the combined AI band.** The Low-severity
  comparison below is computed against `ai_attributed`, so it describes reports
  from AI-security researchers rather than reports with a corroborated AI
  method.
- **2026 is a part-year**, and curl publishes in batches at releases, so the
  quarterly bars show batch timing as much as a discovery rate.
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
an entry crediting Anthropic's Mythos, a Trail of Bits report made in
collaboration with OpenAI, Microsoft's Autonomous Code Security team, three
HackerOne handles crediting AntAISecurityLab, and 9 from Aisle Research.
Big Sleep's curl credit is in 2025, not 2026. Stanislav Fort of Aisle Research
appears in both curl and OpenSSL, so the AI-credited discovery visible across
these codebases is substantially a few well-resourced people pointed at high-value targets
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
