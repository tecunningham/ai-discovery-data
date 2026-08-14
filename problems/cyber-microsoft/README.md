# Microsoft security-update CVEs

**Domain:** vulnerabilities
**Role:** discovery series
**Metric:** CVEs issued by Microsoft's own CNA per month, dated by first publication in the Security Update Guide, split by whether an acknowledgment credit names an AI method, an AI-security employer, a fuzzer, or none of these
**Coverage:** 2016–2026, partial through 2026-08-11; no February or March 2016 document exists upstream, so the first year is ten months
**Data:** annual [`msrc-cves.csv`](msrc-cves.csv); monthly counts by band in [`msrc-monthly.csv`](msrc-monthly.csv); per-credit rows in [`msrc-finders.csv`](msrc-finders.csv); every AI-marked CVE with its full credit strings in [`msrc-ai-cves.csv`](msrc-ai-cves.csv)
**Upstream:** <https://api.msrc.microsoft.com/cvrf/v3.0/updates> (rendered at <https://msrc.microsoft.com/update-guide>)
**Verdict:** accelerating — 1,927 CVEs through 2026-08-11 against 1,243 in 2025; the part year annualizes to about 2.5 times 2025

![Monthly Microsoft security-update CVEs, split by AI method, AI affiliation, and fuzzer credit.](discovery-cyber-microsoft.png)

## Definition

Microsoft ships security fixes in one coordinated monthly release — Patch
Tuesday, running since October 2003 [@arcticwolf2026june] — and publishes
each month since January 2016 as a machine-readable CVRF document in the
Security Update Guide, with acknowledgments naming who reported most
entries. A Windows vulnerability is found against shipped binaries and a bug
bounty rather than a public repository; curl, OpenSSL and Firefox, the other
finder-named codebases in this collection, are all open source.

Trackers count a given Patch Tuesday differently: Arctic Wolf counts the
June 2026 release at 206 vulnerabilities [@arcticwolf2026june], and Tenable
counts the July 2026 release at 569 CVEs while other trackers put the same
release at up to 622 [@tenable2026july]. The spread arises because the
monthly documents also republish CVEs Microsoft did not author — Chromium
fixes shipped through Edge, and from 2023 the Linux CVEs of Azure Linux —
and every tracker folds those in differently. This folder pins one rule to
the primary source: an entry counts when the CNA note in its document says
Microsoft, or when it has no CNA note at all, which is the pre-2018 document
format. Everything that rule excludes is verifiably third-party — the
excluded entries carry Chrome, Linux distribution, curl or similar CNA
notes. Each CVE is dated by the earliest revision in its history across
every document that mentions it, so an out-of-band fix lands in the month it
shipped.

A "discovery" here is one Microsoft-issued CVE first published that month.
It is a patch-and-disclosure count, not a count of bugs found or bugs
remaining.

## Facts

- **by-year:** 2016: 371 · 2017: 622 · 2018: 639 · 2019: 863 · 2020: 825 ·
  2021: 877 · 2022: 956 · 2023: 961 · 2024: 1,095 · 2025: 1,243
- **2016 span:** 371 CVEs across ten documented months
- **plateau and growth:** between 825 and 961 a year from 2019 through
  2023; 14% growth in each of 2024 and 2025
- **2026 (through 2026-08-11):** 1,927 CVEs, 1.55 times the 2025 full year;
  annualizes to about 2.5 times 2025
- **record months:** 220 CVEs dated June 2026, then 662 CVEs dated July
  2026, 3.0 times the June figure
- **ai-marked:** 0 before 2025; 17 in 2025; 26 in 2026, or 1.3% of the part
  year — 21 name an AI system or method and 5 name only an AI-security
  employer
- **fuzz band:** never exceeds 2 CVEs in any year
- **acknowledgments:** 87% of 2016's CVEs carry at least one named credit,
  rising to 98% in the 2026 part year
- **no-customer-action CVEs:** 23 in 2024, 68 in 2025 and 128 in the 2026
  part year

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as cumulative CVEs to date:

![Cumulative CVEs to date.](cumulative-cyber-microsoft.png)

## Method

The CSVs are built by [`fetch.py`](fetch.py), which walks every monthly
security-update document in the CVRF API — matched on document title,
because the IDs are irregular — and applies the CNA rule above. Documents
released after `lib/chart.py`'s snapshot date are skipped, so a refetch
reproduces the committed window; the vendored window ends at the August 2026
Patch Tuesday, released 2026-08-11. Acknowledgment strings are stripped of
HTML and classified with the shared markers in
[`../../lib/credits.py`](../../lib/credits.py): `EXPLICIT_AI_METHOD` for a
named system or method, `AI_AFFILIATION` for an employer, `FUZZ` for
fuzzing, with one CVE's signals unioned across all its credit strings before
the display precedence — method, then affiliation, then fuzz, then none —
picks its band. Anonymized hex handles count as credits, since an anonymous
credit is still a credit. `msrc-monthly.csv` carries the same four bands at
the monthly grain, banded per CVE by the same rule, so the months of a year
sum to that year's row in `msrc-cves.csv`. The annual CSV keeps an
`acknowledged` column beside the bands, and a `no_customer_action` column
counting the cloud-service CVEs Microsoft patches itself, so both facts stay
auditable.

[`figure.py`](figure.py) draws stacked monthly bars from `msrc-monthly.csv`:
`other` in blue, `fuzz` in amber, `ai_affiliated` in pale red and
`explicit_ai` in full red, in the same bands and colours as the
[Firefox series](../cyber-firefox/README.md). No bar is drawn partial —
Microsoft ships one coordinated release per month, and the final month's
release is in the data — and the on-chart note states where the data stop.
January 2026 onward is shaded, as in every figure here. The axis is linear
and nothing is normalized. [`check.py`](check.py) recomputes the fact lines
above and fails when the monthly, annual and per-CVE files stop agreeing.

## Limitations

- **a disclosure is not a discovery, and here it is not dated like one.**
  CVEs are batched to a monthly release cadence and published when fixed,
  not when found or reported; the 662 CVEs of July 2026 are a release
  event, and the gap between report and patch can be months. The count
  moves with Microsoft's triage and engineering throughput as well as with
  anyone's rate of finding.
- **vendor policy moves the count.** In mid-2024 Microsoft began issuing
  CVEs for cloud-service flaws it patches itself, with no customer action
  required: 23 CVEs in 2024, 68 in 2025 and 128 in the 2026 part year.
  Removing that column entirely leaves the 2026 rise in place; other policy
  shifts would not be so visible.
- **the AI share has error in both directions.** Acknowledgments are free
  text; a researcher who used a model silently counts as human, an
  affiliation-only credit may not have used one, and the SEC-agent team's
  marker is the word "agent" in its own name. Only the method-naming
  credits are evidence about how a bug was found, and even those are the
  finder's own account.
- **no severity or depth comparison.** The documents rate severity, but
  this folder has not extracted it, so a 2026 CVE cannot be compared in
  consequence with a 2019 one here.
- **the codebase is fixed but the surface and the effort are not.**
  Microsoft added cloud services, acquired products and an expanded bounty
  over the period, and nothing here gives a denominator of code or search
  effort.
- **edges of coverage.** The first year is ten months; a month with no
  bar — February 2017, for one — is a month in which no CVE has its
  earliest publication; 2026 is a part year through 2026-08-11, ending on
  the August Patch Tuesday rather than a complete calendar month. The rare
  Microsoft-product CVE issued by another CNA — a 2022 Windows SMB flaw
  issued by Rapid7's CNA, for instance — is excluded by the counting rule.

## AI attribution

Every AI-marked CVE is itemized with its full credit strings in
[`msrc-ai-cves.csv`](msrc-ai-cves.csv); the quotes below are read from that
file as vendored, 2026-08-14. No AI marker appears in any acknowledgment
before 2025, as of the 2026-08-11 snapshot.

- **SEC-agent team.** All 17 AI-marked CVEs of 2025 carry a SEC-agent
  credit, 14 of them jointly with ENKI WhiteHat, and 14 of 2026's 26
  AI-marked CVEs carry one. The team's SLYP pipeline runs LLM agents
  against Windows COTS binaries [@secagent2026slyp].

> "Hwiwon Lee (hwiwonl), SEC-agent team | Jongseong Kim (nevul37),
> SEC-agent team with ENKI WhiteHat"
> — MSRC acknowledgment strings for CVE-2025-53802, vendored in [`msrc-ai-cves.csv`](msrc-ai-cves.csv), read 2026-08-14

- **Claude and Anthropic.** 7 of 2026's AI-marked CVEs credit Claude or
  Anthropic [@anthropicmythos2026]. One of them, CVE-2026-33096, is
  co-credited to "WARP & MORSE teams at Microsoft".

> "Calif.io in collaboration with Claude and Anthropic Research"
> — MSRC acknowledgment for CVE-2026-40380, vendored in [`msrc-ai-cves.csv`](msrc-ai-cves.csv), read 2026-08-14

- **XBOW.** 3 CVEs credit "XBOW", an affiliation with no method stated.
- **OpenAI.** The remaining 2 CVEs, both dated 2026-08-11, credit "Thomas
  Neil James Shadwell (zemnmez) with OpenAI" — an affiliation with no
  method stated.

## Sources

- [@msrc2026sug] — the CVRF API; the primary source every vendored count
  here aggregates.
- [@arcticwolf2026june] — Arctic Wolf's June 2026 recap: 206
  vulnerabilities, called the largest single security update since the
  program began in October 2003.
- [@tenable2026july] — Tenable's July 2026 recap: 569 CVEs, with other
  trackers putting the same release at up to 622.
- [@secagent2026slyp] — the SLYP pipeline behind the SEC-agent credits:
  LLM agents over binary-exploration and debugging MCP servers.
- [@anthropicmythos2026] — Anthropic's Mythos preview, background on the
  vendor named in the Claude credits.
- [@bloomberg2026recordflaws] — press reporting connecting 2026 disclosure
  records to AI systems; on this vendor the AI-marked share of the part
  year is 1.3%.
- [@hackerone2025autonomy] — HackerOne's platform statistics, the only
  public figures on how many reports autonomous systems file.
- Sibling series: these CVEs are a subset of
  [all software: disclosed](../cyber-nvd-disclosed/README.md); the
  open-source fixed codebases with named finders are
  [curl](../cyber-curl/README.md), [OpenSSL](../cyber-openssl/README.md)
  and [Firefox](../cyber-firefox/README.md), with
  [OSS-Fuzz](../cyber-oss-fuzz/README.md) as the automation control and
  [known-exploited additions](../cyber-kev-exploited/README.md) as the
  exploitation-side count.
