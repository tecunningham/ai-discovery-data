# Inventory of the AlphaEvolve problem set

**Domain:** mathematics
**Metric:** per problem, whether it has a live numeric record and how many dated prior works the paper cites
**Coverage:** the 65 problems the paper numbers 6.1 to 6.65; cited works span 1852–2025; built 2026-07-26
**Data:** [`alphaevolve-inventory.csv`](alphaevolve-inventory.csv)
**Upstream:** <https://arxiv.org/abs/2511.02864> and <https://github.com/google-deepmind/alphaevolve_repository_of_problems>
**Verdict:** baseline

![Composition of the AlphaEvolve problem set, and how many problems survive each filter a historical comparison requires.](alphaevolve-frame-funnel.png)

## The problem

The AlphaEvolve mathematics paper reports improved bounds on a share of 67
problems, and the discussion of that result has no historical baseline. Nobody
had assembled the dated record of prior improvements on those same problems, so
the AI-era step could not be set against the distribution of historical steps on
the same quantity. The paper's authors decline the survey explicitly, which is
why it is missing: "For reasons of space, we do not attempt to exhaustively
survey the history of each of the problems listed here, and refer the reader to
the references provided for each problem for a more in-depth discussion of known
results."

This folder is not a discovery series. It is the frame the record series are
drawn from: an inventory saying, per problem, what the quantity is, which prior
work the paper cites, what year each cited work dates from, and how the
companion repository classifies the outcome. It answers the prior question —
which of these problems even has a record history to compare against — so that
the sample can be drawn from a stated frame rather than from whichever problems
turned out to be convenient.

A prior-art search found nobody had done this. The nearest miss is HorizonMath,
a benchmark of over 100 unsolved problems with automated verification, which
compares AI output to best-known published results and carries no historical
dimension at all [@arxiv2026horizonmath]. Dated record tables exist per problem —
Packomania and Erich Friedman's packing pages, Radziszowski's small Ramsey
numbers survey, the standard tabulation of the matrix-multiplication exponent —
and no one has joined them to the AI results.

## What the chart shows

Two bar panels. On the left, the repository's own classification of the 65
numbered problems under the assumed index mapping: 19 where AlphaEvolve holds
the record, 11 where it matched a known optimum, 8 where it came in below the
record, 4 where its result has since been surpassed, and 23 unclassified. The 31
in the first, third and fourth groups are the ones with a live numeric record;
the matched-optimal group's history has terminated at a proven optimum, and the
unclassified group is mostly conjectures and non-record tasks.

On the right, the same set after each filter a historical comparison needs: 65
numbered in the paper, 31 with a live numeric record, 12 drawn as the
pre-committed sample, 6 that yielded a dated scalar record sequence at all, and
2 carrying both AI and human steps. That last number is the finding. Of a set
reported as 67 mathematical results, two quantities supported a head-to-head at
the point this inventory was built.

The dating turned out better than expected in one respect. Of the 65 problems,
64 cite at least one dated reference, 52 cite at least two, and 31 cite at least
four; the parsed bibliography yields 302 entries of which 298 carry a year.
Among problems citing two or more dated works the median span between earliest
and latest cited year is 42 years, so these are decades-deep literatures rather
than fresh ones.

## How the chart was built

[`figure.py`](figure.py) counts the `status` column of
`alphaevolve-inventory.csv` for the left panel and reads the first two funnel
rows off the same counts; the last three funnel rows are the sample size, the
number of sampled problems that yielded a sequence, and the number of quantities
with steps of both kinds, which come from
[the record sequences](../math-alphaevolve-records/README.md) and are written
into the figure rather than computed here.

The CSV is built by [`fetch.py`](fetch.py), which reads a local `pdftotext`
extraction of the paper plus a checkout of the companion repository. It locates
each problem's definition inside the paper's problem section, then records the
title, the topic group, the bracketed references cited within that span, the
publication year of each of those references from the parsed bibliography, any
inline bound string, and the repository's status classification. Neither input
is vendored here and the paper's text is not redistributed; only derived counts
and short quoted bound strings go into the CSV.

`n_citations` is the full number of parsed references. To keep the orientation
inventory compact, `cited_refs` lists at most the first twelve reference IDs;
three rows have thirteen or fourteen parsed references.

Two extraction bugs were found during construction and are worth recording,
because both would have corrupted the output silently. A cross-reference to a
problem occurring before its definition made the preceding problem's span
swallow its content, and the topic-group headings were only partly matched, so
group labels drifted forward. Both were caught by checking two problems whose
histories are known independently: the Sidon autoconvolution problem returns
2010 and 2017, matching the Matolcsi–Vinuesa and Cloninger–Steinerberger
attributions its own notebook gives, and the classic moving sofa returns 1992
and 2024, matching Gerver and Baek. That is the check to repeat if the script
changes.

## What it cannot support

- **A cited year is not a record year.** It is the year of a cited work:
  background references, surveys and method papers are mixed in with the papers
  that moved the bound. Separating them means reading the cited papers, which is
  the manual step this inventory scopes rather than performs. Nothing in the CSV
  should be read as a record sequence.
- **The index mapping is an assumption.** The paper numbers problems 6.1 to
  6.65 while the repository's `status.json` indexes 1 to 67, so the two
  enumerations cannot be identical. The identity mapping is assumed and every
  row carries `status_mapping` = `assumed` to say so.
- **The 65 are not 65 distinct problems.** At least twelve of the repository's
  67 experiment directories are the same problem under two names, so the set is
  closer to 50 distinct problems.
- **The status classification is the vendor's.** What counts as holding the
  record, matching an optimum or falling below one is the repository's own
  judgment, not an independent adjudication.
- **Bound strings are pattern-extracted** from lightly normalised LaTeX and are
  for orientation only; they must be re-read against the paper before use.
- **The frame does not fix the selection problem, only state it.** Tractability
  correlates with being well-curated and therefore with progress rate, so a
  sample drawn from this frame is still a sample of problems an AI system was
  pointed at.
- **On the packing problems the historical baseline is itself machine search.**
  Record improvements there have been machine-generated since the 1990s and many
  are unpublished, with Packomania reporting improvements arriving daily. An
  AI-versus-history comparison on those problems is automated against automated,
  so whether each prior record was human-proved or machine-found has to be coded
  per problem or the headline comparison means nothing.

## LLM contributions

None to this inventory, which is a frame rather than a result. The set it
inventories is the output of an evolutionary coding agent that mutates programs
under an automated evaluator [@novikov2025alphaevolve], published with a
companion repository carrying the status classification used here
[@deepmind2025problems].

What the inventory contributes to reading that output is the denominator. A
paper reporting improvements across 67 problems invites a count of results; the
frame says that 31 of them had a live numeric record to improve, and that only a
handful of those could be reduced to a dated sequence in which an AI step and a
human step sit on the same axis. Tao's assessment of the same run points the
same way: rediscovery of known solutions was the modal outcome across the
problem set and improvement the exception [@tao2025exploration].

## Related literature

The paper and its companion repository are the two inputs
[@novikov2025alphaevolve; @deepmind2025problems], and Tao's account of the run
is the standing external assessment of what it did and did not reach
[@tao2025exploration]. That a benchmark can compare AI output to the current
record while carrying no historical dimension — the gap this inventory exists to
close — is visible in the design of HorizonMath [@arxiv2026horizonmath]. The
line of work began with FunSearch's cap-set improvement in December 2023
[@deepmind2023funsearch]. That records in any field arrive in bursts with long
gaps, so a cluster is not by itself a signature, is Sherry and Thompson's
finding [@sherry2021fast]. The series drawn from this frame are
[the record sequences](../math-alphaevolve-records/README.md),
[sums and autoconvolution](../math-sums-autoconvolution/README.md).
