"""The runtime contract for byte-reproducible committed figures."""

from __future__ import annotations

import os
import platform

RENDERER_ID = "linux-amd64-python-3.12.13"
RENDERER_ENV = "AI_DISCOVERY_RENDERER"


def assert_canonical_renderer(*, matplotlib_version: str | None = None,
                              freetype_version: str | None = None) -> None:
    """Reject a host that cannot produce the repository's canonical PNGs."""
    actual = {
        "marker": os.environ.get(RENDERER_ENV, "unset"),
        "system": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
    expected = {
        "marker": RENDERER_ID,
        "system": "Linux",
        "machine": "x86_64",
        "python": "3.12.13",
    }
    if matplotlib_version is not None:
        actual["matplotlib"] = matplotlib_version
        expected["matplotlib"] = "3.11.1"
    if freetype_version is not None:
        actual["freetype"] = freetype_version
        expected["freetype"] = "2.14.3"

    wrong = [
        f"{key}={actual[key]} (expected {value})"
        for key, value in expected.items()
        if actual[key] != value
    ]
    if wrong:
        raise RuntimeError(
            "non-canonical figure renderer: " + "; ".join(wrong)
            + ". Run `make figure PROBLEM=<slug>` or `make figures`; "
              "do not run figure.py directly."
        )
