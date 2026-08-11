"""Recomputing the numbers a document prints.

Every folder document states figures in prose — a total, a share, a growth rate
— and prose does not move when a CSV does. A refetch that changes a series
leaves those sentences behind, stating last month's numbers in the present
tense, and nothing about the file looks wrong.

A folder ``check.py`` closes that gap by recomputing each claim from the CSV
beside it and asserting the resulting string appears in the document. The test
is deliberately textual: it fails when the document says something the data no
longer supports, which is the failure that matters, and it makes the document
rather than the checker the place the number lives.

Two consequences are worth knowing before writing one. Claims must be phrased
so the recomputed form is what a person would naturally write — "49,838
through 2026-08-10", not a rounded restatement — because the check is only as
useful as the sentences it can express. And a claim that cannot be recomputed
from the vendored data does not belong here; those are the ones the documents
mark as this repository's arithmetic over an external source.
"""

from __future__ import annotations

import re
from pathlib import Path


def prose(folder: Path) -> str:
    """The folder's document as one whitespace-collapsed line.

    Collapsing means a claim spanning a line break still matches, so a document
    can be rewrapped without breaking its own checks.
    """
    text = (Path(folder) / "README.md").read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", text)


def missing(text: str, claims: dict[str, str]) -> list[str]:
    """Claims whose recomputed phrasing is absent from the document.

    ``claims`` maps the exact phrase the document should contain to a short
    label naming what it is, which is what the failure line reports.
    """
    return [
        f"README lacks recomputed {label}: {phrase!r}"
        for phrase, label in claims.items()
        if phrase not in text
    ]


def report(failures: list[str]) -> int:
    """Print failures and return the exit status a folder check should use."""
    for failure in failures:
        print(failure)
    return bool(failures)


def annualized(count: int, through: str) -> float:
    """Scale a part-year count to a full year by elapsed days.

    Several folders annualize a partial year the same way, and doing it in one
    place keeps the day count from drifting between them.
    """
    from datetime import date

    day_of_year = date.fromisoformat(through).timetuple().tm_yday
    return count * 365 / day_of_year
