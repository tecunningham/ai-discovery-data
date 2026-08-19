# Appendix: additional discovery candidates

This is the research backlog for series and analyses that look promising but do
not yet meet the repository's inclusion standard. A row here is a lead, not a
validated time series: its unit of discovery, historical coverage, source
stability and rebuild path still need to be audited before it becomes a problem
folder.

There are two importantly different kinds of project here:

1. **Direct discovery-event series**, where each observation is genuinely a new
   entity, result, bound or validated performance record.
2. **Quasi-experimental analyses of AI exposure**, which use treatment timing or
   differential exposure to say more about causality than a trend line can.

## A useful AlphaFold template

Hill and Stein's 2026 paper,
[“How Artificial Intelligence Shapes Science”](https://carolynstein.github.io/files/papers/alphafold.pdf),
is close to the natural experiment this project should emulate. Experimental
structure determination itself barely changed, but downstream research on
proteins that lacked structural information before AlphaFold increased by about
15–40% relative to proteins that already had structures. Proteins without prior
structures are more exposed to the AlphaFold shock, giving the comparison a
clear treatment mechanism.

## Candidate discovery-event datasets

Each candidate is scored on the five things that decide whether it can become a
problem folder here, replacing the earlier single letter grade. Every column is
✅ (2 points), 🟡 (1) or ❌ (0), and the rows are ordered by the total out of 10;
ties keep the earlier ordering. The criteria are:

- **Unit** — is "one discovery" a crisp, stable event? ✅ crisp · 🟡 needs a
  dedup or matching rule · ❌ ill-defined.
- **History** — can events be dated consistently, far back? ✅ clean deep dates ·
  🟡 recoverable with per-entry work · ❌ hard to recover.
- **Rebuild** — a public, stable, scriptable source? ✅ bulk or API, clean · 🟡
  public but messy or licence-limited · ❌ not readily rebuildable.
- **Frontier** — a genuine frontier or first-of-kind, not instrument throughput?
  ✅ yes · 🟡 mixed, needs isolating · ❌ throughput-dominated.
- **AI signal** — can observations be tied to AI, by attribution or exposure? ✅
  strong · 🟡 plausible but indirect · ❌ low exposure. A ❌ here is not
  disqualifying: several rows are wanted precisely as low-exposure controls,
  and the note says so.

| Candidate | Unit | History | Rebuild | Frontier | AI signal | Score | Main blocker / note |
|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **Drug discovery — [BindingDB](https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp?all_download=yes)** · first ligand below 1 µM / 100 nM / 10 nM per target, then affinity records | ✅ | ✅ | ✅ | ✅ | ✅ | **10** | Millions of measured affinities carrying publication and curation dates. Medicinal chemistry is highly AI-exposed and it anchors the AlphaFold-style design #4 — the cleanest all-round candidate. |
| **Solar / materials — [NREL Best Research-Cell Efficiency](https://www.nrel.gov/pv/interactive-cell-efficiency.html)** · independently confirmed cell-efficiency records | ✅ | ✅ | ✅ | ✅ | 🟡 | **9** | A decades-long physical performance frontier across PV technologies, not a paper count. AI exposure is only moderate; the value is a confirmed-record frontier. |
| **Materials — [Starrydata](https://docs.starrydata.org/datasets/)** · thermoelectric ZT, battery capacity/retention, magnetic frontiers | ✅ | ✅ | ✅ | ✅ | 🟡 | **9** | Open dataset linking experimental curves to papers; supports many reconstructed frontiers (design #7). A quantity has to be chosen and standardized, and materials AI exposure is real but diffuse. |
| **Enzymology — [ENZYME](https://enzyme.expasy.org/) + [BRENDA](https://www.brenda-enzymes.org/)** · first characterization of each EC activity | ✅ | 🟡 | 🟡 | ✅ | ✅ | **8** | A newly demonstrated catalytic activity is close to a stable unit of biological function. Dates are recoverable only per-entry from BRENDA, whose licence restricts redistribution — the two soft spots. |
| **Structural biology — [Protein Data Bank](https://www.rcsb.org/)** · first experimental structure per UniProt protein / Pfam family | 🟡 | ✅ | ✅ | 🟡 | ✅ | **8** | Deposition and release dates are clean and AlphaFold makes it highly AI-exposed. Needs a dedup rule to turn raw structure throughput into first-of-kind events. |
| **Astronomy — [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html)** · confirmed exoplanets, especially re-found in archival Kepler/TESS data | 🟡 | ✅ | ✅ | 🟡 | ✅ | **8** | Discovery year, method, facility and instrument are all programmatic. The raw count is detector-limited throughput; the AI-legible frontier is the archival-reanalysis subset (design #6), which must be carved out. |
| **Algorithms — [Algorithm Wiki](https://algorithm-wiki.org/) (MIT FutureTech)** · first algorithm to improve a family's best-known time or space complexity | ✅ | ✅ | 🟡 | ✅ | 🟡 | **8** | Roughly 1,907 catalogued algorithms across 100+ problem families, each with publication year and complexity classes — the theoretical counterpart to the solver and speedrun folders. Curation verified active through a 2025-11 follow-up paper; whether any 2026 entries exist is unverified, and licence and export stability are the other open audits. See the [Algorithm Wiki section](#algorithm-wiki-mit-futuretech) below. |
| **Superconductivity — NIMS SuperCon** · new superconductors, record critical-temperature frontier | ✅ | 🟡 | 🟡 | ✅ | 🟡 | **7** | More than ten thousand materials with transition temperatures and citations. Whether consistent first-report dates can be recovered is the open audit question, and access is a database rather than a clean bulk file. |
| **Medical genetics — [ClinVar archives](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/)** · first high-confidence pathogenic variant–disease call | 🟡 | ✅ | ✅ | 🟡 | 🟡 | **7** | Retained monthly releases let you reconstruct new expert-reviewed classifications and later state transitions rather than counting all submissions. The "high-confidence + first" rule still has to be pinned. |
| **Particle physics — [PDG historical editions](https://pdg.lbl.gov/rpp-archive/)** · precision frontiers for masses, lifetimes, couplings | 🟡 | ✅ | 🟡 | ✅ | 🟡 | **7** | Editions reach back to 1957; recent ones have an API, older ones are PDF archaeology. It is a constructed uncertainty-fall index rather than discrete events, and fundamental-constant precision is only weakly AI-exposed — useful partly as a low-exposure frontier. |
| **Genetics — [GWAS Catalog](https://www.ebi.ac.uk/gwas/docs/programmatic-access)** · first significant independent locus–trait association | 🟡 | 🟡 | ✅ | 🟡 | 🟡 | **6** | Curated associations with downloads and an API. Needs an "independent locus" rule and depends on reconstructing first-arrival from historical releases or publication dates. |
| **Chemistry — [Open Reaction Database](https://github.com/open-reaction-database/ord-data) + USPTO** · first transformations between reaction classes / yield frontiers | 🟡 | 🟡 | ✅ | 🟡 | 🟡 | **6** | ORD preserves structured conditions, outcomes and provenance. The matching rule for a "novel transformation" is unresolved and USPTO dates are patent-filing dates — both need design work. |
| **Cryo-EM — [EMDB releases](https://www.ebi.ac.uk/emdb/statistics_main.html)** · first structure per biological target | 🟡 | ✅ | ✅ | ❌ | 🟡 | **6** | An exceptionally clean release series (640 in 2015, 3,820 in 2020, 11,657 in 2025), but the rise reflects microscopes and methods more than AI. Best after deduplication, and most useful as a throughput comparison or control. |
| **Gravitational waves — [GWOSC](https://gwosc.org/eventapi/)** · catalog events per observing day | ✅ | ✅ | ✅ | ❌ | ❌ | **6** | Clean, machine-readable events, but discovery is strongly detector-sensitivity constrained and AI exposure is low. Include it explicitly as a negative / low-exposure control (designs #2, #10), not as a positive AI series. |
| **Weakness classes — [CWE](https://cwe.mitre.org/) composition of CVE series** · NVD's per-CVE CWE assignments as a composition cut | ❌ | ✅ | ✅ | ❌ | 🟡 | **4** | Not a discovery series of its own: CWE is a taxonomy, and its value here is as a dimension on the existing CVE series — whether agent-era disclosures differ in *kind* (use-after-free vs injection vs XSS), a depth signal orthogonal to severity. Would extend the NVD folder with per-year counts for the top weakness classes; assignment coverage and NVD's analysis backlog are the caveats. |

## Algorithm Wiki (MIT FutureTech)

The [Algorithm Wiki](https://algorithm-wiki.org/)
([MediaWiki instance](https://algorithm-wiki.csail.mit.edu/wiki/Main_Page)) is
the living continuation of Sherry and Thompson's 2021 "How Fast Do Algorithms
Improve?" dataset — the same paper cited from the main README as the base rate
for how rarely algorithm families improve. It now holds roughly 1,907 algorithm
records across 100+ problem families, each carrying publication year, time
complexity and space complexity, with a
[custom dataset export](https://algorithm-wiki.org/download) and a bulk
download on the [FutureTech datasets page](https://futuretech.mit.edu/datasets).
As a problem folder it would count one event per published algorithm that
improved a family's best-known asymptotic complexity, plotted as improvements
per year since 1940 — a genuine frontier series, and a useful low-AI-exposure
contrast (design #10) with one already-AI-credited exception: the 2026
matrix-multiplication exponent record in
[`problems/matrix-omega/`](problems/matrix-omega/), whose family the wiki also
tracks.

### How up to date is it?

Verified as of 2026-08-19:

- The 2021 paper compiled 113 families from 57 textbooks and more than 1,110
  research papers, with coverage effectively through the late 2010s.
- A follow-up survey of space complexity
  ([arXiv 2511.22084](https://arxiv.org/abs/2511.22084), submitted 2025-11-27)
  reuses and extends the same dataset — 118 problems, 800+ algorithms — so
  curation was active through late 2025.
- Whether any 2026-dated algorithm appears in the wiki is not verified: the
  wiki and the FutureTech datasets page were unreachable from the session that
  wrote this entry (network egress blocked), and no indexed page settles it.
  Until the export is inspected, coverage should be assumed to end near the
  2025 survey's compilation, with 2026 absent.

The censoring consequence matters more than the average lag: the most recent
bins of a per-year series built from the wiki would count when curators caught
up, not when improvements were published, so 2024–2026 bins under-count until
audited. An empty 2026 bin would be censoring, not a flat frontier, and the
folder's verdict would have to say so.

### How much work to bring it current?

Bounded, because genuinely new best-known-complexity results are rare — a few
per year across all families, against the 2021 paper's finding that about half
of families never improve at all and the average family records 1.44
improvements since 1940. The matrix-multiplication ledger in this repository
shows the cadence at the fast end: four exponent records over 2022–2026 in one
of the most-watched families in the field. The path:

1. **Audit the export against known ledgers** — cross-check the fast-moving
   families against `problems/matrix-omega/` and against recent SODA/STOC/FOCS
   results. This also answers the 2026 question directly. About a day.
2. **One-time recency sweep** — check the families with post-2015 activity
   against the recent literature; the majority of families are static and need
   only a spot-check. A few days, front-loaded on the active families.
3. **Ongoing maintenance** — a small annual sweep thereafter, or contributions
   filed upstream to the wiki itself, which is the better home for corrections.

Two audits sit on the critical path before a problem folder: no licence is
stated anywhere findable, so a note to the FutureTech team is needed (and would
also establish their update cadence); and the export appears to be an
interactive builder rather than a stable URL, so the first ingest would be a
hand-vendored CSV with a retrieval date — the ✍️ maintenance status the
repository already supports — with a MediaWiki-API `fetch.py` as a possible
later upgrade if `api.php` proves to be enabled.

## Deferred algorithm benchmark reconstructions

These three sources have unusually good historical artifacts, but they do not
yet provide clean time series of algorithmic progress. Their official annual
results or release histories are not comparable measurements: the tasks,
machines, rules or software interfaces change over time. They therefore belong
in this appendix until controlled retrospective reruns have actually been
completed.

### MaxSAT Evaluation

The [MaxSAT Evaluation archive](https://maxsat-evaluations.github.io/) spans
annual solver generations from 2006 onward and often preserves solver source,
benchmarks and detailed results. The official scores cannot simply be joined
across years because benchmark composition, tracks, time limits, hardware and
ranking rules changed.

A defensible series would require substantial extra work:

- freeze one weighted and unweighted benchmark corpus;
- specify an ex-ante rule for selecting each year's solver snapshot;
- recover and containerize roughly twenty generations of historical solvers,
  including obsolete compilers and dependencies;
- run every snapshot under identical CPU, memory and timeout limits; and
- vendor per-instance logs before calculating solved count, PAR-2 or objective
  gap.

Until that work is done, edition count measures competition activity and annual
rankings mix algorithm progress with changing experimental conditions.

### MiniZinc Challenge

The [MiniZinc Challenge](https://www.minizinc.org/challenge/) has annual editions
from 2008 onward, with model, solver and result archives. Its official medal and
score histories are not a clean time series because the model set, data files,
MiniZinc and FlatZinc versions, solver interfaces, hardware, time limits and
scoring system all changed.

Reconstruction would require selecting a recurring set of optimization models
before examining outcomes, defining how each model is compiled for old solver
interfaces, rebuilding historical solvers in pinned environments, and running
them on common hardware. Compatibility translations would need to be audited so
they do not accidentally give newer or older solvers different problems. This
is a valuable project, but it is closer to experimental software archaeology
than to parsing an existing ledger.

### OR-Tools CP-SAT

[OR-Tools release notes](https://developers.google.com/optimization/support/release_notes)
and [tagged releases](https://github.com/google/or-tools/releases) provide a
dense chronology from CP-SAT's 2018 public launch. Release cadence and prose
claims about “performance improvements” are not performance observations,
however.

This is the easiest of the three reconstructions, but it still needs a frozen
constraint-optimization suite, adapters for old APIs and model formats, pinned
compiler and dependency environments, fixed hardware and worker counts, and
repeated seeds for nondeterministic parallel search. Only those reruns could
support a time series of runtime, solved count, proof rate or objective gap.
Without them, a version-by-date chart would measure packaging activity rather
than algorithmic progress.

## Cross-domain analyses

### 1. Build a discovery index rather than an output index

Convert perhaps 30–50 series into dated discovery events. Fit the pre-AI trend
separately for each series, estimate whether 2021–2026 observations lie above
that trend, and meta-analyse the deviations. This avoids the central ambiguity
of arXiv and Crossref counts: cheaper writing can increase output without
increasing discovery.

### 2. Test whether acceleration is proportional to AI exposure

Assign each domain an ex-ante AI-exposure measure. Protein structure, medicinal
chemistry and combinatorial optimization are computational and search-heavy;
telescope-limited astronomy, field taxonomy and some experimental physics are
less exposed. Estimate a `post-AI × AI-exposure` interaction and include the
low-exposure domains as controls. A common 2023 kink across both groups would
point to a secular data, investment or reporting effect rather than AI.

### 3. Use staggered AI shocks

“ChatGPT happened in 2022” is too crude. Candidate treatment dates include
modern deep learning around 2012, AlphaFold2 and AlphaFold DB in 2021,
generative protein design around 2022, broadly used LLMs in 2022–2023, GNoME in
2023, and increasingly capable scientific agents in 2025–2026. The Hill–Stein
design shows how to combine a discrete shock with cross-sectional exposure.

### 4. Extend the AlphaFold design with BindingDB

Split protein targets by whether they had an experimental PDB structure before
July 2021. For each target, measure time to first potent ligand and the frequency
and magnitude of affinity-record improvements. Test whether previously
structureless targets catch up after AlphaFold. BindingDB supplies publication
dates, while [AlphaFold DB](https://alphafold.ebi.ac.uk/) supplies prediction
coverage. This gets closer to “did AlphaFold increase drug-discovery output?”
than a paper count does.

### 5. Apply the same logic to enzyme discovery

For each newly characterized EC reaction, recover the underlying publication
date from BRENDA. Classify papers or labs as explicitly AI-assisted, or classify
enzyme families by how much sequence and structure information AI can exploit.
Then test whether the creation rate of genuinely new experimentally demonstrated
catalytic functions changes.

### 6. Separate new data from better inference on old data

For each exoplanet, distinguish the observation date from the announcement
date, then plot discoveries made from archival observations separately. AI that
improves inference or search should create findings from fixed existing data
without requiring a better telescope. The same design can be used for old code,
sequencing datasets, collider data and other archived evidence.

### 7. Measure frontier magnitude, not only event count

Use Starrydata to reconstruct quantities such as global experimental `ZT(t)` or
best battery capacity at a standardized cycle count. NREL already maintains this
kind of frontier for photovoltaic efficiency. AI may create many trivial events
without moving an important frontier—or one large frontier jump without many
events—so both count and magnitude should be retained.

### 8. Measure problem-opening-to-solution latency

Candidate queues include newly identified drug target → first potent ligand,
disease gene → validated mechanism, protein sequence → functional annotation,
exoplanet candidate → confirmation, and open mathematical question →
resolution. AI may appear more clearly as shorter queues than as increased gross
output.

### 9. Run scientist-level event studies with NIH and OpenAlex

[NIH ExPORTER](https://reporter.nih.gov/exporter/) provides bulk project data,
legacy records, publications and patents. Combine it with
[OpenAlex](https://docs.openalex.org/) authors, works, topics and citations.
Identify researchers' first explicit AI use, match them to non-adopters using
pre-adoption histories, and compare externally validated discoveries, patents,
topic distance and citations after adoption.

A 2026 Nature study of 41.3 million papers,
[“Artificial intelligence tools expand scientists' impact but contract science's focus”](https://www.nature.com/articles/s41586-025-09922-y),
already reports higher individual publication and citation output alongside a
narrower collective range of topics. The valuable extension is to replace
papers and citations with externally validated discovery outcomes.

### 10. Treat low-AI-exposure series as falsification tests

Gravitational-wave detections, detector-limited astronomy, some taxonomic
discoveries and experimental structure deposition dominated by microscope
throughput can serve as explicit controls. If these accelerate in the same way
and at the same time as BindingDB or computational optimization, the common
cause is unlikely to be AI exposure alone.

## Highest-value next investigations

The current priority order is:

1. **BindingDB target–ligand frontiers**
2. **BRENDA new enzyme functions**
3. **NREL and Starrydata materials frontiers**
4. **PDG precision histories**

Together they cover medicinal biology, basic biology, materials science and
fundamental physics with unusually objective notions of progress. They also
provide a useful mix of AI-exposed and lower-exposure domains for the
cross-domain event-study framework.
