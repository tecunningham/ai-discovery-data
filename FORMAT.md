# Problem-page format

Problem pages are reference material. Every sentence states a fact that can be
checked — against the vendored CSVs, against a quoted source, or against a
stated scope limit. Interpretation, comparison-shopping between series, and
argument belong to the documents that cite these pages, not to the pages.
`tools/check.py` enforces the structure below and lints the register.

## Front matter

Every page opens with one `#` title and these `- **Field:**` bullet lines, in
order. They are bullets rather than bare lines because markdown joins
consecutive bare lines into one run-together paragraph:

| Field | Content |
|---|---|
| `**Domain:**` | one word: `vulnerabilities`, `mathematics`, `algorithms`, or the outside-domain label |
| `**Role:**` | one controlled phrase: `discovery series` · `prestige ledger` · `control: no-AI baseline` · `contrast case: volume` · `denominator frame` |
| `**Metric:**` | what is counted, in one sentence, including the unit and any split |
| `**Coverage:**` | the span, the cadence, and the as-of date of the last read |
| `**Data:**` | folder-local CSV links |
| `**Upstream:**` | source URLs |
| `**Verdict:**` | see below |

### Verdict

One controlled term — `accelerating`, `declining`, `no acceleration`,
`inconclusive`, `too early`, `baseline` — followed by an em-dash and one
clause comparing the 2026 rate against a historical rate: against 2025,
against a stated multi-year mean, or against both. The clause contains
numbers and units only; no argument, no cross-series comparison.

```
- **Verdict:** no acceleration — 0 dated resolutions in 2026 against 3 in 2025 and a 1.9/year mean over 2019–2025
```

A series with no meaningful 2026 measurement states why in the same shape
("too early — first observation 2026-05-30; no prior-year rate exists").

## Sections

Six `##` sections, these names, this order. Extra sections are allowed after
`Facts` (the per-item register, below) but the six must exist.

| Section | Charter — what may appear | What may not |
|---|---|---|
| `## Definition` | what the upstream is; what counts as an event; the counting and dating rules; term definitions | why the series is in the collection (that is the `Role:` field); comparisons to sibling series |
| `## Facts` | slugged fact lines (below), each recomputable from the CSVs or carrying a quote; figure embeds | readings, narrative, emphasis ("the bend is the finding") |
| `## Method` | how the data is fetched or maintained (a folder without `fetch.py` states how the CSVs are maintained — "hand-scored", "transcribed", etc.); the scoring rule; what the figure code draws; known artifacts of the pipeline | design-intent persuasion ("drawn this way so it cannot be misread") beyond a plain statement of the mapping |
| `## Limitations` | scope limits as neutral statements, one bullet each: `- **slug.** statement` | rhetorical leads, reader-coaching ("easy to over-read"), speculation |
| `## AI attribution` | a register of AI-credited events: claim, verbatim quote, named source, date; or a scoped negative ("no AI credit appears in `<source>` as of `<date>`") | synthesis across series, capability claims, predictions |
| `## Sources` | each citekey or linked source with the specific facts it supports; sibling-folder links with the relation stated factually | argument about what the sources mean |

## Fact lines

Facts are `**key:** value` bullets. Keys are short slugs, stable across
refetches; values are the numbers, phrased exactly as the folder `check.py`
recomputes them.

```markdown
- **rows:** 101 scored; 13 resolved with a dated year; 1 partial; 87 open
- **span:** dated resolutions 2019–2025
- **by-year:** 2019: 2 · 2021: 2 · 2022: 1 · 2023: 4 · 2024: 1 · 2025: 3
- **ai-attributed:** 0 of 13 dated resolutions
```

A folder with a `check.py` recomputes every numeric fact line and asserts the
exact string appears in the page. A fact that cannot be recomputed from the
vendored data carries a quote instead.

## Per-item register

Ledger and event series carry a register after `Facts`: one `###` subsection
per item whose status differs from open, headed `### <id> — <short name>`
matching the CSV's `problem_id`/`short_name` (or slug/title), holding
`**key:**` lines that mirror CSV columns, and where applicable a quote giving
the upstream wording the status rests on. The register may expand to more
rows later; the CSV remains the complete table.

```markdown
### 90 — unit distances
- **status:** disproved
- **resolved:** 2026
- **resolver:** OpenAI model; nine-author verified account (arXiv 2605.20695)
- **notes:** $500 prize; growth exponent shown to exceed 1.014

> "Solved by an OpenAI model in May 2026."
> — erdosproblems.com, problem 90, read 2026-08-14
```

## Quotes

- Form: blockquote, exact text, then an attribution line
  `> — <named source>, <locator>, <date read or published>`, plus `[@citekey]`
  where an entry exists. Every blockquote must end with such a line carrying
  a year; `tools/check.py` checks this.
- Quote rather than paraphrase: upstream status wording that a score rests
  on; any characterization of a third party's claim (press framing, vendor
  claims, maintainers' hedges); credit strings behind an AI attribution —
  quoted from the vendored CSV where one holds them.
- Attribution is to a named source. "A security firm", "the announcement",
  "its own author" do not appear; if the source cannot be named and located,
  the claim is dropped.
- Negative claims are scoped and dated: "no AI credit appears in the release
  log as of 2026-08-14", never "no credible claim exists".
- Quotes are never invented, trimmed to change meaning, or reconstructed
  from memory; ellipses mark elisions.

## Files

- The folder's primary time-series figure is `discovery-<slug>.png` and its
  CUMULATIVE.md panel is `cumulative-<slug>.png`. Both prefixes are reserved
  for exactly those names — the index and the cumulative page find the
  figures by name — and `tools/check.py` rejects a near-miss.
- Secondary figures in new folders are `<aspect>-<slug>.png`
  (`severity-cyber-openssl.png`); several older folders predate the rule and
  keep their names.
- CSV and PNG filenames are unique across all folders, not just within one:
  downstream consumers resolve them by name alone.

## Register (style)

- No first person, no reader address, no imperatives to the reader.
- No ranking of this series against siblings ("the most useful instrument",
  "the weakest aggregate"). A factual relation may be stated ("counts a
  different unit than ../cyber-nvd-disclosed").
- No inclusion apologetics, metaphor, suspense ordering, or narrative
  framing. Banned phrases are linted by `tools/check.py`: "worth stating",
  "the story of", "is the reading", "cuts the reading down", "famously",
  "remarkably", and similar; the lint list is in `STYLE_LINT`.
- Judgments live in exactly one place: the `Verdict:` field, in its
  constrained form.
- Interpretation removed in the migration to this format is dropped, not
  relocated.
