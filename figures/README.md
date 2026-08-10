# Figures

Everything here is generated. Never edit an image: change the data or the code
and re-run `make figures`.

Two generators, split by scope rather than by style.

`tools/make_figures.py` draws **one series per chart**, so a single claim can be
checked against a single picture. Those 23 figures are named
`discovery-<slug>.png` and each has its own document at `problems/<slug>.md`.
They are not listed here; the series table in the [README](../README.md) is the
index.

`tools/make_omnibus.py` draws the **cross-series comparisons**, where the point
is the contrast between series and no single panel stands alone. Those are listed
below, because a figure with no per-series document would otherwise have nothing
explaining it. Most are embedded in the source logs of
[the apple-picking project](https://tecunningham.github.io), which is where their
readings and caveats are written out.

| Figure | What it puts side by side | Built by | From |
|---|---|---|---|
| `domain-curves-cyber.png` | The six vulnerability series in one frame, so a bend in one can be read against the others | `domain_curves()` | `curl-vulnerabilities.csv`, `openssl-vulnerabilities.csv`, `firefox-advisories.csv`, `ossfuzz-discoveries.csv`, `nvd-kev-by-year.csv` |
| `domain-curves-math.png` | The mathematics bound, record and catalogue series | `domain_curves()` | `antedb-sweep.csv`, `alphaevolve-records.csv`, `erdos-database-history.csv` |
| `domain-curves-algorithms.png` | The algorithm record series, split into those AI has entered and those it has not | `domain_curves()` | `nanogpt-records.csv`, `cifar-speedrun-records.csv`, `stockfish-ncm-elo.csv`, `compression-records.csv` |
| `domain-curves-other.png` | Five output-volume series, which bend where the discovery curves do not | `other_series()` | `arxiv-monthly.csv`, `crossref-dois-by-year.csv`, `github-innovationgraph-global.csv`, `pypi-projects-over-time.csv`, `stackoverflow-questions-monthly.csv` |
| `scored-fields.png` | Scored fields chosen to span verification cost: weather, factoring, sphere packing | `scored_fields()` | `weather-forecast-skill.csv`, `weather-ml-models.csv`, `factoring-records.csv`, `sphere-packing-lower-bound-records.csv` |
| `efficiency-halving-times.png` | Fitted halving times for 66 pre-AI technologies against the quoted AI algorithmic-progress rates | `efficiency_rates()`, fitted by `owid_rates()` | `owid-66-technologies.csv` plus rates quoted in the source log |
| `problem-sets-over-time.png` | The four problem sets on a shared year axis and nothing else, because their rates are not commensurable | `problem_sets()` | `antedb-sweep.csv`, `alphaevolve-records.csv`, `owid-66-technologies.csv` |
| `antedb-small-multiples.png` | Thirty exponent slices, one raw series each, ten per family | `antedb_small_multiples()` | `antedb-sweep.csv` |
| `antedb-improvement-by-parameter.png` | Whole-record improvement ratio against the parameter, which the small multiples cannot show at a glance | `antedb_improvement_by_parameter()` | `antedb-sweep.csv` |
| `alphaevolve-frame-funnel.png` | How many of the paper's problems survive into a record-status frame | `alphaevolve_frame()` | `alphaevolve-inventory.csv` |
| `alphaevolve-record-steps.png` | AI record steps against human steps on the same quantities, pooled by kind of agent | `alphaevolve_records()` | `alphaevolve-records.csv` |
| `famous-open-problem-lists.png` | Six prestige fall-tracks plus the Erdős catalogue stock | `famous_problem_lists()` | `famous-open-problem-lists.csv`, `erdos-database-history.csv` |

## Two figures are not built here

`sources-timeline.png` and `aixcc-semifinal-vs-final.png` stay in the blog
repository's `tools/sources_figures.py`. Neither is a function of the data in
`data/`: the timeline is parsed out of the source log's own chronology table so
it cannot drift from the entries, and the AIxCC panel is plotted from figures
transcribed into a single entry.

## Reproducibility

Figures are byte-for-byte reproducible from the CSVs. That is checkable — run
`make figures` twice and nothing should change — and it is the reason
`stable_jitter()` exists: cosmetic jitter used to come from `hash()`, whose
string seed varies per process, so identical data produced a different PNG on
every run.
