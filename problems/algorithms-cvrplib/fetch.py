#!/usr/bin/env python3
"""Rebuild the fixed-X CVRPLIB frontier ledger from the public update log."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402

BASE = "https://galgos.inf.puc-rio.br/cvrplib/index.php/en/updates/"


class Items(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.current: list[str] | None = None
        self.items: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        classes = dict(attrs).get("class", "").split()
        if tag == "div" and self.current is None and {"list-group-item", "p-3"} <= set(classes):
            self.current = []
            self.depth = 1
        elif self.current is not None and tag == "div":
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.current is None or tag != "div":
            return
        self.depth -= 1
        if self.depth == 0:
            self.items.append(" ".join(" ".join(self.current).split()))
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current.append(data)


def fetch_page(page: int) -> list[str]:
    url = f"{BASE}?page={page}"
    request = Request(url, headers={"User-Agent": "ai-discovery-data/1.0"})
    parser = Items()
    parser.feed(urlopen(request, timeout=45).read().decode("utf-8"))
    return parser.items


def extract() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    # Follow the pagination until a page contributes nothing new, rather than
    # assuming how many pages the ledger has grown to: a sixth page appearing
    # upstream would otherwise be skipped without any check noticing. The cap
    # exists so a site that echoes its last page forever cannot loop this.
    page = 0
    while True:
        page += 1
        if page > 40:
            raise RuntimeError("more than 40 update pages; check the pagination")
        added = 0
        source_url = f"{BASE}?page={page}"
        for text in fetch_page(page):
            date_match = re.match(r"([A-Z][a-z]+ \d{1,2}, \d{4})", text)
            if not date_match:
                continue
            recorded = datetime.strptime(date_match.group(1), "%B %d, %Y").date().isoformat()
            instances = re.findall(r"\b(X-(?:n)?\d+-k\d+)\s*\(([\d,.]+)\)", text)
            instances = [
                (re.sub(r"^X-(?!n)", "X-n", name), objective.replace(",", ""))
                for name, objective in instances
            ]
            kinds = []
            if re.search(r"improv|BKS", text, re.I):
                kinds.append("objective_improvement")
            if re.search(r"proven optimal|proved optimal", text, re.I):
                kinds.append("optimality_proof")
            for kind in kinds:
                for instance, objective in instances:
                    key = recorded, instance, objective, kind
                    if key in seen:
                        continue
                    seen.add(key)
                    added += 1
                    rows.append({
                        "recorded_date": recorded,
                        "instance": instance,
                        "objective": objective,
                        "event_type": kind,
                        "source_url": source_url,
                    })
        if added == 0:
            break
    return sorted(rows, key=lambda row: (
        row["recorded_date"], row["event_type"], row["instance"], row["objective"]
    ))


def main() -> None:
    rows = extract()
    if len(rows) < 280:
        raise RuntimeError(f"only extracted {len(rows)} X-frontier events; page structure changed")
    write_csv(HERE / "cvrplib-x-frontier.csv", rows)


if __name__ == "__main__":
    main()
