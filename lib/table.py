"""Read and write the vendored CSVs.

Every series is a CSV in its own problem folder, read and written through here so
quoting and newline handling stay identical across the repository. A fetcher that
formats its own CSV will eventually differ from the rest in a way that shows up
as a spurious diff.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: CSV has no header")
        duplicate_fields = [
            field for field, count in Counter(reader.fieldnames).items() if count > 1
        ]
        if duplicate_fields:
            raise ValueError(
                f"{path}: duplicate CSV column(s): {', '.join(duplicate_fields)}"
            )
        rows = list(reader)
    for line_number, row in enumerate(rows, 2):
        if None in row:
            raise ValueError(
                f"{path}:{line_number}: row has {len(row[None])} extra field(s)"
            )
        missing = [field for field, value in row.items() if value is None]
        if missing:
            raise ValueError(
                f"{path}:{line_number}: row is missing field(s): {', '.join(missing)}"
            )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    """Write rows, creating the folder if needed. Field order follows the first row."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write an empty {path.name}")
    fields = fieldnames or list(rows[0].keys())
    # Preserve a vendored file's established newline style so a refresh changes
    # data rows, not every line in the file. New files use LF.
    line_ending = (
        "\r\n" if path.exists() and b"\r\n" in path.read_bytes() else "\n"
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=line_ending)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.name} ({len(rows)} rows)")
