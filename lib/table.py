"""Read and write the vendored CSVs.

Every series is a CSV in its own problem folder, read and written through here so
quoting and newline handling stay identical across the repository. A fetcher that
formats its own CSV will eventually differ from the rest in a way that shows up
as a spurious diff.
"""

from __future__ import annotations

import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    """Write rows, creating the folder if needed. Field order follows the first row."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write an empty {path.name}")
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name} ({len(rows)} rows)")
