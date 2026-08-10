# Integer factorization records

**Domain:** outside the three domains
**Metric:** cryptanalysis; decimal digits in the largest hard semiprime factored, as a running maximum
**Coverage:** 1991-04 to 2020-02, confirmed unmoved as of 2026-07-29
**Data:** [`factoring-records.csv`](factoring-records.csv) (all 23 published RSA factorizations, plus the 795-bit discrete-logarithm record and the first SHA-1 collision for context)
**Upstream:** <https://en.wikipedia.org/wiki/RSA_numbers>, with the last two records from <https://caramba.loria.fr/rsa250.txt> and <https://caramba.loria.fr/dlp240-rsa240.txt>
**Verdict:** no acceleration — no record since February 2020, and the fourfold slowdown before that predates AI entirely

![Integer factorization records: the running maximum in decimal digits, rising from 1991 to 2020 and flat thereafter, with every published RSA factorization behind it.](discovery-integer-factorization.png)

## The problem

Factoring is the cheap-verifier extreme, and it is here for the same reason
weather is: to span the cost of checking an answer, which the three worked
domains barely vary. Multiplying two claimed factors takes microseconds, so a
result is verified instantly, for free, by anyone. The field also has everything
else a scoreboard needs — a published list of targets, three decades of dated
records with named teams, and a cash-prize history.

A discovery here is one new largest factorization. That is a coarse instrument
by construction: the record is a running maximum over a fixed list of targets,
so it moves only when someone commits a very large computation to the next
number on the list.

## What the chart shows

Thirteen records between April 1991 and February 2020, and nothing since.

The rate falls fourfold inside the series, well before AI: about 7.1 digits a
year from RSA-100 in 1991 to RSA-768 in December 2009, then about 1.8 a year to
RSA-250 in February 2020. Both figures are computed in the figure code from the
running maximum. RSA-250 has stood for six years and four months, across exactly
the period in which AI systems were setting records on speedruns, kernels, a SAT
competition, and a dozen mathematical bounds. RSA-260, RSA-270, RSA-896 and
RSA-1024 remain unfactored.

The open markers behind the line are every published RSA factorization,
including the ones that were not records — RSA-170, RSA-180, RSA-190, RSA-210
and others, factored in the 2010s while the maximum stood at 232 digits. They
are there so a flat line is not misread as nobody working.

Every record in the series is the number field sieve, or the quadratic sieve for
the earliest ones, run as a large parallel computation by a human team. The
`ai_involved` column is `no` on all 23 rows.

## How the chart was built

[`figure.py`](figure.py) filters `factoring-records.csv` to the
`integer_factorization` rows, sorts by date, and takes the running maximum over
`digits` as a step function; the two adjacent records in the file, a discrete
logarithm and a hash collision, are excluded because they are different
quantities. Three records are labelled — the first, the last of the fast era,
and the current one — and the rest are left unlabelled to keep the steps
readable. The rates in the annotation are computed at plot time from the running
maximum, split at RSA-768, so they cannot drift from the CSV. January 2026
onward is shaded, as in every figure here.

There is no fetcher. The record list is a hand-maintained page rather than an
API, the last two records come from the record-setters' own announcements, and
the fields that matter here — who, which method, whether machine learning was
involved — need reading rather than parsing.

## What it cannot support

- **A stalled record is not a demonstration that AI could not do it.** No one
  has published a serious AI-assisted attempt. The arithmetic is not the kind of
  task current systems are pointed at, and no attempt means no evidence either
  way.
- **The prize is gone, which is a sufficient explanation on its own.** The RSA
  Factoring Challenge was formally discontinued in 2007, so the 2019 and 2020
  records were one-off academic efforts.
- **A record here costs real money.** RSA-250 took "roughly 2700 core-years",
  and RSA-768 was reported as "the equivalent of almost 2000 years of computing
  on a single-core 2.2 GHz AMD Opteron". The stall is not disinterest in a cheap
  prize.
- **Thirteen points cannot detect a modest change in rate.** The series is dense
  enough to show a fourfold slowdown and a six-year stop; it is far too sparse
  to rule out a smaller effect.
- **The running maximum hides the work.** Effort that goes into a number smaller
  than the current record leaves no mark on the line at all, which is why the
  non-record factorizations are drawn.

## LLM contributions

None recorded anywhere in the series. The one announcement that separates
algorithm from hardware attributes the gain to human work: the RSA-240 team
report that "our computation was 3 times faster than the expected time that
would have been extrapolated from previous records", and that "the acceleration
can be attributed to various algorithmic improvements that were implemented for
these computations. The CADO-NFS implementation was also vastly improved." So
the last real step in this series was human algorithmic and implementation work
worth about 3x against a hardware-adjusted baseline.

The two adjacent records in the file point the same way. The 795-bit discrete
logarithm was set by the same team on the same day as RSA-240, and the first
SHA-1 collision was published in February 2017 by a Google and CWI team using a
differential path and about 2^63.1 hash evaluations. Neither involved machine
learning either.

## Related literature

Grace's 2013 survey of algorithmic progress in six domains recorded factoring
improving "about 5.5 digits per year for the last two decades"
[@grace2013algorithmic], which this series confirms for the window she had and
which makes the subsequent deceleration visible as a departure from a documented
trend. The heterogeneity of pre-AI improvement rates across algorithm families
is Sherry and Thompson's subject [@sherry2021fast], and it is the reason a single
stalled family is weak evidence on its own. Within this collection the natural
comparison is [weather forecasting](../weather-forecasting/README.md), the other
cheap verifier outside the three domains, and
[sphere packing](../math-sphere-packing/README.md), where a similarly old ladder
took its two largest steps since 1947 in 2023 and 2025 — both of them human
proofs.
