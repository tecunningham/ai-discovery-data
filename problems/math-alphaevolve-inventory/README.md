# Inventory of the AlphaEvolve problem set

**Domain:** mathematics
**Role:** denominator frame
**Metric:** per problem, whether it has a live numeric record and how many dated prior works the paper cites
**Coverage:** the 65 problems the paper numbers 6.1 to 6.65; cited works span 1852–2025; built 2026-07-26
**Data:** [`alphaevolve-inventory.csv`](alphaevolve-inventory.csv)
**Upstream:** <https://arxiv.org/abs/2511.02864> and <https://github.com/google-deepmind/alphaevolve_repository_of_problems>
**Verdict:** baseline — 65 problems inventoried, 31 with a live numeric record; built 2026-07-26

![Composition of the AlphaEvolve problem set, and how many problems survive each filter a historical comparison requires.](alphaevolve-frame-funnel.png)

## Definition

The AlphaEvolve mathematics paper reports improved bounds across a set of 67
mathematical problems; its problem section numbers them 6.1 to 6.65
[@georgiev2025mathexploration]. This folder is an inventory over those 65
numbered problems, not a discovery series: per problem it records what the
quantity is, which prior work the paper cites, what year each cited work
dates from, and how the companion repository classifies the outcome. The
record series drawn from this frame are
[the record sequences](../math-alphaevolve-records/README.md).

The paper states its own scope on problem history:

> "For reasons of space, we do not attempt to exhaustively survey the
> history of each of the problems listed here, and refer the reader to the
> references provided for each problem for a more in-depth discussion of
> known results."
> — Georgiev, Gómez-Serrano, Tao and Wagner, arXiv 2511.02864, 2025 [@georgiev2025mathexploration]

An entry in this inventory is one numbered problem. A problem counts as
having a live numeric record when the repository's classification places it
in the `world_record`, `worse_than_record` or `former_record` groups: the
matched-optimal group's history has terminated at a proven optimum, and the
unclassified group is mostly conjectures and non-record tasks.

## Facts

- **status composition:** 19 where AlphaEvolve holds the record, 11 where it
  matched a known optimum, 8 where it came in below the record, 4 where its
  result has since been surpassed, and 23 unclassified
- **live records:** 31 of the 65 problems have a live numeric record (the
  first, third and fourth groups above)
- **funnel:** 65 numbered in the paper · 31 with a live numeric record · 12
  drawn as the pre-committed sample · 6 that yielded a dated scalar record
  sequence · 2 carrying both AI and human steps
- **citation depth:** of the 65 problems, 64 cite at least one dated
  reference, 52 cite at least two, and 31 cite at least four
- **cited-year spans:** among problems citing two or more dated works the
  median span between earliest and latest cited year is 42 years

This folder has no cumulative view on the collection-wide
[cumulative index](../../CUMULATIVE.md): the inventory is a one-date
snapshot of a problem set, not a time series. The dated record sequences it
feeds are [the records folder's](../math-alphaevolve-records/README.md),
which has one.

## Method

The CSV is built by [`fetch.py`](fetch.py), which reads a local `pdftotext`
extraction of the paper plus a checkout of the companion repository. It
locates each problem's definition inside the paper's problem section, then
records the title, the topic group, the bracketed references cited within
that span, the publication year of each of those references from the parsed
bibliography, any inline bound string, and the repository's status
classification. Neither input is vendored here and the paper's text is not
redistributed; only derived counts and short quoted bound strings go into
the CSV. The parsed bibliography yields 302 entries, of which 298 carry a
year.

`n_citations` is the full number of parsed references. To keep the
inventory compact, `cited_refs` lists at most the first twelve reference
IDs; three rows have thirteen or fourteen parsed references.

Two extraction bugs were found and fixed during construction, and both would
have corrupted the output silently: a cross-reference to a problem occurring
before its definition made the preceding problem's span swallow its content,
and the topic-group headings were only partly matched, so group labels
drifted forward. Two rows with independently known histories anchor the
extraction: the Sidon autoconvolution problem (6.2) returns 2010 and 2017,
matching the Matolcsi–Vinuesa and Cloninger–Steinerberger attributions its
own notebook gives, and the classic moving sofa (6.62) returns 1992 and
2024, matching Gerver and Baek. [`check.py`](check.py) re-asserts both
anchors along with the fact lines above.

[`figure.py`](figure.py) counts the `status` column of
`alphaevolve-inventory.csv` for the left panel and reads the first two
funnel rows off the same counts; the last three funnel rows — the sample
size, the number of sampled problems that yielded a sequence, and the number
of quantities with steps of both kinds — come from
[the record sequences](../math-alphaevolve-records/README.md) and are
written into the figure rather than computed here.

## Limitations

- **a cited year is not a record year.** It is the year of a cited work:
  background references, surveys and method papers are mixed in with the
  papers that moved the bound. Separating them requires reading the cited
  papers, a manual step this inventory scopes rather than performs; the CSV
  is not a record sequence.
- **the index mapping is an assumption.** The paper numbers problems 6.1 to
  6.65 while the repository's `status.json` indexes 1 to 67, so the two
  enumerations cannot be identical. The identity mapping is assumed and
  every row carries `status_mapping` = `assumed` to say so.
- **the 65 are not 65 distinct problems.** At least twelve of the
  repository's 67 experiment directories are the same problem under two
  names, so the set is closer to 50 distinct problems.
- **the status classification is the vendor's.** What counts as holding the
  record, matching an optimum or falling below one is the repository's own
  judgment, not an independent adjudication.
- **bound strings are pattern-extracted** from lightly normalised LaTeX and
  are recorded for orientation only.
- **the frame states the selection problem rather than fixing it.**
  Tractability correlates with being well-curated and therefore with
  progress rate, so a sample drawn from this frame is still a sample of
  problems an AI system was pointed at.
- **on the packing problems the historical baseline is itself machine
  search.** Record improvements there have been machine-generated since the
  1990s and many are unpublished, with Packomania reporting improvements
  arriving daily; an AI-versus-history comparison on those problems is
  automated against automated unless each prior record's finder type is
  coded per problem.

## AI attribution

No AI system contributed to this inventory, which is a frame rather than a
result, and no row of `alphaevolve-inventory.csv` scores an AI event. The
set it inventories is the output of an evolutionary coding agent that
mutates programs under an automated evaluator [@novikov2025alphaevolve],
published with a companion repository carrying the status classification
used here [@deepmind2025problems]. The AI and human steps on these problems
are scored in [the record sequences](../math-alphaevolve-records/README.md).

## Sources

- [@georgiev2025mathexploration] — the mathematics paper the problem
  definitions, citations and bound strings are extracted from; quoted above
  on its own scope.
- [@novikov2025alphaevolve] — the AlphaEvolve system paper.
- [@deepmind2025problems] — the companion repository whose `status.json`
  supplies the status classification.
- [@tao2025exploration] — co-author's account of the run across the problem
  set.
- [@arxiv2026horizonmath] — HorizonMath, a benchmark of over 100 unsolved
  problems with automated verification that compares AI output to best-known
  published results and carries no historical dimension.
- [@deepmind2023funsearch] — FunSearch's cap-set improvement of December
  2023, the dated precedent for this line of work.
- [@sherry2021fast] — measured heterogeneity of improvement rates across
  algorithm families; records arrive in bursts with long gaps.
- Series drawn from this frame:
  [the record sequences](../math-alphaevolve-records/README.md) and
  [sums and autoconvolution](../math-sums-autoconvolution/README.md).
