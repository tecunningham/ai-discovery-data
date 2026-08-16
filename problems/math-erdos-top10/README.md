# Top 10 Erdős problems

- **Domain:** mathematics
- **Role:** prestige ledger
- **Metric:** dated resolutions per year across 12 scored rows
- **Coverage:** list posed 2026-04-16; dated resolutions 1975–2026; statuses read 2026-08-14
- **Data:** [`erdos-top10-problems.csv`](erdos-top10-problems.csv)
- **Upstream:** <https://www.erdosproblems.com/forum/thread/blog:5>, with the unit-distance row resting on the human-verified account at <https://arxiv.org/abs/2605.20695>
- **Verdict:** inconclusive — 1 resolution in 2026 against 3 in the 90 years since 1936; a series this small sets no rate

![Dated resolutions per year.](discovery-math-erdos-top10.png)

## Definition

On 2026-04-16, Thomas Bloom — the mathematician who built and maintains
erdosproblems.com — published a list of what he considers the most important
Erdős problems, solved and unsolved [@bloom2026top10]. The list has ten
entries naming twelve of the site's problem numbers: 3, 139, 4, 20, 28, 52,
61, 67, 77, 90, 571 and 713. The progressions entry spans numbers 3 and 139,
and the Turán-exponents entry spans 571 and 713, so this ledger scores twelve
rows. Bloom states the list's basis:

> "Naturally this is very subjective (and probably will change even for
> myself day to day), and others are welcome to post in the comments their
> own candidates."
> — Thomas Bloom, Top 10 Erdős Problems, erdosproblems.com forum, 2026-04-16 [@bloom2026top10]

A "discovery" in this series is a row with status resolved, dated by the year
of the resolving work. Statuses and years are scored from the blog post's own
discussion of each problem; the one resolution after the post's date (problem
90) is scored from the sources named in its register entry.

## Facts

- **rows:** 12 scored; 4 resolved with a dated year; 8 open
- **by-year:** 1975: 1 · 2016: 2 · 2026: 1
- **ai-attributed:** 1 of 4 dated resolutions
- **open rows:** 3, 20, 28, 52, 61, 77, 571, 713
- **prizes stated in the post:** $5000 (problem 3) · $10000 (problem 4) · $1000 (problem 20) · $500 (problem 67) · $500 (problem 90)

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws the
ledger as rows remaining:

![Rows remaining without a dated resolution.](cumulative-math-erdos-top10.png)

### 4 — Large gaps between primes
- **status:** resolved
- **resolved:** 2016
- **resolver:** Maynard; Ford–Green–Konyagin–Tao
- **notes:** $10000 prize

> "Erdős' belief in the difficulty of this problem was well-founded - it was
> over 60 years since he asked this question till it was solved by Maynard
> [Ma16] and Ford, Green, Konyagin, and Tao [FGKT16]"
> — Thomas Bloom, Top 10 Erdős Problems, erdosproblems.com forum, 2026-04-16 [@bloom2026top10]

### 67 — Erdős discrepancy problem
- **status:** resolved
- **resolved:** 2016
- **resolver:** Tao
- **notes:** $500 prize; the year matches the imputed solution year in [`../math-erdos/`](../math-erdos/README.md)'s independent dating

> "This was resolved in the affirmative by Tao [Ta16]"
> — Thomas Bloom, Top 10 Erdős Problems, erdosproblems.com forum, 2026-04-16 [@bloom2026top10]

### 90 — Unit distances
- **status:** resolved
- **resolved:** 2026
- **resolver:** OpenAI model
- **notes:** negative resolution after the list was posed; the growth exponent is shown to exceed 1.014; the sharp form of the question remains open

At the post's date Bloom recorded the problem open:

> "Erdős conjectured many times (and offered $500 for a solution) that this
> was best possible"
> — Thomas Bloom, Top 10 Erdős Problems, erdosproblems.com forum, 2026-04-16 [@bloom2026top10]

The resolution is the vendor announcement of 2026-05-20, titled

> "Model disproves discrete geometry conjecture"
> — OpenAI, announcement title, 2026-05-20 [@openai2026discretegeometry]

with the argument digested by nine mathematicians into a human-verified
account (arXiv 2605.20695) and the explicit exponent, greater than 1.014,
stated by Sawin (arXiv 2605.20579). The catalogue's imputed-year dataset
records the same event: problem 90, disproved, 2026, dated by the AI wiki at
2026-05-20 ([`../math-erdos/`](../math-erdos/README.md),
`erdos-solution-years.csv`).

### 139 — Density version of long progressions
- **status:** resolved
- **resolved:** 1975
- **resolver:** Szemerédi
- **notes:** posed with Turán in 1936

> "the resolution of [139] was achieved by Szemerédi [Sz75] in 1975 using a
> very different, purely combinatorial, argument"
> — Thomas Bloom, Top 10 Erdős Problems, erdosproblems.com forum, 2026-04-16 [@bloom2026top10]

## Method

The rows are hand-scored from the blog post: each entry's discussion states
whether the problem is solved and by whom, and the resolution years for rows
4, 67 and 139 equal the imputed solution years the
[math-erdos](../math-erdos/README.md) folder derives independently from the
catalogue's own pages. Row 90's status postdates the post and is scored from
the 2026-05-20 sources quoted in its register entry; its `source` column
names them. There is no `fetch.py`.

[`figure.py`](figure.py) calls the shared `problem_list_chart()` in
[`../../lib/families.py`](../../lib/families.py) with `ai_problem="90"`,
counting rows with status resolved and a non-empty `resolved_year` by year;
the `ai_caption` argument sets the annotation to that row's verification
standing (an AI disproof with a human-verified account). The cumulative view
is the shared `ledger_remaining_chart()`.

## Limitations

- **selection.** The list is one mathematician's judgment, posed in 2026
  with knowledge of which problems had fallen and how; a solved problem can
  be selected partly because its solution was celebrated.
- **sample size.** Four dated resolutions in ninety years; no rate or trend
  is estimable from this series.
- **row 90 is a partial negative resolution.** The conjectured bound is
  refuted; the exact growth exponent remains open, and the row rests on a
  human-verified account of a model's argument rather than on formal kernel
  checks or completed peer review.
- **overlap.** All twelve rows are entries of the catalogue scored in
  [math-erdos](../math-erdos/README.md); the two ledgers are not independent.
- **resolution landmarks are not effort-adjusted discovery rates.**

## AI attribution

One row. Problem 90 (unit distances) is credited to an OpenAI model on
2026-05-20, per the vendor announcement and the nine-author verified account
quoted in its register entry [@openai2026discretegeometry]. No other row's
resolution or open status carries any AI credit in the blog post or on the
catalogue's pages as of 2026-08-14. The catalogue-wide AI-contribution
record is the frozen wiki [@erdosproblems2026wiki].

## Sources

- [@bloom2026top10] — the list, its entries, and the status discussion every
  row except 90 is scored from.
- [@openai2026discretegeometry] — the 2026-05-20 unit-distance disproof:
  vendor announcement, the nine-author verified account (arXiv 2605.20695),
  and Sawin's explicit exponent (arXiv 2605.20579).
- [@erdosproblems2026catalogue] — the catalogue the twelve problem numbers
  index into.
- [@erdosproblems2026wiki] — the AI-contribution wiki, frozen 2026-06-30.
- Sibling ledgers over the same corpus or of the same instrument type:
  [math-erdos](../math-erdos/README.md) (full catalogue),
  [math-green](../math-green/README.md),
  [math-hilbert](../math-hilbert/README.md),
  [math-smale](../math-smale/README.md),
  [math-millennium](../math-millennium/README.md).
