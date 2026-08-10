#!/usr/bin/env python3
"""Draw output-crossref-dois.png from this folder's annual deposit counts.

Run: python3 problems/output-crossref/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402


def main() -> None:
    rows = read_csv(HERE / "crossref-dois-by-year.csv")
    counts = {int(row["year"]): int(row["dois_created"]) for row in rows}
    # A row carrying a note is the year still in progress at fetch time, so
    # every comparison below is between complete years.
    complete = [int(row["year"]) for row in rows if not row["note"]]
    first, last = complete[0], complete[-1]
    growth = counts[last] / counts[first] - 1
    falls = [year for year in complete[1:] if counts[year] < counts[year - 1]]

    volume_series(
        HERE / "output-crossref-dois.png",
        xs=[float(row["year"]) for row in rows],
        ys=[int(row["dois_created"]) / 1e6 for row in rows],
        title="DOI records deposited with Crossref",
        subtitle="Registration of formal publications; the control on the other volume series",
        ylabel="Million DOI records that year",
        reading=f"{counts[first] / 1e6:.2f}M records in {first}, "
                f"{counts[last] / 1e6:.2f}M in {last} — up {growth:.0%} over\n"
                f"{last - first} years, falling in {len(falls)} of them, most "
                f"recently {falls[-1]}.\n"
                f"No clean bend: the rise long predates the shaded period.",
        source_label="Crossref REST API by created date, vendored as "
                     "crossref-dois-by-year.csv",
        source_url="https://api.crossref.org/works",
        built_by=__file__,
        bars=True,
        partial_last="part year",
    )


if __name__ == "__main__":
    main()
