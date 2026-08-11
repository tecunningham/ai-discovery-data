# Firefox vulnerability disclosures

**Domain:** vulnerabilities
**Metric:** advisory–CVE mentions per year, split by AI, fuzzer, or other reporter credit; unique CVE IDs retained as a sensitivity count
**Coverage:** 2016–2026, partial through the latest advisory on 4 August 2026
**Data:** [`firefox-advisories.csv`](firefox-advisories.csv); per-reporter rows in [`firefox-finders.csv`](firefox-finders.csv)
**Upstream:** <https://github.com/mozilla/foundation-security-advisories> (rendered at <https://www.mozilla.org/en-US/security/advisories/>)
**Verdict:** accelerating — though disclosures roughly doubled from 2021 to 2025 with essentially no AI credit

![Annual Firefox vulnerability disclosures, split by explicit AI and fuzzer credit.](discovery-cyber-firefox.png)

## The problem

Mozilla publishes one YAML file per security advisory, and each CVE inside it
carries a `reporter` string. The same CVE can appear in advisories for several
products or releases, so the plotted unit is one advisory–CVE mention rather
than one distinct vulnerability. That makes Firefox the third fixed codebase in this
collection where the finder is named, and by far the largest: a browser is two
orders of magnitude bigger than curl, with a correspondingly bigger attack
surface and a much larger population of people looking at it.

Firefox adds something the other two records barely support. Mozilla's reporter
strings frequently name a fuzzer, so fuzzing can be counted as its own category
rather than being folded into either the human or the AI side. That distinction
is the whole reason this series is worth having next to curl: it separates
"automated search found it" from "a model found it", which is exactly the
ambiguity the 2026 numbers otherwise carry.

A "discovery" here is one CVE listed in an advisory, counted in the advisory's
announcement year. It is a disclosure-mention count, not a count of distinct
bugs found or bugs remaining.

## What the chart shows

A codebase whose advisory-CVE count was already climbing: 119 mentions in 2016,
429 in 2017, then a range of roughly 280 to 500 a year through 2024, 640 in
2025, and 1,140 through the latest advisory on 4 August 2026 — a part-year total
already 1.8 times the 2025 full year. Those last two totals represent 210 and
342 distinct CVE IDs respectively.

The AI band appears almost from nothing. No reporter string carries an AI marker
until 2025, which has exactly one, and 2026 has 137 mentions across 37 distinct
CVE IDs, or 12% of that year's mentions.
The fuzzer band moves quite differently: 7 in 2018, 8 in 2022, then 32, 41, 104
and 108 across 2023 to 2026. Fuzzer-credited discovery grew through 2025 and
then flattened in the same step where AI-credited discovery went from 1 to 137.

Two things cut the finding down. The count roughly doubled from 2021 to 2025
with essentially no AI credit anywhere, so an upward trend was already running
and nothing here separates AI from Mozilla's own growing security investment.
And the 2016 and 2017 figures reflect a change in how Mozilla bundles CVEs into
advisories rather than a discovery swing, so the series should not be read
across that break.

## How the chart was built

[`figure.py`](figure.py) calls the shared `cyber_stacked()` shape in
[`../../lib/families.py`](../../lib/families.py), which
draws stacked annual bars from `firefox-advisories.csv`: `other_attributed` in
blue, `fuzz_attributed` in amber, `ai_attributed` in red, with the
`partial_year` row outlined against its `total` so the incomplete 2026 cannot be
misread as a full year. January 2026 onward is shaded, as in every figure here.

The axis is linear and nothing is normalized, so a bar twice as tall is twice as
many advisory–CVE mentions, and the amber band can be compared with the red one
by eye.

The CSVs are built by [`fetch.py`](fetch.py),
which walks every `announce/*.yml` file in Mozilla's repository, takes the year
from the advisory's `announced` field, and classifies each CVE's `reporter`
string with two regexes from [`../../lib/credits.py`](../../lib/credits.py).
The shared AI marker list matches Claude, Anthropic, OpenAI, GPT,
Gemini, Big Sleep, Mythos, the AI-security firms, and the bare words "LLM" and
"agent"; `FUZZ` matches "fuzz". AI is tested first, so a report crediting
a model and a fuzzer counts as AI. Bare "Claude" is accepted only from 2024
onward so a human reporter with that given name cannot create a historical AI
credit. Pre-2016 advisories do not list CVEs in this structure, which is where
the series starts. The annual and per-reporter tables use the same classifier;
unifying the former marker lists moved no currently vendored row. The annual
CSV also retains `unique_cves` and
`unique_ai_cves`, deduplicated by CVE ID within each year, so the mention count
can be compared with a distinct-ID sensitivity count.

## What it cannot support

- **The AI share is a floor.** A reporter string is free text, so a researcher
  who used a model and did not mention it counts as human and the 12% is a lower
  bound by an unknown margin.
- **Mentions are not unique vulnerabilities.** A CVE repeated across product or
  release advisories contributes more than once to the plotted bar. In 2026,
  1,140 mentions represent 342 distinct IDs, so this chart is not directly
  comparable to a deduplicated CVE series such as NVD.
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

The concentration is extreme and is the main finding of this series. Of the 137
AI-credited advisory–CVE mentions in 2026, 121 (covering 31 distinct CVE IDs)
are credited to a single seven-person team —
Evyatar Ben Asher, Keane Lucas, Nicholas Carlini, Newton Cheng, Daniel Freeman,
Alex Gaynor and Joel Weinberger, using Claude from Anthropic — so roughly 11% of
everything Firefox disclosed in 2026 traces to one coordinated effort with one
tool. The remaining mentions are 11 credited to Amy Burnett of OpenAI, 2 to Artur
Cygan of Trail of Bits in partnership with OpenAI, 2 to "Claude, Kai Engert",
and 1 to OpenAI Preparedness with Bill Demirkapi. The single 2025 AI credit is
Aisle Research. Alex Gaynor also appears in OpenSSL's credits, so this is not a
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
