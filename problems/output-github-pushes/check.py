#!/usr/bin/env python3
"""Check this folder's CSV and the numbers its README prints.

Run: python3 problems/output-github-pushes/check.py
     python3 problems/output-github-pushes/check.py --upstream   # needs network

The failure this guards against is specific. GitHub's Innovation Graph publishes
one row per economy plus an aggregate EU row that repeats its member states, so
a sum that keeps EU overstates every metric by about a fifth. The fetcher drops
it, and in 2026 upstream renamed the economy column from `iso2` to `iso2_code`,
which is exactly the kind of change that can make a drop silently stop working.
The offline checks below assert the shape of the vendored data; `--upstream`
re-sums the published files and asserts the vendored totals equal the EU-free
sum and differ from the EU-inclusive one.
"""

from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402

METRICS = ("git_pushes", "repositories", "developers")
CSV_NAME = "github-innovationgraph-global.csv"


def quarter_key(quarter: str) -> tuple[int, int]:
    year, index = quarter.split("-Q")
    return int(year), int(index)


def offline(rows: list[dict[str, str]], prose: str) -> list[str]:
    failures: list[str] = []
    for row in rows:
        if "EU aggregate row excluded" not in row["note"]:
            failures.append(f"{row['quarter']} does not record the EU exclusion")
        for metric in METRICS:
            if not row[metric].isdigit() or int(row[metric]) <= 0:
                failures.append(f"{row['quarter']} has no positive {metric}")

    keys = [quarter_key(row["quarter"]) for row in rows]
    if keys != sorted(keys):
        failures.append("quarters are not in ascending order")
    for earlier, later in zip(keys, keys[1:]):
        expected = (earlier[0] + 1, 1) if earlier[1] == 4 else (earlier[0], earlier[1] + 1)
        if later != expected:
            failures.append(f"gap between {earlier} and {later}")

    # Repositories and developers are cumulative upstream, so a fall in either is
    # a sign the economy set changed under the sum rather than real movement.
    for field in ("repositories", "developers"):
        for earlier, later in zip(rows, rows[1:]):
            if int(later[field]) < int(earlier[field]):
                failures.append(
                    f"{field} falls from {earlier['quarter']} to {later['quarter']}"
                )

    by_quarter = {row["quarter"]: row for row in rows}
    claims = {
        "135.4 million in 2022-Q4": ("2022-Q4", 135.4),
        "167.8 million in 2024-Q4": ("2024-Q4", 167.8),
        "319.8 million in 2026-Q1": ("2026-Q1", 319.8),
        "246.8 million in 2025-Q4": ("2025-Q4", 246.8),
    }
    for phrase, (quarter, millions) in claims.items():
        if phrase not in prose:
            failures.append(f"README lacks the claim {phrase!r}")
        elif round(int(by_quarter[quarter]["git_pushes"]) / 1e6, 1) != millions:
            failures.append(
                f"README says {phrase} but the CSV holds "
                f"{int(by_quarter[quarter]['git_pushes']) / 1e6:.1f} million"
            )

    first, last = rows[0], rows[-1]
    middle = by_quarter["2022-Q4"]
    growth = {
        "adds 68%": (first, middle),
        "adds 136%": (middle, last),
    }
    for phrase, (start, end) in growth.items():
        stated = int(re.search(r"(\d+)", phrase).group(1))
        actual = round(
            (int(end["git_pushes"]) / int(start["git_pushes"]) - 1) * 100
        )
        if phrase not in prose:
            failures.append(f"README lacks the claim {phrase!r}")
        elif actual != stated:
            failures.append(
                f"README says {phrase} from {start['quarter']} to {end['quarter']}, "
                f"recomputed {actual}%"
            )

    # The recent-quarters ratio and the verdict clause, recomputed from the
    # same rows the claims above check.
    ratio = int(last["git_pushes"]) / int(rows[-6]["git_pushes"])
    mean_2025 = sum(int(by_quarter[f"2025-Q{i}"]["git_pushes"])
                    for i in range(1, 5)) / 4
    recomputed = {
        f"{ratio:.1f} times in five quarters": "recent-quarters ratio",
        f"{int(last['git_pushes']) / 1e6:.1f} million pushes in "
        f"{last['quarter']} against "
        f"{int(by_quarter['2025-Q4']['git_pushes']) / 1e6:.1f} million in "
        f"2025-Q4 and a 2025 quarterly mean of {mean_2025 / 1e6:.1f} million":
            "verdict clause",
        f"Coverage:** {first['quarter']} to {last['quarter']}, quarterly":
            "coverage field",
    }
    for phrase, label in recomputed.items():
        if phrase not in prose:
            failures.append(f"README lacks recomputed {label}: {phrase!r}")
    return failures


def upstream(rows: list[dict[str, str]]) -> list[str]:
    """Re-sum the published files and prove the EU aggregate is not in the CSV."""
    from lib.web import fetch

    from fetch import URL  # noqa: E402

    failures: list[str] = []
    for metric in METRICS:
        raw = fetch(URL.format(metric=metric), refresh=True).decode("utf-8")
        records = list(csv.DictReader(io.StringIO(raw)))
        field = "iso2_code" if "iso2_code" in (records[0] if records else {}) else "iso2"
        excluding: dict[str, int] = {}
        including: dict[str, int] = {}
        for record in records:
            quarter = f"{record['year']}-Q{record['quarter']}"
            value = int(record[metric])
            including[quarter] = including.get(quarter, 0) + value
            if record[field] != "EU":
                excluding[quarter] = excluding.get(quarter, 0) + value
        if not any(record[field] == "EU" for record in records):
            failures.append(
                f"{metric}: upstream no longer publishes an EU row under {field!r}; "
                "confirm the column was not renamed again"
            )
        for row in rows:
            quarter, vendored = row["quarter"], int(row[metric])
            if quarter not in excluding:
                failures.append(f"{metric}: upstream no longer covers {quarter}")
                continue
            if vendored != excluding[quarter]:
                failures.append(
                    f"{metric} {quarter}: vendored {vendored:,} against an EU-free "
                    f"sum of {excluding[quarter]:,}"
                )
            elif vendored == including[quarter] and including[quarter] != excluding[quarter]:
                failures.append(f"{metric} {quarter}: vendored value includes EU")
    return failures


def main() -> int:
    rows = read_csv(HERE / CSV_NAME)
    prose = re.sub(r"\s+", " ", (HERE / "README.md").read_text(encoding="utf-8"))
    failures = offline(rows, prose)
    if "--upstream" in sys.argv:
        failures += upstream(rows)
    for failure in failures:
        print(failure)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
