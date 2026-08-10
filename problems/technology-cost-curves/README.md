# Technology cost curves: the pre-AI efficiency baseline

**Domain:** outside the three domains
**Metric:** 66 industrial and scientific technologies; months to halve unit cost, fitted log-linearly per technology, set against the halving times quoted for AI algorithmic progress
**Coverage:** 1929–2013 for the cost curves; 2012–2023 for the three AI estimates they are compared with
**Data:** [`owid-66-technologies.csv`](owid-66-technologies.csv), [`ai-efficiency-rates.csv`](ai-efficiency-rates.csv)
**Upstream:** <https://ourworldindata.org/grapher/costs-of-66-different-technologies-over-time>, adapted by Our World in Data from the Santa Fe Performance Curve Database as compiled by Farmer and Lafond (2016)
**Verdict:** baseline

![Left: the years each efficiency measurement covers, for seven physical cost curves and three AI algorithmic-progress estimates. Right: halving times on a log axis, with published intervals and Moore's law marked at 24 months.](efficiency-halving-times.png)

## The problem

This folder is not evidence about AI. It is the ruler the other folders are read
against.

Every claim that AI has bent an efficiency curve needs an answer to the obvious
question: bent relative to what? Steady exponential improvement is the normal
case for a technology, and it was the normal case for decades before anyone
trained a model. These 66 series are the widest consistently measured picture of
that baseline — unit cost against year, across chemicals, semiconductors,
energy, transport and biology — and all of them end before AI played any part in
them.

There is no discovery event here at all. The unit is a rate: how long a
technology takes to halve its unit cost.

## What the chart shows

The right panel is the comparison. Language-model pretraining compute to a fixed
loss halves about every 8 months, with a published interval of 5 to 14 months;
ImageNet compute-augmenting algorithmic advances every 9 months, interval 4 to
25; compute to reach AlexNet-level accuracy every 16 months. Against them: DNA
sequencing at 8.6 months, hard disk drives at 13.0, transistors at 17.2, DRAM at
19.1, laser diodes at 24.0, all fitted here from the CSV. Moore's law sits on the
same axis at 24 months.

The fastest measured AI rate and the fastest measured physical cost curve are the
same number to within the confidence intervals, and the AI rates sit inside a
range that ordinary industrial technologies occupied decades ago. That is the
whole content of the figure.

The left panel exists to stop the right one being over-read. Each rate is
measured over its own window, and the windows barely overlap: the physical curves
are mostly mid-twentieth century and all end by 2013, while the AI estimates all
begin in 2012 and none extends past 2023. Nothing here is a contemporaneous
like-for-like comparison, and none of it covers the agent era.

Two facts about the distribution matter for how the seven plotted curves are
read. Of the 66 series, 65 have a falling log-linear fit and one rises — nuclear
electricity, 1970 to 1989. And only five halve faster than every two years: the
median falling series takes decades, so rapid exponential improvement is the
exception across technologies even though it is the norm among the ones anybody
writes about.

## How the chart was built

The three AI rates the physical curves are compared against are quotations, not
measurements: each is a halving time an author fitted and published, with the
interval they gave. They sit in [`ai-efficiency-rates.csv`](ai-efficiency-rates.csv)
with the source-log anchor that carries each quote, rather than in the figure
code, because the source log's own evidence-coverage figure plots the same three
measurement windows — a rate transcribed in two places is a rate that will
eventually disagree with itself. Recomputing any of them here would invent a
number the source did not state.

[`figure.py`](figure.py) fits each entity in the OWID CSV separately: a log-linear
regression of cost on year, converted to a halving time in months, keeping
series with at least five observations and a falling fit. A fit is used rather
than an endpoint ratio so that one noisy first or last observation cannot set
the rate on its own. The seven fastest go in the left panel and the five fastest
in the right.

The three AI rates are not fitted. They are quotations, hardcoded as `AI_RATES`
in the figure code with the interval each source published — Epoch AI's estimate
for language-model pretraining, the ImageNet algorithmic-advances estimate, and
the compute-to-AlexNet figure — and the entry each came from is named in the
constant. Keeping them as constants rather than recomputing them is deliberate:
they are other people's published numbers, and this folder's arithmetic should
not be mistaken for a re-estimate.

There is no fetcher. The CSV is Our World in Data's own chart download, vendored
here unchanged, and the underlying dataset stopped in 2013 and will not move.

## What it cannot support

- **The data stops in 2013**, so this dataset cannot speak to AI's effect on
  anything. It establishes the shape and scale of the outcome variable, and
  nothing more.
- **Levels are not comparable across series.** The chart's own subtitle says the
  cost of each technology is "expressed in different units, chosen for
  visualization purposes", and DNA sequencing is divided by 1000 to fit the
  chart. Only within-series rates of change mean anything.
- **A halving time compresses a whole series to one number.** Where a curve
  bends, the fit averages over the bend, and the fitted rate will match no
  particular decade.
- **The nearly flat series are excluded on judgment.** A fitted halving time of
  several centuries is arithmetically fine and substantively meaningless, which
  is why only the fastest curves are plotted; the choice of seven and five is a
  legibility decision, not a statistical one.
- **The AI rates are quoted, not verified here.** Their intervals are their
  authors', they are measured on different quantities from each other, and two
  of the three concern image models rather than the systems in the agent era.
- **A cost curve is not a discovery curve.** Efficiency improving on a fixed
  task is the thing this collection keeps finding; it is not the thing the
  collection is trying to measure.

## LLM contributions

None to the underlying series, by construction: every technology here stopped
being measured in 2013 at the latest.

The folder's relevance to language models is entirely as a comparator, and it
cuts against the strongest version of the AI story. The rates quoted for
algorithmic progress in AI are fast, and they are not unprecedented — DNA
sequencing halved its cost faster over 2001 to 2013 than language-model
pretraining compute has halved since 2012.

## Related literature

Sherry and Thompson measure improvement rates across algorithm families and find
them wildly heterogeneous, with most families improving slowly and a few
extremely fast [@sherry2021fast]; that is the algorithmic counterpart to the
skew in these cost curves. Grace's survey of algorithmic progress in six domains
is the older version of the same exercise [@grace2013algorithmic]. Epoch AI has
since published a much faster stated estimate for current AI algorithmic
progress, around a factor of ten a year with an 80% interval of two to fifty, and
labels it a best guess rather than a measured series [@epoch2026driver] — which
would sit far off the right-hand side of this chart if it were plotted, and is
the reason the plotted rates are restricted to estimates with published
intervals. Within this collection, the cost reading in
[weather forecasting](../weather-forecasting/README.md) is the one place an
agent-era cost curve can be compared against these, and
[output volume](../output-volume/README.md) is the other variable that visibly
moves.
