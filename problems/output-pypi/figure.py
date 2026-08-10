#!/usr/bin/env python3
"""Draw output-pypi-projects.png from this folder's dated counter readings.

Run: python3 problems/output-pypi/figure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.chart import year_fraction  # noqa: E402
from lib.families import volume_series  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The last full year before the slope steepens, named here rather than written
# into the annotation so the comparison and the label it produces cannot drift
# apart when the readings are extended.
BASELINE_YEAR = 2023


def main() -> None:
    rows = read_csv(HERE / "pypi-projects-over-time.csv")
    first, last = rows[0], rows[-1]

    def january(year: int) -> int:
        """The first reading of a calendar year, which is the year's anchor.

        The captures are quarterly and never land exactly on 1 January, so a
        year's additions are measured between whichever early-January readings
        exist rather than between fixed dates.
        """
        return next(int(row["projects"]) for row in rows
                    if row["date"].startswith(f"{year}-01"))

    baseline = january(BASELINE_YEAR + 1) - january(BASELINE_YEAR)
    last_year = int(last["date"][:4])
    to_date = int(last["projects"]) - january(last_year)

    volume_series(
        HERE / "output-pypi-projects.png",
        xs=[year_fraction(row["date"]) for row in rows],
        ys=[int(row["projects"]) / 1000 for row in rows],
        title="Projects registered on PyPI",
        subtitle="The registry's own front-page counter; a stock of names, not working software",
        ylabel="Thousand projects registered (cumulative)",
        reading=f"{int(first['projects']):,} projects on {first['date']}, "
                f"{int(last['projects']):,} on {last['date']}.\n"
                f"{baseline:,} names added across {BASELINE_YEAR}; "
                f"{to_date:,} in {last_year} so far —\n"
                f"the slope steepens after {BASELINE_YEAR + 1}.",
        source_label="Wayback captures of pypi.org, vendored as "
                     "pypi-projects-over-time.csv",
        source_url="https://pypi.org/",
        built_by=__file__,
        markers=True,
    )


if __name__ == "__main__":
    main()
