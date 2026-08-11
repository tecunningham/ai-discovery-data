"""Deciding whether a vulnerability credit names an AI system.

Every finder-attributed cyber series matches its credit strings against the same
marker list. The list lives here rather than in the problem folders, because a
marker added in one folder and not the others would make the codebases quietly
incomparable.

The classification is by explicit textual marker, so every count it produces is
a floor: a researcher who used a model without saying so is counted as human.
Fuzzers are kept apart from AI deliberately — a fuzzer is automated but is not a
model, and folding them together would credit a decade of fuzzing to LLMs.

The bare name "Claude" is ambiguous before the model era, so that one marker is
accepted only from 2024 onward. Callers pass the disclosure year to enforce that
guard even though no currently vendored pre-2024 credit is affected.
"""

from __future__ import annotations

import re

# Shared across curl FINDER credits, Mozilla reporter strings, and OpenSSL's
# "Found by" credits. "Aisle" is included as a word, not only the full company
# name, because upstream sometimes omits "Research".
AI_CREDIT = re.compile(
    r"\banthropic\b|\bopenai\b|\bgpt\b|big sleep|mythos|\bgemini\b"
    r"|antaisecuritylab|aisle research|autonomous code security|xbow|zeropath"
    r"|\baisle\b|\bLLM\b|\bagent\b|using AI\b",
    re.I,
)
CLAUDE = re.compile(r"\bclaude\b", re.I)

# Compatibility aliases for code and notebooks that imported the old names.
CURL_AI = FIREFOX_AI = ADVISORY_AI = AI_CREDIT

FUZZ = re.compile(r"fuzz", re.I)

SEVERITIES = ["Low", "Medium", "High", "Critical"]


def classify(finder: str, year: int | None = None) -> str:
    """Return "ai", "fuzz" or "other" for one finder credit."""
    finder = finder or ""
    if AI_CREDIT.search(finder) or (
        CLAUDE.search(finder) and (year is None or year >= 2024)
    ):
        return "ai"
    if FUZZ.search(finder):
        return "fuzz"
    return "other"
