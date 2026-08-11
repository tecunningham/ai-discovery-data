"""Signals present in vulnerability finder credits.

Every finder-attributed cyber series matches its credit strings against the same
marker list. The list lives here rather than in the problem folders, because a
marker added in one folder and not the others would make the codebases quietly
incomparable.

The coarse ``classify`` result is a textual-credit category, not proof of a
discovery method. In particular, an employer such as Anthropic or Aisle Research
is an affiliation; it does not establish that AI was used for a particular
finding. Callers that make causal claims must keep affiliation separate and add
finding-level provenance from another source.

AI and fuzz markers are independent signals. ``classify`` retains its historical
single-category return value for existing charts, but new datasets should store
both booleans so an AI-guided fuzzing finding is not arbitrarily swallowed by
the first matching branch.

The bare name "Claude" is ambiguous before the model era, so that one marker is
accepted only from 2024 onward. Callers pass the disclosure year to enforce that
guard even though no currently vendored pre-2024 credit is affected.
"""

from __future__ import annotations

import re

# Shared across curl FINDER credits, Mozilla reporter strings, and OpenSSL
# reporter credits. These names indicate affiliation only.
AI_AFFILIATION = re.compile(
    r"\banthropic\b|\bopenai\b|antaisecuritylab|aisle research|\baisle\b"
    r"|xbow|zeropath",
    re.I,
)

# These words name a system or method, although callers should still inspect the
# surrounding credit before treating it as finding-level provenance.
EXPLICIT_AI_METHOD = re.compile(
    r"\bgpt\b|big sleep|mythos|\bgemini\b|autonomous code security"
    r"|\bLLM\b|\bagent\b|using AI\b",
    re.I,
)
CLAUDE = re.compile(r"\bclaude\b", re.I)

# Compatibility matcher for code and notebooks that need the old broad signal.
AI_CREDIT = re.compile(
    rf"{AI_AFFILIATION.pattern}|{EXPLICIT_AI_METHOD.pattern}|\bclaude\b",
    re.I,
)

# Compatibility aliases for code and notebooks that imported the old names.
CURL_AI = FIREFOX_AI = ADVISORY_AI = AI_CREDIT

FUZZ = re.compile(r"fuzz", re.I)

SEVERITIES = ["Low", "Medium", "High", "Critical"]


def has_ai_affiliation(finder: str) -> bool:
    """Whether a credit names an AI lab or security company."""
    return bool(AI_AFFILIATION.search(finder or ""))


def names_ai_method(finder: str, year: int | None = None) -> bool:
    """Whether a credit explicitly names an AI system or method."""
    finder = finder or ""
    return bool(
        EXPLICIT_AI_METHOD.search(finder)
        or (CLAUDE.search(finder) and (year is None or year >= 2024))
    )


def is_fuzz_credit(finder: str) -> bool:
    """Whether a credit explicitly names fuzzing."""
    return bool(FUZZ.search(finder or ""))


def classify(finder: str, year: int | None = None) -> str:
    """Return the legacy single textual-credit category.

    This compatibility API gives AI markers priority over fuzz markers. It does
    not establish that AI caused a finding; new provenance-aware datasets should
    call the independent signal helpers above.
    """
    finder = finder or ""
    if has_ai_affiliation(finder) or names_ai_method(finder, year):
        return "ai"
    if is_fuzz_credit(finder):
        return "fuzz"
    return "other"
