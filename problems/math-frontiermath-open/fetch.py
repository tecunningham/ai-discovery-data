#!/usr/bin/env python3
"""Rebuild frontiermath-open-problems.csv from Epoch AI's problem pages.

Run: python3 problems/math-frontiermath-open/fetch.py

The problem list comes from the site's sitemap and each problem's own page:
the status chip ("Solved (AI)", "Solved (human)", "Unsolved"), the field chip,
the task-type chips, and the notability badge are all server-rendered HTML, so
the ledger is a mechanical read of what each page states on the day it runs.
An unrecognised status chip is a hard failure rather than a guessed mapping,
so a new page state shows up as a fetcher error instead of a silent category.

The solution-event ledger beside this file,
frontiermath-open-solutions.csv, is hand-transcribed and is not rewritten
here: the dates, systems and elicitors of each solve live in the pages'
solution-update prose and announcement posts, which no parser can read
reliably. Rerunning this fetcher therefore updates statuses and the problem
pool while leaving the reviewed event ledger alone; a status this fetcher
writes that has no matching event row is exactly the disagreement the folder's
check.py exists to catch.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

SITEMAP = "https://epoch.ai/sitemap-pages-0.xml"
PREFIX = "https://epoch.ai/frontiermath/open-problems/"
STATUS = {
    "Solved (AI)": "solved_ai",
    "Solved (human)": "solved_human",
    "Unsolved": "unsolved",
}
# The badge is usually one of the four notability tiers, but not always:
# the withdrawn explicit-deformations page badges "Novel example" instead.
# The value is recorded verbatim; the figure buckets non-tier values.
TIERS = ("Moderately interesting", "Solid result", "Major advance",
         "Breakthrough")


def problem_urls() -> list[str]:
    sitemap = fetch(SITEMAP).decode("utf-8")
    urls = sorted(set(re.findall(rf"{PREFIX}[a-z0-9-]+", sitemap)))
    return [url for url in urls if not url.endswith("/about")]


def parse_page(url: str) -> dict[str, str]:
    page = fetch(url).decode("utf-8")
    title = re.search(r'<h1 class="title"[^>]*>([^<]+)</h1>', page)
    status = re.search(
        r'<span class="chip chip-(?:unsolved|solved(?:-human)?) ui-4">'
        r'.*?</span>([^<]+)</span>',
        page, re.S)
    meta_start = page.find('<div class="problem-meta"')
    chips = re.findall(r'<span class="chip chip-normal ui-4">([^<]+)</span>',
                       page[meta_start:meta_start + 4000])
    tags = re.findall(r'<span class="problem-tag-chip"><span[^>]*>([^<]+)',
                      page[meta_start:meta_start + 4000])
    badge = re.search(r'<span class="badge-text">([^<]+)</span>', page)
    if not (title and status):
        raise SystemExit(f"{url}: page has no title or status chip; "
                         "the layout has changed and this parser needs updating")
    status_text = html.unescape(status.group(1)).strip()
    if status_text not in STATUS:
        raise SystemExit(f"{url}: unrecognised status chip {status_text!r}")
    notability = html.unescape(badge.group(1)).strip() if badge else ""
    field = html.unescape(chips[0]).strip() if chips else ""
    return {
        "slug": url.removeprefix(PREFIX),
        "title": html.unescape(title.group(1)).strip(),
        "field": field,
        "task_type": "; ".join(dict.fromkeys(
            html.unescape(tag).strip() for tag in tags)),
        "notability": notability,
        "status": STATUS[status_text],
        "source_url": url,
    }


def main() -> None:
    rows = [parse_page(url) for url in problem_urls()]
    write_csv(HERE / "frontiermath-open-problems.csv", rows)
    counts = {value: sum(row["status"] == value for row in rows)
              for value in STATUS.values()}
    print(f"wrote {len(rows)} problem pages: "
          + ", ".join(f"{count} {value}" for value, count in counts.items()))


if __name__ == "__main__":
    main()
