# Weather forecasting

**Domain:** outside the three domains
**Metric:** numerical weather prediction; forecast days of useful skill on 500 hPa geopotential height, plus the dated arrival of machine-learning models that beat the physics incumbent
**Coverage:** skill anchors 1980 and 1985, rate claim published 2015; model arrivals 2022-02 to 2025-02
**Data:** [`weather-forecast-skill.csv`](weather-forecast-skill.csv), [`weather-ml-models.csv`](weather-ml-models.csv)
**Upstream:** <https://www.ecmwf.int/en/forecasts/quality-our-forecasts>, <https://www.nature.com/articles/nature14956>, and each model's own paper or announcement
**Verdict:** no acceleration — the skill trend did not bend; the cost of producing a forecast fell by about three orders of magnitude

![Weather forecast skill: two stated anchors, the stated one-day-per-decade rate drawn forward as a dashed line, and the 2022 to 2025 arrival of machine-learning models.](discovery-weather-forecasting.png)

## The problem

Weather is the case that should have been easiest for AI to win, and it is here
because of that. The metric is fixed and old, the baseline is four decades long
and densely dated, and the verifier is the cheapest there is: reality checks the
forecast within days, blind, for free, and it is checked by the institution that
owns the incumbent model rather than by the challenger. If cheap verification
were sufficient for AI to accelerate discovery, this is where it would show.

The headline series ECMWF publishes is the "forecast lead-time at which the
anomaly correlation of the HRES 500 hPa geopotential reaches 80% for the
extra-tropical northern hemisphere" — one atmospheric variable, one correlation
threshold, scored against what the weather actually did.

A discovery in this folder is a gain in that lead time. That is the awkward part
of the case and the reason it earns its own category: what machine learning
delivered here is not obviously a gain in lead time at all.

## What the chart shows

Two filled points and a dashed line, and they are not the same kind of thing.

The filled points are the two dated anchors that exist in text: northern
hemisphere useful forecast length of 5.5 days in 1980 and 6.5 days in 1985. The
dashed line is the rate the literature states — "the skill of deterministic
'best-guess' weather forecasts in the range from 3 to 10 days ahead has improved
by about a day a decade" — drawn forward from the 1985 anchor to 2026. That line
is a claim about the trend, not a measurement of it, and the figure labels it as
such.

The red triangles along the bottom are the arrivals of six machine-learning
models between February 2022 and 2025, plotted at their dates; their height
carries no value. Four beat the physics incumbent on its own class of metric:
FourCastNet, which "matches the forecasting accuracy of the ECMWF Integrated
Forecasting System (IFS) … at short lead times … while outperforming IFS for
small-scale variables"; Pangu-Weather, where "for the first time, an AI-based
method outperforms state-of-the-art numerical weather prediction (NWP) methods
in terms of accuracy … of all factors … and in all time ranges"; GraphCast,
"significantly more accurate than the ECMWF's deterministic forecasting system,
HRES, on 89.3% of the 2760 target variables and lead times we evaluated"; and
GenCast, "more accurate than ENS on 97.2% of these targets, and on 99.8% at lead
times greater than 36 hours".

The dotted vertical line is the fact that carries the most weight. ECMWF's own
AIFS became operational on 25 February 2025, so the organization that owns both
the physics model and the verification framework adopted a machine-learning
model in production. At that point the capability claim stops being a vendor
claim.

Set the two magnitudes side by side, which is what the annotation does. ECMWF
reports that AIFS "outperforms state-of-the-art physics-based models for many
measures … with gains of up to 20%", the ensemble scorecard showing
"improvements reach up to 25%" with overall skill improving 4–6% in v1.1 — and
"a reduction of approximately 1,000 times in energy use". Percentages on skill;
three orders of magnitude on cost. Nothing in the sources examined claims the
forty-year one-day-per-decade trend has measurably steepened.

## How the chart was built

[`figure.py`](figure.py) reads both CSVs. The anchors are the rows whose metric
begins `useful_forecast_length`; the dashed line starts at the later anchor and
rises at the rate stored in the `skill_gain_rate_500hPa_Z` row, so the slope
comes from the file rather than from the code. The arrival markers are one per
row of `weather-ml-models.csv`, placed at the first dated release in the row's
`date` field, and the dotted vertical is the operational date named in the AIFS
row.

There is no fetcher. ECMWF's live skill chart blocks automated fetching, which
is why the vendored file holds text-stated anchor points and a stated rate
instead of a digitized series, and the model claims are quotations transcribed
by hand from each paper or announcement. Digitizing the published skill figure
is the obvious way to improve this folder.

The legend distinguishes the measurement from the claim, and the markers are
kept off the skill scale, because the one thing this chart must not do is imply
a forty-year series that nobody here read.

## What it cannot support

- **The dashed line is not data.** It is the source's stated rate drawn forward
  from one anchor. It cannot be used to read a value off any particular year,
  and it certainly cannot be used to detect a bend.
- **The anchors and ECMWF's headline series use different thresholds.** The two
  vendored anchors are a useful forecast length at an anomaly correlation of
  0.6, quoted from a 2003 review citing ECMWF and Kalnay; ECMWF's own headline
  series uses 80%. They are not interchangeable.
- **The model claims are their developers' own**, including ECMWF's for AIFS,
  and none was independently reproduced here.
- **GenCast is scored on a different axis.** CRPS is a probabilistic ensemble
  score, so its 97.2% is not comparable to the deterministic anomaly-correlation
  series.
- **The learned models are downstream of the physics system.** GraphCast, Pangu,
  GenCast and AIFS are trained on ERA5 reanalysis, which is itself the output of
  ECMWF's physics-based 4D-Var data assimilation. They are bounded by, and
  derived from, the system they outperform, so they are not an independent route
  to the same knowledge.
- **Physics still wins on the cases that carry the value.** A 2026 paper's title
  states the finding: "Physics-based models outperform AI weather forecasts of
  record-breaking extremes." The aggregate score improves while the extremes do
  not, which is the same shape as the proxy-versus-objective gap seen elsewhere.
- **A cost collapse is not nothing.** Reading this folder as a null would be as
  wrong as reading it as an acceleration. A thousandfold cut in the energy cost
  of a forecast is a large change; it is a change in a different variable.

## LLM contributions

None, and the distinction matters for the collection. The systems here are
domain-specific weather emulators — graph neural networks, transformers, and a
diffusion model — trained on reanalysis data, not language models and not
agents. No source claims a language model contributed to any of these results.

What the folder contributes is a category. Elsewhere the question is whether AI
found something; here AI reproduced an existing capability at roughly the same
accuracy and about a thousandth of the energy. That is the third case the
collection turns on: volume up, cost down, discovery rate roughly unchanged.

## Related literature

The cost reading belongs next to
[technology cost curves](../technology-cost-curves/README.md), where halving
times for 66 pre-AI technologies set the scale against which a thousandfold cut
should be judged. The verification-cost argument belongs next to
[integer factorization](../integer-factorization/README.md), the other cheap
verifier outside the three domains, where the record series simply stopped: two
domains where checking an answer is nearly free, and neither shows a discovery
curve bending. For the contrast with volume, see
[arXiv submissions](../output-arxiv/README.md) and the four series beside it.
