# Output volume: papers, code, packages, DOIs, questions

**Domain:** outside the three domains
**Metric:** research and code output; five indicators of how much gets produced — arXiv submissions a month, git pushes a quarter, Stack Overflow questions a month, DOIs deposited a year, PyPI projects registered
**Coverage:** 1991–2026 (arXiv), 2010–2026 (Crossref), 2019–2026 (Stack Overflow, PyPI), 2020-Q1–2026-Q1 (GitHub)
**Data:** [`arxiv-monthly.csv`](arxiv-monthly.csv), [`github-innovationgraph-global.csv`](github-innovationgraph-global.csv), [`stackoverflow-questions-monthly.csv`](stackoverflow-questions-monthly.csv), [`crossref-dois-by-year.csv`](crossref-dois-by-year.csv), [`pypi-projects-over-time.csv`](pypi-projects-over-time.csv)
**Upstream:** <https://arxiv.org/stats/monthly_submissions>, <https://github.com/github/innovationgraph>, <https://api.stackexchange.com/docs>, <https://api.crossref.org/works>, and dated Wayback captures of <https://pypi.org/>
**Verdict:** accelerating — on volume, which is not discovery

![Five output-volume series in one format: arXiv submissions, git pushes, Stack Overflow questions, Crossref DOIs and PyPI projects, with January 2026 onward shaded.](output-volume.png)

## The problem

This folder holds one question, not five: does the volume of research and code
output bend upward in the agent era? The five series are five indicators of it,
each measuring a different artifact — a paper, an upload of commits, a
registered package, a DOI record, a question asked of other people — and each
produced by the organization that hosts the thing being counted.

They are here as the contrast case. Every other folder in this collection asks
whether some record, bound or discovery count moved. These ask whether the flow
of output moved, which is a far easier thing to measure and a much weaker thing
to establish. Holding the two side by side is the point: volume is where AI's
effect is unmistakable, and discovery is where it has to be argued for.

There is no notion of a discovery in this folder at all. A submission is not a
result, a push is not working code, and a registered package name is not
software anybody runs.

## What the chart shows

Four of the five rise, and one collapses.

arXiv went from 17,271 submissions in November 2022, the month ChatGPT was
released, to 32,040 in June 2026, the last complete month: 85% in three years
and seven months, after decades in which the series took roughly a decade to
double. GitHub pushes are the sharpest bend, from 135.4 million in 2022-Q4 to
167.8 million in 2024-Q4 to 319.8 million in 2026-Q1, roughly doubling over the
last five quarters of the series. PyPI holds 163,524 projects in January 2019
and 861,282 on 28 July 2026, with the slope steepening after 2024: about 61,000
projects added across 2023 against about 142,000 in the twelve months to July
2026.

Crossref is the control, and it is the reason the other three cannot be read
straight off. Deposits rose from 5.28 million records in 2010 to 12.81 million
in 2025 with no clean bend and a dip in 2024, so scholarly publishing volume was
climbing steeply long before there was an agent era to explain it.

Stack Overflow runs the other way and falls further than anything else here
rises: 149,549 questions in January 2019, 109,341 in November 2022, and 2,054 in
June 2026 — a fall of about 98% from the pre-ChatGPT level, beginning at
ChatGPT's release. It is the one series that measures demand for other people's
time rather than production of artifacts, and it is the cleanest demand-side
evidence in the collection.

## How the chart was built

[`figure.py`](figure.py) draws six panels in one format: years on the x-axis, a
volume on the y-axis, January 2026 onward shaded, and a key in the sixth panel.
Part periods are drawn open rather than filled — the trailing arXiv month and
the 2026 Crossref bar — so an incomplete period cannot be read as a full one.
Nothing is normalized or rescaled between panels, because the panels are not
meant to be compared to each other in level, only in shape.

The four live series are rebuilt by [`fetch.py`](fetch.py) from arXiv's own
statistics download, one Crossref API request per year, one Stack Exchange API
request per month, and the three per-economy Innovation Graph CSVs summed over
economies with the EU aggregate row dropped.

PyPI has no fetcher. The registry publishes current totals only, so its history
was collected by hand from 31 dated Wayback captures of the front-page counter
plus one live reading, and each row in the CSV carries the capture URL it came
from. Rerunning `fetch.py` leaves that file alone.

## What it cannot support

- **No authorship labels anywhere.** None of the five series records whether a
  human or a model produced the artifact, so no AI share can be read off any of
  them, and the attribution of the bends is open.
- **Volume is not discovery.** These count artifacts produced. The three domain
  folders count results, and the two need not move together.
- **A push is an upload event.** Agent-driven pushes, CI automation, and humans
  typing faster are indistinguishable, and the composition evidence elsewhere in
  the collection runs the other way.
- **Stack Overflow counts surviving questions.** Deleted questions vanish
  retroactively, so historical months understate what was asked at the time.
  The collapse is far too large for that to explain, but the levels are not
  exact.
- **Crossref counts deposits, not publications.** Backfile deposits of old work
  land in whatever year they were registered, which is what makes the 2024 dip
  uninterpretable as a change in publishing.
- **A PyPI project is a registered name**, not working or used software, and
  registry spam and name-squatting waves are not corrected for.
- **The GitHub total is assembled here.** GitHub publishes per-economy files;
  economies below its 100-developer reporting threshold are absent, so the sum
  slightly undercounts.
- **No denominator of effort.** Nothing here measures how many people were
  working, so a rise in output per unit of input cannot be separated from more
  input.

## LLM contributions

Nothing in these series is attributable to a model, by construction, and that
is worth stating plainly rather than leaving as an omission: the series are
counts of artifacts with no authorship field, so a rise is consistent with
models writing the artifacts, with more people producing more, or with both.

The one place the timing does most of the work is Stack Overflow, where the
fall begins at ChatGPT's release and continues to near zero. Asking a public
question is directly substitutable by asking a model, which makes substitution
the natural reading — but it is a reading, and the series cannot distinguish it
from the platform declining for its own reasons.

## Related literature

The point of this folder is the comparison with the rest of the collection.
Set it against [curl](../cyber-curl/README.md), where a fixed codebase yields a
step change in disclosures, and against the mathematics folders, where the
records barely move. The same volume-against-discovery distinction shows up in
the vulnerability counts: NIST reports 263% growth in CVE submissions between
2020 and 2025 while its own enrichment of nearly 42,000 CVEs in 2025 failed to
keep pace [@nist2026cvegrowth], which is a statement about throughput rather
than about what was found. The efficiency baseline in
[technology cost curves](../technology-cost-curves/README.md) is the other half
of the frame: output volume and unit cost are the two things that visibly move
in this collection.
