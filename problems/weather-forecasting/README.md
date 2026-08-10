# Weather forecasting

**Domain:** outside the three domains
**Metric:** numerical weather prediction; forecast days of useful skill on 500 hPa geopotential height, plus the dated arrival of machine-learning models that beat the physics incumbent
**Coverage:** skill anchors 1980 and 1985, rate claim published 2015; model arrivals 2022-02 to 2025-02
**Data:** [`weather-forecast-skill.csv`](weather-forecast-skill.csv), [`weather-ml-models.csv`](weather-ml-models.csv)
**Upstream:** <https://www.ecmwf.int/en/forecasts/quality-our-forecasts>, <https://www.nature.com/articles/nature14956>, and each model's own paper or announcement
**Verdict:** no acceleration — the skill trend did not bend; the cost of producing a forecast fell by about three orders of magnitude


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

There is no chart. The skill series is not a digitized time series: two text-stated
anchors (5.5 days in 1980, 6.5 days in 1985) and a stated rate of about a day a
decade, with the arrival dates of the machine-learning models recorded beside
them. Drawing that as a line would present a claim as if it were a measurement,
so the folder keeps the CSVs and the reading without a figure.

The reading itself is unchanged. Four ML models beat the physics incumbent
between 2022 and 2025, ECMWF made its own AIFS operational on 2025-02-25, skill
gains are reported at 4 to 25%, and energy use fell by about a thousandfold —
while nothing in the sources claims the forty-year one-day-per-decade trend
steepened.

## How the chart was built

There is no figure and no `figure.py`. The folder is kept for the two CSVs and
the document: `weather-forecast-skill.csv` holds the text-stated anchors and the
stated rate, and `weather-ml-models.csv` holds the dated model arrivals. Neither
is a digitized series, so they are not plotted.

There is no fetcher. ECMWF's live skill chart blocks automated fetching, which
is why the vendored file holds text-stated anchor points and a stated rate
rather than a measured series, and why a figure would overclaim. Digitizing the
published skill chart is the fix if a plotted series is wanted later.


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
