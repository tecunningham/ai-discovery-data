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

| Area | Dataset and proposed metric | Why it is interesting | Rating |
|---|---|---|---|
| Drug discovery | [BindingDB](https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp?all_download=yes): first potent ligand for each protein target, then successive affinity records | The download contains millions of measured protein–ligand affinities and now provides publication and curation dates for each measurement. Define discovery as the first ligand below 1 µM, 100 nM or 10 nM for a target, or a new record-best affinity. | **A+** |
| Enzymology | [ENZYME](https://enzyme.expasy.org/) and [BRENDA](https://www.brenda-enzymes.org/): first characterization of each distinct EC enzyme activity | ENZYME supplies the classification ledger; BRENDA connects enzyme classes and functional data to dated primary literature. A newly demonstrated catalytic activity is close to a stable unit of new biological function. | **A+** |
| Solar and materials | [NREL Best Research-Cell Efficiency Chart](https://www.nrel.gov/pv/interactive-cell-efficiency.html): independently confirmed efficiency records | This is a decades-long physical performance frontier across photovoltaic technologies, rather than a paper or submission count. | **A+** |
| Materials | [Starrydata](https://docs.starrydata.org/datasets/) property frontiers: thermoelectric ZT, standardized battery capacity or retention, magnetic properties and related quantities | The open dataset links experimental curves to papers and covers thermoelectric, battery, magnetic, dielectric and other materials. It can support many reconstructed historical frontiers. | **A+** |
| Superconductivity | NIMS SuperCon: newly discovered superconductors and the record critical-temperature frontier | The underlying experimental database includes transition temperatures and citations for more than ten thousand superconducting materials. The main audit question is whether first-report dates can be recovered consistently. | **A** |
| Structural biology | [Protein Data Bank](https://www.rcsb.org/): first experimental structure for a UniProt protein or Pfam family | Deposition and release dates are clean. Deduplicating raw structure output into the first structure for a protein or family turns throughput into a discovery event. | **A** |
| Genetics | [GWAS Catalog](https://www.ebi.ac.uk/gwas/docs/programmatic-access): first significant independent locus–trait association | The catalog provides curated associations, downloads and an API. Historical releases or publication dates could reconstruct the arrival of the first independent loci per trait. | **A−** |
| Medical genetics | [ClinVar archives](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/): first high-confidence pathogenic variant–disease classification | Retained monthly releases make it possible to reconstruct new expert-reviewed classifications and later state transitions rather than counting all submissions. | **A−** |
| Particle physics | [Particle Data Group historical editions](https://pdg.lbl.gov/rpp-archive/): precision frontiers for masses, lifetimes, couplings and other parameters | Aggregate the fall in uncertainty across hundreds of stable parameters. The editions reach back to 1957; recent editions also have a machine-readable API. | **A−** |
| Astronomy | [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html): confirmed exoplanets, especially discoveries extracted from old observations | Discovery year, method, publication date, facility and instrument are available programmatically. The especially useful series is planets found by reanalysing archival Kepler, TESS or other observations. | **A−** |
| Chemistry | [Open Reaction Database](https://github.com/open-reaction-database/ord-data) and USPTO reaction data: novel transformation or condition frontiers | ORD preserves structured conditions, outcomes, provenance and repository history. Possible units include first transformations between reaction classes or yield improvements under comparable substrate constraints, but the matching rule needs more thought. | **B+** |
| Cryo-EM | [EMDB releases](https://www.ebi.ac.uk/emdb/statistics_main.html), preferably first structure for a biological target | The source has an exceptionally clean annual release series—640 in 2015, 3,820 in 2020 and 11,657 in 2025. Much of the rise reflects microscopes and methods rather than AI, making it a useful comparison or control after deduplication. | **B+** |
| Gravitational-wave astronomy | [GWOSC](https://gwosc.org/eventapi/) catalog events per observing day | The events are clean and machine-readable, but discovery is strongly detector-sensitivity constrained. That makes this more valuable as a negative or low-AI-exposure control than as a direct AI series. | **B, as control** |

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
