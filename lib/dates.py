"""The committed snapshot date and the date arithmetic shared across the repo.

These are matplotlib-free on purpose. The fetchers drop rows newer than the
snapshot date, tools/check.py enforces it against every CSV, and several folder
checks recompute date arithmetic — none of which should need a plotting library
installed. lib/chart.py re-exports everything here so figure code keeps one
import surface.
"""

from __future__ import annotations

import re
from datetime import date

# A committed snapshot date keeps PNG bytes stable. tools/check.py rejects data
# newer than this date, so a refetch cannot silently leave standing-record lines
# ending before their newest observation.
AS_OF_DATE = date(2026, 8, 20)
NOW = AS_OF_DATE.year + (AS_OF_DATE.timetuple().tm_yday - 1) / 365.25


def year_fraction(value: str) -> float:
    parts = [int(part) for part in value.split("-")]
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return parts[0] + (parts[1] - 0.5) / 12
    day = date(*parts[:3])
    return day.year + (day.timetuple().tm_yday - 1) / 365.25


def period_bounds(label: str) -> tuple[float, float]:
    """Start and end of a period label as year fractions.

    Accepts the three period vocabularies the vendored CSVs use: a year
    ("2000"), a quarter ("2020-Q1"), or a month ("1991-07"). Shared by the
    cumulative shapes (whose steps land at period ends) and the periodic bar
    charts (whose bars span the period).
    """
    if re.fullmatch(r"\d{4}", label):
        year = int(label)
        return year, year + 1
    quarter = re.fullmatch(r"(\d{4})-Q([1-4])", label)
    if quarter:
        year, q = int(quarter.group(1)), int(quarter.group(2))
        return year + (q - 1) / 4, year + q / 4
    month = re.fullmatch(r"(\d{4})-(\d{2})", label)
    if month:
        year, m = int(month.group(1)), int(month.group(2))
        return year + (m - 1) / 12, year + m / 12
    raise ValueError(f"unrecognized period label: {label!r}")
