"""Signals present in vulnerability finder credits.

Every finder-attributed cyber series matches its credit strings against the same
marker list. The list lives here rather than in the problem folders, because a
marker added in one folder and not the others would make the codebases quietly
incomparable.

Three signals are read out of a credit string, and they are independent:

``explicit_ai``
    The credit names an AI system or states an AI method — "using Claude",
    "powered by Mythos", "Big Sleep". This is the only signal that speaks to how
    a finding was made.
``ai_affiliated``
    The credit names an AI lab or an AI-security company — Anthropic, OpenAI,
    Aisle Research, XBOW, ZeroPath, AntAISecurityLab. This is an employer, not a
    method. A researcher at an AI company can find a bug by reading code.
``fuzz``
    The credit names fuzzing. This is deliberately *orthogonal* to the two
    above rather than a competing category, because an AI-written harness or an
    AI-guided fuzzer is legitimately both, and forcing a choice would hide
    exactly the cases that matter.

None of these is a measurement of cause. A credit that names no AI can still
have been found with one, and a credit that names an AI company need not have
used a model for that finding. So the counts here carry error in both
directions and are **not** a floor on AI involvement: the affiliation-only band
can overstate it as easily as silent model use understates it. Only the
``explicit_ai`` band is evidence about method, and even that is usually the
finder's own account. A caller that wants to make a causal claim has to add
finding-level provenance from another source — see
``problems/cyber-openssl/`` for the shape that takes.

The bare name "Claude" is ambiguous before the model era, so that one marker is
accepted only from 2024 onward. Callers pass the disclosure year to enforce that
guard even though no currently vendored pre-2024 credit is affected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Shared across curl FINDER credits, Mozilla reporter strings, and OpenSSL
# reporter credits. These names establish an employer, not a discovery method.
# "Autonomous Code Security" is here rather than among the method markers
# because it is the name of a team at Microsoft, not a statement about how a
# particular bug was found.
AI_AFFILIATION = re.compile(
    r"\banthropic\b|\bopenai\b|antaisecuritylab|aisle research|\baisle\b"
    r"|xbow|zeropath|autonomous code security",
    re.I,
)

# These name a system or a method. "Aisle" as a bare company name is not here:
# the company is an affiliation, and its CVE-level claims are provenance a
# caller adds separately.
EXPLICIT_AI_METHOD = re.compile(
    r"\bgpt\b|big sleep|mythos|\bgemini\b|\bLLM\b|\bagent\b|using AI\b",
    re.I,
)
CLAUDE = re.compile(r"\bclaude\b", re.I)

# Compatibility matcher for code that needs the old undifferentiated signal.
AI_CREDIT = re.compile(
    rf"{AI_AFFILIATION.pattern}|{EXPLICIT_AI_METHOD.pattern}|\bclaude\b",
    re.I,
)

# Compatibility aliases for code and notebooks that imported the old names.
CURL_AI = FIREFOX_AI = ADVISORY_AI = AI_CREDIT

FUZZ = re.compile(r"fuzz", re.I)

SEVERITIES = ["Low", "Medium", "High", "Critical"]

# Display precedence, most specific first. Charts need one band per bar segment
# even though the underlying signals overlap; this order is a rendering rule and
# does not erase the signals it passes over.
BANDS = ["explicit_ai", "ai_affiliated", "fuzz", "other"]


@dataclass(frozen=True)
class Signals:
    """The independent signals one credit string carries."""

    explicit_ai: bool
    ai_affiliated: bool
    fuzz: bool

    @property
    def any_ai_marker(self) -> bool:
        """Either AI signal, which is what the pre-split series counted."""
        return self.explicit_ai or self.ai_affiliated

    @property
    def band(self) -> str:
        """The single band this credit is drawn in, by BANDS precedence."""
        if self.explicit_ai:
            return "explicit_ai"
        if self.ai_affiliated:
            return "ai_affiliated"
        if self.fuzz:
            return "fuzz"
        return "other"


def has_ai_affiliation(finder: str) -> bool:
    """Whether a credit names an AI lab or AI-security company."""
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


def signals(finder: str, year: int | None = None) -> Signals:
    """Read all three independent signals out of one credit string."""
    return Signals(
        explicit_ai=names_ai_method(finder, year),
        ai_affiliated=has_ai_affiliation(finder),
        fuzz=is_fuzz_credit(finder),
    )


def band(finder: str, year: int | None = None) -> str:
    """Return the display band for one credit: see BANDS for the precedence."""
    return signals(finder, year).band


def classify(finder: str, year: int | None = None) -> str:
    """Return the pre-split category: "ai", "fuzz" or "other".

    Kept for series whose vendored CSVs were built before the AI signal was
    split, so that refetching one folder does not silently redefine another's
    columns. New work should call ``signals`` or ``band``.
    """
    result = band(finder, year)
    return "ai" if result in ("explicit_ai", "ai_affiliated") else result
