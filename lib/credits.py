"""Deciding whether a vulnerability credit names an AI system.

Every cyber series in this repository counts disclosures by who is credited with
finding them, which reduces to matching a finder string against a list of
markers. The lists live here rather than in the six problem folders, because a
marker added in one folder and not the others would make the codebases quietly
incomparable.

The classification is by explicit textual marker, so every count it produces is
a floor: a researcher who used a model without saying so is counted as human.
Fuzzers are kept apart from AI deliberately — a fuzzer is automated but is not a
model, and folding them together would credit a decade of fuzzing to LLMs.

The three lists below are not identical, and the differences are historical
rather than principled: they were written against three sources at three times.
CURL_AI is the narrowest, ADVISORY_AI adds a bare "aisle" that FIREFOX_AI lacks.
Unifying them would change published counts, so they are kept as they are and
the divergence is recorded here where it is visible. If you widen one, say in
the problem folder's README which series moved and by how much.
"""

from __future__ import annotations

import re

# curl's own vuln.json, matched against the FINDER credits.
CURL_AI = re.compile(
    r"big sleep|mythos|openai|anthropic|antaisecuritylab|aisle research"
    r"|autonomous code security|xbow|zeropath|\bagent\b",
    re.I,
)

# Mozilla advisories, matched against the per-CVE `reporter` string.
FIREFOX_AI = re.compile(
    r"\bclaude\b|\banthropic\b|\bopenai\b|\bgpt\b|big sleep|mythos|\bgemini\b"
    r"|antaisecuritylab|aisle research|autonomous code security|xbow|zeropath"
    r"|\bLLM\b|\bagent\b|using AI\b",
    re.I,
)

# OpenSSL's "Found by" credits, and the finder-level tables for all three.
ADVISORY_AI = re.compile(
    r"\bclaude\b|\banthropic\b|\bopenai\b|\bgpt\b|big sleep|mythos|\bgemini\b"
    r"|antaisecuritylab|aisle research|\baisle\b|autonomous code security|xbow"
    r"|zeropath|\bLLM\b|\bagent\b|using AI\b",
    re.I,
)

FUZZ = re.compile(r"fuzz", re.I)

SEVERITIES = ["Low", "Medium", "High", "Critical"]


def classify(finder: str, ai: re.Pattern[str] = ADVISORY_AI) -> str:
    """Return "ai", "fuzz" or "other" for one finder credit."""
    if ai.search(finder or ""):
        return "ai"
    if FUZZ.search(finder or ""):
        return "fuzz"
    return "other"
