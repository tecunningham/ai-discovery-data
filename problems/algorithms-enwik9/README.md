# Hutter Prize compression: enwik9

**Domain:** algorithms
**Role:** discovery series
**Metric:** total size in bytes of decompressor plus archive for a fixed 1 GB
text corpus, under a CPU-time and memory cap, per awarded record
**Coverage:** 2019 baseline to 2026; the prize moved to enwik9 on 2020-02-21;
prize site read 2026-07-28, benchmark page's own update dated 2026-07-08
**Data:** [`enwik9-records.csv`](enwik9-records.csv), holding both the
`hutter_enwik9` and `ltcb_enwik9` series
**Upstream:** <http://prize.hutter1.net/> and
<http://mattmahoney.net/dc/text.html>
**Verdict:** no acceleration — 0 awarded records in 2026 (one pending claim
of 2026-06-26) against 2 in 2024 and 4 over 2021–2024; the uncapped
comparator is unchanged since 2023-10-23

![Hutter Prize enwik9 records with a pending entry open and the uncapped leaderboard dashed.](discovery-algorithms-enwik9.png)

## Definition

The task is to compress the first 10^9 bytes of a fixed XML dump of English
Wikipedia, scored on the compressed size including the size of the
decompression program. The corpus was frozen in 2006, so the task has no
benchmark drift by construction, and counting the decompressor closes the
loophole of hiding the model in the program.

The prize caps resources:

> "must run in ≲50 hours using a single CPU core and <10GB RAM and <100GB
> HDD on our test machine"
> — Hutter Prize rules, prize.hutter1.net, read 2026 [@hutter2026prize]

The cap excludes GPUs, so two series are plotted rather than one: the prize
is the constrained series, and Matt Mahoney's Large Text Compression
Benchmark is the same corpus with no cap, admitting GPU and TPU compressors
[@mahoney2026ltcb].

A "discovery" is an awarded record, dated by the award. The prize pays only
for improvements of at least 1% over the standing record, so the ledger
records steps that cleared a hurdle, not every improvement made.

## Facts

- **baseline:** 116,673,681 bytes at the 2019 phda9v1.8 baseline
- **awards:** starlit by Artemiy Margaritov on 2021-05-31 · fast cmix by
  Saurabh Kumar on 2023-07-16 · fx-cmix by Kaido Orav on 2024-02-02 ·
  fx2-cmix by Kaido Orav and Byron Knoll on 2024-09-03 at 110,793,128 bytes
- **steps:** measured against the record each displaced, those steps are
  1.13%, 1.04%, 1.38% and 1.59%; together the four awards take the total
  down 5.0% from the 2019 baseline
- **pending:** cmix-lex by Ibrahim Marcouch, announced on the benchmark page
  on 2026-06-26 at 109,190,109 bytes, a further 1.45% and inside the
  109,685,196 needed to clear the 1% hurdle; not an awarded record on the
  prize site as of 2026-07-28
- **uncapped:** nncp v3.2 reached 107,261,318 bytes on 2023-10-23 and is
  still ranked 1 as of the benchmark page's 2026-07-08 update, with active
  submissions below it through 2024 to 2026

The retired 100 MB enwik8 prize is a different corpus and is not joined to
the curve. Its complete five-row chronology:

| Date | Program | Total bytes | Status |
|---|---|---:|---|
| 2006-03-24 | paq8f -7 | 18,324,887 | pre-prize baseline |
| 2006-09-25 | paq8hp5 -7 | 17,073,018 | first award |
| 2007-05-14 | paq8hp12 -7 | 16,481,655 | second award |
| 2009-05-23 | decomp8 | 15,949,688 | third award |
| 2017-11-04 | phda9 | 15,284,944 | fourth award |

Alexander Rhatushnyak set all four enwik8 awards; the gap before the last
runs eight and a half years. The prize moved to enwik9 in February 2020.

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as the standing record's value over time:

![Standing record for total size in MB over time.](cumulative-algorithms-enwik9.png)

## Method

The rows are transcribed by hand from the two upstream pages, so there is no
fetcher that rebuilds them. [`fetch.py`](fetch.py) is a staleness probe
instead: it reads the prize page and reports if the standing awarded record
has been displaced, leaving the CSV and this document to be updated by hand.
[`check.py`](check.py) recomputes the fact lines above from the CSV.

[`figure.py`](figure.py) calls the shared `compression_chart()` in
[`../../lib/families.py`](../../lib/families.py), which reads
`enwik9-records.csv`, keeps the rows whose `series` column matches, and plots
`total_bytes` divided by 10^6 against the year fraction of `date` as a step
function. Rows whose `award` column is anything other than `pending` are
drawn filled and joined by the solid line, which therefore includes the
unawarded 2019 baseline; the pending row is drawn as an open marker labelled
from its `program` column, "cmix-lex, pending". When the series is
`hutter_enwik9`, the function additionally selects the `ltcb_enwik9` rows and
draws them in grey dashes, with a corner note reporting the uncapped frontier
as flat since October 2023 at 107.3 MB. The axis is linear and in megabytes;
January 2026 onward is shaded, as in every figure here.

## Limitations

- **a hurdle censors the small steps.** The prize pays only above 1%, so
  improvements below that threshold are invisible here whether or not they
  happened, and the observed 1.0–1.6% cadence is partly an artefact of the
  rule.
- **neural is not AI-authored.** The uncapped leader nncp uses a transformer
  architecture and cmix has carried an LSTM since 2016, but a hand-written
  neural compressor is not a model-written one.
- **the two pages do not agree on every byte count.** fx2-cmix is
  110,793,128 on the prize site and 110,351,665 on the benchmark, because
  the archives and measurement conventions differ, and the benchmark's nncp
  v2 row prints a total equal to its archive-only size, apparently omitting
  a 99,671-byte decompressor.
- **the rows were transcribed by hand from prose pages.** Neither upstream
  is a feed; both are HTML tables read and typed into the CSV, and the prize
  site was read over plain HTTP because its TLS certificate has expired.
- **the capped and uncapped series are not comparable in level.** They are
  different rules on the same corpus, which is why they share an axis but
  not a line style.
- **a flat frontier is not a measured absence of effort.** Submissions
  continued below the uncapped leader, but nothing in the data counts how
  much search went into them.

## AI attribution

No record on either the capped or the uncapped series credits a language
model or an agent, as of the prize-site read of 2026-07-28 and the benchmark
page's update of 2026-07-08. The nearby AI-credited results in this domain
are not compression records: the 23% GPU kernel speedup reported in the
AlphaEvolve paper [@novikov2025alphaevolve], and GPU kernels found by
test-time training that beat the best human submissions by 15 to 51%
[@yuksekgonul2026learning].

## Sources

- [@hutter2026prize] — the prize site: the record table, the resource cap
  quoted above, and the 1% improvement hurdle.
- [@mahoney2026ltcb] — the Large Text Compression Benchmark: the uncapped
  rows, the pending cmix-lex announcement, and the enwik8 chronology.
- [@novikov2025alphaevolve] — the AlphaEvolve kernel speedup cited in the
  AI-attribution register.
- [@yuksekgonul2026learning] — the test-time-training kernel result cited in
  the AI-attribution register.
- [@sherry2021fast] — the published base rate: about half of algorithm
  families show little or no improvement over decades, with improvements
  arriving at roughly 1.44 per family since 1940.
