#!/usr/bin/env python3
"""Rebuild github-innovationgraph-global.csv from GitHub's Innovation Graph.

Run: python3 problems/output-github-pushes/fetch.py
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = ("https://raw.githubusercontent.com/github/innovationgraph/"
       "main/data/{metric}.csv")
METRICS = ("git_pushes", "repositories", "developers")


def build() -> list[dict]:
    """Innovation Graph quarterly totals, summed over economies.

    GitHub publishes per-economy files rather than a global total. The EU row
    is an aggregate of member states and would double-count, so it is dropped;
    economies below the dataset's 100-developer reporting threshold are absent
    from the files altogether, so the sum slightly undercounts.
    """
    sums: dict[str, dict[str, int]] = {}
    for metric in METRICS:
        raw = fetch(URL.format(metric=metric)).decode("utf-8")
        for record in csv.DictReader(io.StringIO(raw)):
            # Innovation Graph renamed this field from iso2 to iso2_code in
            # 2026. Accept both so the aggregate EU row is never double-counted.
            economy = record.get("iso2_code") or record.get("iso2")
            if economy == "EU":
                continue
            quarter = f"{record['year']}-Q{record['quarter']}"
            sums.setdefault(quarter, {})
            sums[quarter][metric] = sums[quarter].get(metric, 0) + int(record[metric])
    note = ("sum over economies in github/innovationgraph data (EU aggregate row "
            "excluded); economies below 100-developer reporting threshold not included")
    rows = [{"quarter": quarter,
             "git_pushes": str(values.get("git_pushes", "")),
             "repositories": str(values.get("repositories", "")),
             "developers": str(values.get("developers", "")),
             "note": note}
            for quarter, values in sorted(sums.items())]
    print(f"github: {len(rows)} quarters, {rows[0]['quarter']}–{rows[-1]['quarter']}; "
          f"{int(rows[-1]['git_pushes']) / 1e6:.1f}M pushes in the last quarter")
    return rows


if __name__ == "__main__":
    write_csv(HERE / "github-innovationgraph-global.csv", build())
