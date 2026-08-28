"""Reading a problem page's title and front matter.

FORMAT.md's front matter is a bullet list whose values are hard-wrapped across
continuation lines, so any reader matching a single physical line silently
truncates the value mid-sentence. That happened: the generated index tables
carried ten folders' Metric and Coverage cut off at the first line break, and a
multi-line **Data:** list was read as its first row only. The joining lives
here, once, for tools/check.py and tools/build_docs.py both.
"""

from __future__ import annotations

import re

_TITLE = re.compile(r"^#\s+(.+)$", re.M)
_FIELD = re.compile(r"^- \*\*([A-Za-z?]+):\*\*\s*(.*)$")


def title(text: str) -> str:
    """The document's `# ` heading, or an empty string."""
    match = _TITLE.search(text)
    return match.group(1).strip() if match else ""


def front_matter(text: str) -> dict[str, str]:
    """Field name to full value, continuation lines joined with single spaces.

    Only the text above the first `## ` section heading is read, so a fact
    line deeper in the document can never shadow a front-matter field. A value
    runs until the next bullet, a blank line, a heading, an image embed, or a
    blockquote — the shapes that end the front-matter list in practice.
    """
    fields: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = _FIELD.match(line)
        if match:
            current = match.group(1)
            fields[current] = match.group(2).strip()
            continue
        if current is None:
            continue
        if not line.strip() or line.startswith(("#", "- ", ">", "![")):
            current = None
            continue
        fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields
