# DOI records deposited with Crossref

**Domain:** outside the three domains
**Role:** contrast case: volume
**Metric:** formal publishing volume; DOI records deposited with Crossref per year, by created date
**Coverage:** 2010 to 2026, annual, the last year partial through 2026-08-10
**Data:** [`crossref-dois-by-year.csv`](crossref-dois-by-year.csv)
**Upstream:** <https://api.crossref.org/works>
**Verdict:** no acceleration — 2026 annualizes to roughly 13.3 million records against 12.80 million in 2025 and an 8.63 million/year mean over 2010–2025

![DOI records deposited with Crossref each year, 2010 to 2026, drawn as annual bars with 2026 outlined as a part year.](output-crossref-dois.png)

## Definition

Crossref registers DOIs for scholarly publishing: member publishers deposit
a metadata record for each item they register, and each record carries a
`created` date, the day it was registered. The REST API reports how many
records fall in any created-date range.

An event in this series is one DOI record, counted in the calendar year of
its `created` date. The count is by registration date, not by publication
date, so a backfile deposit of older work lands in the year it was
registered. The last row is the year in progress at fetch time,
year-to-date through 2026-08-10. The CSV holds the yearly totals the API
reports; the records behind them are not vendored. The dataset carries no
authorship field.

## Facts

- **span:** from 5.28 million records in 2010 to 12.80 million in 2025, up
  143%
- **falls:** six of the fifteen year-on-year changes over 2010–2025 are
  falls
- **2024 dip:** deposits fell to 11.31 million from 12.69 million in 2023,
  then rose to 12.80 million in 2025
- **2026 year-to-date:** 8,108,195 records through 2026-08-10, annualizing
  to roughly 13.3 million

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as cumulative DOI records to date:

![Cumulative DOI records to date.](cumulative-output-crossref.png)

## Method

[`fetch.py`](fetch.py) makes one Crossref REST API request per year from
2010, filtered to that year's created-date range and asking for `rows=0` so
the response is a count rather than the records themselves. The row for the
current year is marked year-to-date with the date it was fetched. The
requests are sequential with a sleep between them, which is what keeps a
rebuild polite.

[`figure.py`](figure.py) draws the series through
[`lib/families.py`](../../lib/families.py)'s shared volume shape: years on
the x-axis, the count on the y-axis, 2026 shaded, the part year outlined
rather than filled. The three volume folders draw through that one shape.
The series is drawn in slate rather than the blue used elsewhere for human
or uncredited finders because it has no authorship field.
[`check.py`](check.py) recomputes the fact lines from the CSV; the
annualization uses the shared day-count rule in
[`lib/prose.py`](../../lib/prose.py).

## Limitations

- **deposits are not publications.** The count is by `created` date;
  backfile deposits of old work land in whatever year they were registered,
  so a year-on-year fall is not readable as a fall in publishing.
- **no authorship field.** The CSV records years and counts only; whether a
  human or a model wrote the work behind a record is not recorded.
- **volume, not discovery.** The series counts artifacts registered; the
  domain folders count results, and the two need not move together.
- **membership is not held fixed.** A deposit exists because a publisher
  that registers DOIs registered one, so more work being published cannot
  be separated from more of publishing being registered with Crossref.
- **no denominator of effort.** Nothing here measures how many researchers
  were working, so output per unit of input cannot be separated from more
  input.
- **the 2026 annualization is this repository's arithmetic**, scaled from a
  part year on an even-rate assumption.

## AI attribution

The dataset carries no authorship field; no AI share can be computed from
it. [`crossref-dois-by-year.csv`](crossref-dois-by-year.csv) holds a year,
a count and a part-year note per row; no AI credit appears in it as of the
2026-08-10 fetch.

## Sources

- <https://api.crossref.org/works> — the REST API the yearly counts are
  read from; this page carries no bibliography citekeys, and the counts
  rest on the API alone.
- [output-arxiv](../output-arxiv/README.md) and
  [output-github-pushes](../output-github-pushes/README.md) — the other two
  volume series, drawn through the same shared shape; they count preprint
  submissions and git pushes where this folder counts DOI registrations of
  formal publications.
