# Stack Overflow questions

**Domain:** outside the three domains
**Metric:** demand for human answers; questions created on Stack Overflow per month
**Coverage:** 2019-01 to 2026-06, monthly, complete months only
**Data:** [`stackoverflow-questions-monthly.csv`](stackoverflow-questions-monthly.csv)
**Upstream:** <https://api.stackexchange.com/docs>
**Verdict:** declining — on demand for human answers, not on discovery

![Stack Overflow questions created per month, 2019 to 2026, collapsing after ChatGPT's release, with January 2026 onward shaded.](output-stackoverflow-questions.png)

## The problem

Does demand for other people's time move in the agent era? The other volume
folders count artifacts produced — a paper, a push, a package, a DOI record.
This one counts a request for help, which is the only thing in the collection a
model substitutes for directly: asking a public question and asking a model are
close substitutes in a way that writing a paper and having a model write one are
not.

That makes it the cleanest demand-side evidence here, and it is still not a
discovery series. A question asked is not a result, and a question not asked is
not a result either.

## What the chart shows

The series collapses. It stood at 149,549 questions in January 2019, peaked at
186,411 in May 2020 in the first pandemic months, and was at 109,341 in November
2022, the month ChatGPT was released. By June 2026 it was 2,054: 98% below the
pre-ChatGPT level, and the fall is continuous rather than a step.

The decline did not begin with ChatGPT. From the May 2020 peak the series was
already drifting down, and November 2022 is 41% below it. What changes at the
dotted rule is the slope: the seven months after ChatGPT's release take the
count down another 42%, and it keeps falling for three more years.

Every figure in the annotation is computed from the CSV when the chart is drawn,
so it cannot survive a refetch that changes the numbers.

## How the chart was built

[`fetch.py`](fetch.py) asks the Stack Exchange API for one count per month since
January 2019, bounded by the first and last second of the month in UTC, and
stops at the last complete month so a month in progress cannot be read as a
finished one. The API returns questions that exist now, matched by creation
date.

[`figure.py`](figure.py) draws the series through
[`lib/families.py`](../../lib/families.py)'s shared volume shape: years on the
x-axis, the count on the y-axis, January 2026 onward shaded, with a dotted rule
at ChatGPT's release since that is the date the series is usually read against.
The five volume folders use that one shape so a difference in appearance between
any two of them is a difference in the data. It is drawn in slate rather than
the blue the other charts use for human or uncredited finders, because this
series has no authorship field at all.

## What it cannot support

- **These are surviving questions, not questions asked.** Deleted questions
  vanish retroactively, so historical months understate what was asked at the
  time. The collapse is far too large for that to explain, but the levels are
  not exact, and the undercount is worst for the oldest months, which biases the
  fall downward rather than up.
- **Substitution is a reading, not a measurement.** The fall begins at ChatGPT's
  release and the substitute is obvious, but nothing in the series distinguishes
  that from the platform declining for its own reasons.
- **No authorship labels.** Nothing here records why a question was not asked,
  so no AI share can be read off it.
- **One platform.** The series cannot say whether the questions moved to other
  forums, to models, or nowhere.
- **A question is not a discovery.** These count requests for help. The domain
  folders count results, and the two need not move together.
- **No denominator of effort.** Nothing here measures how many people were
  programming, so a fall in questions per programmer cannot be separated from
  fewer programmers.

## LLM contributions

This is the one series in the collection where timing does most of the work. The
fall begins at ChatGPT's release and runs to near zero over three and a half
years, and asking a public question is directly substitutable by asking a model,
which makes substitution the natural reading.

It remains a reading. The series has no authorship field and no counterfactual,
and the platform had problems of its own over the same period; what the chart
establishes is the collapse, not its cause.

## Related literature

The comparison this folder exists for is with the rest of the collection.
[Git pushes](../output-github-pushes/README.md) is the direct pairing: code
pushed to GitHub roughly doubles over the last five quarters while questions
about code collapse, which is what substitution for the human help around coding
would look like and also what a platform losing its audience would look like.
[arXiv](../output-arxiv/README.md) and [PyPI](../output-pypi/README.md) are the
other rising artifact counts, and [Crossref](../output-crossref/README.md) is
the control on all of them. Set the whole group against
[curl](../cyber-curl/README.md), where a fixed codebase yields a step change in
disclosures, and against the mathematics folders, where the records barely move:
this is the only series here that changes by two orders of magnitude, and it
measures nobody discovering anything.
