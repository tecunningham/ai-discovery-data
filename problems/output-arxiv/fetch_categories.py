#!/usr/bin/env python3
"""Build month × primary-category submission counts for the arXiv corpus.

Run by hand, either way:

    python3 problems/output-arxiv/fetch_categories.py --snapshot <path>
    python3 problems/output-arxiv/fetch_categories.py            # OAI harvest
    python3 problems/output-arxiv/fetch_categories.py --resume   # after a crash

Writes arxiv-categories-by-month.csv: one row per (month, primary category)
with the count of papers whose first version was submitted that month. The
month comes from the v1 submission date — not the OAI datestamp or
update_date, which move on every metadata edit; the category is the primary
(first-listed) one, so each paper counts once and the columns sum to the
monthly totals series up to arXiv's own historical corrections.

The fast path is arXiv's official metadata snapshot — the ~5 GB
arxiv-metadata-oai-snapshot.json distributed via Kaggle
(Cornell-University/arxiv), one JSON record per line, updated weekly. It
needs a Kaggle login to download, so it is an operator convenience rather
than the documented rebuild: the no-auth path is the OAI-PMH harvest of
https://oaipmh.arxiv.org/oai, which walks ~2,400 resumption pages and takes
the better part of a day at the pace the endpoint meters out. Both paths
produce the same aggregation; papers first submitted after lib/chart.py's
AS_OF_DATE are dropped, so a re-run reproduces the committed window plus
whatever upstream recategorized since.

Not part of `make fetch` and excluded from the weekly freshness workflow by
its filename, on both counts: the snapshot needs credentials and the harvest
needs hours. For the harvest, a checkpoint (counts + resumption token) is
saved under .cache/ every 25 pages; --resume continues from it while the
token is still valid on arXiv's side.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import AS_OF_DATE  # noqa: E402
from lib.table import write_csv  # noqa: E402

BASE = "https://oaipmh.arxiv.org/oai"
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "arxiv": "http://arxiv.org/OAI/arXiv/",
}
CHECKPOINT = HERE.parents[1] / ".cache" / "arxiv-oai-checkpoint.json"
# arXiv's OAI turns hostile toward eager harvesters: sustained one-a-second
# paging earns 503s whose Retry-After can run to many minutes, and retrying
# early resets the penalty. Four seconds between pages stays under the radar,
# and a 503's full Retry-After is honoured up to fifteen minutes.
PAGE_DELAY_SECONDS = 4.0
RETRY_AFTER_CAP_SECONDS = 900


def fetch_page(params: dict[str, str]) -> bytes:
    """One OAI request, honouring 503 flow control and retrying transients."""
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "ai-discovery-data arXiv category harvest"}
    )
    for attempt in range(8):
        try:
            # The endpoint meters ListRecords hard and a page can take
            # minutes to arrive; a short socket timeout turns a slow page
            # into a wasted wait plus a retry of the same slow page.
            with urllib.request.urlopen(request, timeout=900) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 503:
                wait = min(max(int(error.headers.get("Retry-After") or "30"),
                               5), RETRY_AFTER_CAP_SECONDS)
                print(f"  503; waiting {wait}s as asked", flush=True)
                time.sleep(wait)
                continue
            if error.code >= 500:
                time.sleep(30 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            # A timeout has already spent its wait; retry promptly.
            print(f"  {type(error).__name__}; backing off", flush=True)
            time.sleep(10)
    raise SystemExit(f"gave up after 8 attempts on {url}")


def parse_page(payload: bytes) -> tuple[list[tuple[str, str]], str | None, str]:
    """(created, primary category) pairs, the resumption token, and list size."""
    root = ET.fromstring(payload)
    error = root.find("oai:error", NS)
    if error is not None:
        raise SystemExit(f"OAI error {error.get('code')}: {error.text}")
    pairs = []
    for record in root.iterfind(".//oai:record", NS):
        header = record.find("oai:header", NS)
        if header is not None and header.get("status") == "deleted":
            continue
        created = record.find(".//arxiv:created", NS)
        categories = record.find(".//arxiv:categories", NS)
        if created is None or not (created.text or "").strip():
            continue
        if categories is None or not (categories.text or "").strip():
            continue
        pairs.append((created.text.strip(), categories.text.split()[0]))
    token = root.find(".//oai:resumptionToken", NS)
    size = token.get("completeListSize", "?") if token is not None else "?"
    value = (token.text or "").strip() if token is not None else ""
    return pairs, (value or None), size


def save_checkpoint(counts: Counter, token: str | None, pages: int) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps({
        "token": token,
        "pages": pages,
        "counts": {f"{month}|{category}": count
                   for (month, category), count in counts.items()},
    }))


def load_checkpoint() -> tuple[Counter, str | None, int]:
    state = json.loads(CHECKPOINT.read_text())
    counts: Counter = Counter()
    for key, count in state["counts"].items():
        month, category = key.split("|", 1)
        counts[(month, category)] = count
    return counts, state["token"], state["pages"]


def harvest(resume: bool) -> Counter:
    cutoff = AS_OF_DATE.isoformat()
    counts: Counter = Counter()
    token: str | None = None
    pages = 0
    kept = 0
    if resume and CHECKPOINT.exists():
        counts, token, pages = load_checkpoint()
        kept = sum(counts.values())
        print(f"resuming from page {pages} with {kept} records counted",
              flush=True)
        if token is None:
            print("checkpoint was already complete", flush=True)
            return counts
    while True:
        params = (
            {"verb": "ListRecords", "resumptionToken": token}
            if token else
            {"verb": "ListRecords", "metadataPrefix": "arXiv"}
        )
        pairs, token, size = parse_page(fetch_page(params))
        pages += 1
        for created, category in pairs:
            if created > cutoff:
                continue
            counts[(created[:7], category)] += 1
            kept += 1
        if pages % 25 == 0:
            save_checkpoint(counts, token, pages)
            print(f"{time.strftime('%H:%M:%S')} page {pages}: {kept} records "
                  f"counted (complete list size {size})", flush=True)
        if token is None:
            save_checkpoint(counts, None, pages)
            print(f"done: {pages} pages, {kept} records", flush=True)
            return counts
        time.sleep(PAGE_DELAY_SECONDS)


def from_snapshot(path: Path) -> Counter:
    """Aggregate the Kaggle snapshot: same counting rule as the harvest."""
    import email.utils

    cutoff = AS_OF_DATE
    counts: Counter = Counter()
    total = 0
    skipped = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            total += 1
            versions = record.get("versions") or []
            v1 = next((v for v in versions if v.get("version") == "v1"), None)
            categories = (record.get("categories") or "").split()
            if v1 is None or not v1.get("created") or not categories:
                skipped += 1
                continue
            created = email.utils.parsedate_to_datetime(v1["created"]).date()
            if created > cutoff:
                continue
            counts[(created.isoformat()[:7], categories[0])] += 1
    print(f"snapshot: {total} records, {sum(counts.values())} counted, "
          f"{skipped} without a v1 date or category", flush=True)
    return counts


def main() -> None:
    if "--snapshot" in sys.argv[1:]:
        after = sys.argv[sys.argv.index("--snapshot") + 1:]
        # The conventional local home for the snapshot; gitignored, since
        # five gigabytes of upstream metadata is not this repository's to
        # vendor.
        path = (Path(after[0]).expanduser() if after
                else HERE / "arxiv-metadata-oai-snapshot.json")
        counts = from_snapshot(path)
    else:
        counts = harvest(resume="--resume" in sys.argv[1:])
    rows = [
        {"month": month, "category": category, "submissions": count}
        for (month, category), count in sorted(counts.items())
    ]
    categories = {row["category"] for row in rows}
    print(f"arxiv categories: {len(rows)} month-category rows, "
          f"{len(categories)} primary categories, "
          f"{rows[0]['month']}–{rows[-1]['month']}")
    write_csv(HERE / "arxiv-categories-by-month.csv", rows)


if __name__ == "__main__":
    main()
