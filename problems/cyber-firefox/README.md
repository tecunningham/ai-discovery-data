# Firefox vulnerability disclosures

**Domain:** vulnerabilities
**Metric:** distinct CVEs per year, split by whether the reporter credit names an AI method, an AI-security employer, a fuzzer, or none of these; advisory–CVE mentions retained as a sensitivity count
**Coverage:** 2016–2026, partial through the latest advisory on 4 August 2026
**Data:** [`firefox-advisories.csv`](firefox-advisories.csv); per-reporter rows in [`firefox-finders.csv`](firefox-finders.csv); every AI-marked CVE with its credit strings in [`firefox-ai-cves.csv`](firefox-ai-cves.csv)
**Upstream:** <https://github.com/mozilla/foundation-security-advisories> (rendered at <https://www.mozilla.org/en-US/security/advisories/>)
**Verdict:** accelerating — though distinct CVEs rose 44% from 2021 to 2025 with essentially no AI credit

![Annual Firefox distinct-CVE disclosures, split by AI method, AI affiliation, and fuzzer credit.](discovery-cyber-firefox.png)

## The problem

Mozilla publishes one YAML file per security advisory, and each CVE inside it
carries a `reporter` string. The same CVE can appear in advisories for several
products or releases, so a mention count moves with how Mozilla packages
releases as well as with discovery. The plotted unit is therefore the distinct
CVE ID: a flaw fixed in Firefox, Firefox ESR and Thunderbird on the same day is
one discovery, not three. That makes Firefox the third fixed codebase in this
collection where the finder is named, and by far the largest: a browser is two
orders of magnitude bigger than curl, with a correspondingly bigger attack
surface and a much larger population of people looking at it.

Firefox adds something the other two records barely support. Mozilla's reporter
strings frequently name a fuzzer, so fuzzing can be counted as its own category
rather than being folded into either the human or the AI side. That distinction
is the whole reason this series is worth having next to curl: it separates
"automated search found it" from "a model found it", which is exactly the
ambiguity the 2026 numbers otherwise carry.

A "discovery" here is one distinct CVE ID appearing in that year's advisories.
It is a disclosure count, not a count of bugs found or bugs remaining.

## What the chart shows

A codebase whose distinct-CVE count was drifting up slowly and then jumped: 65
in 2016, 187 in 2017, then a range of roughly 140 to 200 a year through 2024,
210 in 2025, and 342 through the latest advisory on 4 August 2026 — a part-year
total already 1.6 times the 2025 full year.

The AI bands appear almost from nothing. No reporter string carries an AI marker
until 2025, which has exactly one, and 2026 has 37 AI-marked distinct CVEs, or
11% of that year's total. Those 37 divide into 32 whose credit names an AI system
or method and 5 that name only an AI-security employer.
The fuzzer band moves quite differently: 3 distinct CVEs in 2018, 4 in 2022, then
12, 17, 30 and 32 across 2023 to 2026. The fuzz part year already tops 2025 and
annualizes to about 54, so fuzzer-credited discovery kept growing through the
same step where AI-credited discovery went from 1 to 37.

Three things cut the finding down. Distinct CVEs rose 44% from 2021 to 2025 with
essentially no AI credit anywhere, so an upward trend was already running and
nothing here separates AI from Mozilla's own growing security investment. The
2016 and 2017 figures reflect a change in how Mozilla bundles CVEs into
advisories rather than a discovery swing, so the series should not be read
across that break. And the ratio of mentions to distinct CVEs is itself rising —
1.8 in 2016, 3.0 in 2025, 3.3 in 2026 — which is why the old mention-based
headline of "1,140 in 2026, 1.8 times 2025" overstated the change.

![Advisory–CVE mentions against distinct CVE IDs for Firefox.](counting-units-cyber-firefox.png)

The two units are plotted together above. The gap between them is Mozilla's
packaging: more products shipping the same fix multiply mentions without adding
a discovery.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this series
as cumulative distinct CVEs to date:

![Cumulative distinct CVEs to date.](cumulative-cyber-firefox.png)

## How the chart was built

[`figure.py`](figure.py) draws stacked annual bars from
`firefox-advisories.csv`: `unique_other` in blue, `unique_fuzz` in amber,
`unique_ai_affiliated` in pale red and `unique_explicit_ai` in full red, with the
`partial_year` row outlined so the incomplete 2026 cannot be misread as a full
year. The two red bands are the same family in different strengths because they
are different grades of evidence, not different kinds of finder. January 2026
onward is shaded, as in every figure here. The same script draws the
counting-units chart, which is kept separate because by 2026 mentions are more
than three times distinct CVEs and sharing an axis would flatten the bars.

The axis is linear and nothing is normalized, so a bar twice as tall is twice as
many distinct CVEs, and the amber band can be compared with the red ones by
eye.

The CSVs are built by [`fetch.py`](fetch.py),
which walks every `announce/*.yml` file in Mozilla's repository, takes the year
from the advisory's `announced` field, and classifies each CVE's `reporter`
string with two regexes from [`../../lib/credits.py`](../../lib/credits.py).
The classifier reads three independent signals. `EXPLICIT_AI_METHOD` matches a
named system or method — Claude, GPT, Gemini, Big Sleep, Mythos, and the bare
words "LLM" and "agent". `AI_AFFILIATION` matches an employer — Anthropic,
OpenAI, Aisle, XBOW, ZeroPath, AntAISecurityLab — which says who the reporter
works for and nothing about how the bug was found. `FUZZ` matches "fuzz" and is
orthogonal to both, so an AI-written harness can be true in two columns at once.
Bare "Claude" is accepted only from 2024 onward so a human reporter with that
given name cannot create a historical AI credit. Pre-2016 advisories do not list
CVEs in this structure, which is where the series starts.

Bars need one band per segment, so the chart applies a display precedence:
method, then affiliation, then fuzz, then none. Where one CVE carries different
reporter strings in different advisories, its signals are unioned across the year
before that precedence is applied, so which advisory happened to be read last
cannot decide its band. The annual CSV keeps the mention-level columns
(`total`, `ai_attributed`, `fuzz_attributed`, `other_attributed`) beside the
distinct-CVE ones, so the older unit remains auditable rather than discarded.

## What it cannot support

- **The AI share has error in both directions.** A reporter string is free text,
  so a researcher who used a model and did not say so counts as human; equally,
  the 5 affiliation-only CVEs name an employer and not a method, and some of them
  may have been found by hand. The 11% is not a floor, and only the 32
  method-naming CVEs are evidence about how a bug was found.
- **Distinct CVEs still depend on Mozilla's process.** Deduplicating by CVE ID
  removes the product-packaging inflation but not the question of when Mozilla
  assigns one ID versus several to related flaws.
- **No severity comparison.** Mozilla sets `impact` per advisory as well as per
  CVE, and this collection has not untangled the two, so the depth check the
  curl series supports is not available here.
- **A disclosure is not a discovery.** The count moves when Mozilla's own
  advisory process changes, which is visible in the 2016–2017 break.
- **The codebase is fixed but the effort is not.** Nothing here gives a
  denominator of search effort, and Mozilla's security investment grew over the
  same period.
- **2026 is a part-year** through the latest advisory on 4 August, so the bar is outlined and should
  not be compared directly with the full years beside it.

## LLM contributions

The concentration is extreme and is the main finding of this series. Of the 37
AI-marked distinct CVEs in 2026, 31 are credited to a single seven-person team —
Evyatar Ben Asher, Keane Lucas, Nicholas Carlini, Newton Cheng, Daniel Freeman,
Alex Gaynor and Joel Weinberger, using Claude from Anthropic — so roughly 9% of
everything Firefox disclosed in 2026 traces to one coordinated effort with one
tool, and that credit names the model outright. The rest are 11 advisory–CVE
mentions credited to Amy Burnett of OpenAI, 2 to Artur Cygan of Trail of Bits in
partnership with OpenAI, 2 to "Claude, Kai Engert", and 1 to OpenAI Preparedness
with Bill Demirkapi; of these only the Kai Engert credit names a model, which is
why the affiliation-only band exists. The single 2025 AI credit is Aisle
Research, an affiliation with no method stated. Alex Gaynor also appears in OpenSSL's credits, so this is not a
diffuse capability arriving everywhere at once
[@anthropicmythos2026; @aisle2026].

## Related literature

Press coverage frames 2026 as AI finding record numbers of flaws
[@bloomberg2026recordflaws]; on this codebase that headline is mostly a handful
of teams. The fuzzer band is the local version of the control in
[OSS-Fuzz](../cyber-oss-fuzz/README.md), which runs the other way over the same
period, and the two smaller fixed codebases are [curl](../cyber-curl/README.md)
and [OpenSSL](../cyber-openssl/README.md). Every count here is an aggregation of Mozilla's
published advisory data [@mozilla2026advisories]. On the reporting side rather
than the finding side, HackerOne's platform statistics are the only public
figures on how many reports autonomous systems file and how widely human
researchers have adopted models [@hackerone2025autonomy].
