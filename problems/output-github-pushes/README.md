# Git pushes to GitHub

**Domain:** outside the three domains
**Metric:** code output; git pushes to GitHub per quarter, summed over economies
**Coverage:** 2020-Q1 to 2026-Q1, quarterly
**Data:** [`github-innovationgraph-global.csv`](github-innovationgraph-global.csv)
**Upstream:** <https://github.com/github/innovationgraph>
**Verdict:** accelerating — on volume, which is not discovery

![Git pushes to GitHub per quarter, 2020 to 2026, with January 2026 onward shaded.](output-github-pushes.png)

## The problem

Does the volume of code output bend upward in the agent era? GitHub is the
largest single place where code is written down, and it publishes its own
quarterly counts through the Innovation Graph, so the count comes from the
platform hosting the thing being counted rather than from a survey or an
estimate.

This is a contrast case, not a discovery series. Every folder in the three
domains asks whether some record, bound or vulnerability count moved. This one
asks whether the flow of artifacts moved, which is far easier to measure and a
much weaker thing to establish. A push is an upload of commits, not working
software and not a result.

## What the chart shows

Pushes rose from 135.4 million in 2022-Q4, the quarter ChatGPT was released, to
167.8 million in 2024-Q4 and 319.8 million in 2026-Q1, roughly doubling over the
last five quarters of the series. This is the sharpest bend of the five volume
series, and the bend is late: 2020-Q1 through 2022-Q4 adds 68%, while 2022-Q4
through 2026-Q1 adds 136%, and the steepest part of the climb runs from 2025 into the
shaded 2026 period.

Every figure in the annotation is computed from the CSV when the chart is drawn,
so it cannot survive a refetch that changes the numbers.

## How the chart was built

[`fetch.py`](fetch.py) downloads the three per-economy Innovation Graph files —
pushes, repositories and developers — and sums each over economies for every
quarter. The EU row is an aggregate of its member states, so including it would
count those pushes twice; it is dropped. The CSV carries all three metrics and a
note recording that exclusion; the chart plots pushes.

That exclusion is the one thing in this folder that could go wrong without
looking wrong: the EU row is about a fifth of the total, and upstream renamed the
economy column from `iso2` to `iso2_code` in 2026, which is the kind of change
that can make a filter silently stop matching. [`check.py`](check.py) therefore
asserts every vendored row records the exclusion, that the quarters are
contiguous and the cumulative metrics never fall, and that the README's printed
figures match the CSV. Run with `--upstream` it also re-sums the published files
and fails if any vendored quarter is not exactly the EU-free sum:

```sh
python3 problems/output-github-pushes/check.py --upstream
```

[`figure.py`](figure.py) draws the series through
[`lib/families.py`](../../lib/families.py)'s shared volume shape: years on the
x-axis, the count on the y-axis, January 2026 onward shaded. A marker is drawn
on each quarter, since the series is twenty-five points rather than the hundreds
the monthly series carry. The five volume folders use that one shape so a
difference in appearance between any two of them is a difference in the data. It
is drawn in slate rather than the blue the other charts use for human or
uncredited finders, because this series has no authorship field at all.

## What it cannot support

- **A push is an upload event.** An agent pushing, a CI job pushing, and a
  person committing more often are the same row, and nothing in the file
  separates them.
- **The global total is assembled here.** GitHub publishes per-economy files
  rather than a world total. Economies below its 100-developer reporting
  threshold are absent from those files altogether, so the sum slightly
  undercounts, and the exclusion of the EU aggregate row is a choice made in
  [`fetch.py`](fetch.py) rather than something upstream marks.
- **No authorship labels.** The series does not record whether a human or a
  model produced the commits, so no AI share can be read off it and the
  attribution of the bend is open.
- **Volume is not discovery.** These count artifacts produced. The domain
  folders count results, and the two need not move together.
- **The file's other columns are not a denominator of effort.** The same
  download carries repository and developer counts, but they rise in every
  quarter here, including quarters in which pushes fell, so they behave like
  cumulative platform totals rather than counts of who was active. Pushes per
  developer is not readable off them without first establishing what GitHub
  means by the field.
- **Composition is invisible.** A rise is consistent with smaller and more
  frequent commits, with more automation, or with more code being written, and
  the series cannot distinguish those.

## LLM contributions

Nothing in this series is attributable to a model, by construction, and that is
worth stating plainly rather than leaving as an omission: it is a count of push
events with no authorship field, so the rise is consistent with agents pushing,
with more people pushing more often, or with both.

The timing is suggestive and no more. The steep part runs from 2025 into 2026,
which is when coding agents that commit on their own became widely available,
but the same period covers continued growth in the reported developer
population, and the discovery series in the three domain folders do not bend
over it.

## Related literature

The comparison this folder exists for is with the rest of the collection. Set it
against [curl](../cyber-curl/README.md), where a fixed codebase yields a step
change in disclosures, and against the mathematics folders, where the records
barely move. [arXiv](../output-arxiv/README.md) is the same shape over a much
longer history, and [Crossref](../output-crossref/README.md) is the control:
publishing volume rose steeply through the same period with no clean bend, so a
rising volume curve is not by itself evidence of anything new.
[Stack Overflow](../output-stackoverflow/README.md) is the direct pairing —
pushes of code roughly double while questions about code collapse. HackerOne's
platform self-report of a 210% rise in AI-attributed
vulnerability reports [@hackerone2025autonomy] is a statement of the same kind:
a count of submissions rather than of what was found.
