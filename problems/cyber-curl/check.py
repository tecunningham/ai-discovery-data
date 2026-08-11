#!/usr/bin/env python3
"""Recompute the numerical claims in this folder's hand-written prose."""

from __future__ import annotations

import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    annual = read("curl-vulnerabilities.csv")
    finders = read("curl-finders.csv")
    openssl_finders = read("../cyber-openssl/openssl-finders.csv")
    prose = re.sub(r"\s+", " ", (HERE / "README.md").read_text(encoding="utf-8"))
    current = next(row for row in annual if row["year"] == "2026")
    baseline = [
        row for row in annual if 2014 <= int(row["year"]) <= 2023
    ]
    average = sum(int(row["total"]) for row in baseline) / len(baseline)
    aisle = sum(
        int(row["cves"])
        for row in finders
        if row["year"] == "2026" and "Aisle Research" in row["finder"]
    )
    big_sleep_years = {
        row["year"] for row in finders if "Big Sleep" in row["finder"]
    }
    shared_fort = (
        any("Stanislav Fort" in row["finder"] for row in finders)
        and any("Stanislav Fort" in row["finder"] for row in openssl_finders)
    )
    ai_low_share = round(
        100 * int(current["ai_sev_low"]) / int(current["ai_attributed"])
    )
    other_low_share = round(
        100 * int(current["other_sev_low"]) / int(current["other_attributed"])
    )

    expected = {
        f"{current['total']} through 24 June 2026": "current total",
        f"with {current['ai_attributed']} of those crediting": "current AI count",
        f"{average:.1f} a year across 2014–2023": "baseline average",
        f"{ai_low_share}% are rated Low": "AI severity share",
        f"{other_low_share}% Low for the other finders": "other severity share",
        f"and {aisle} from Aisle Research": "Aisle count",
        "Big Sleep's curl credit is in 2025, not 2026": "Big Sleep year",
        "Stanislav Fort of Aisle Research appears in both curl and OpenSSL":
            "cross-project finder",
    }
    failures = [
        f"README lacks recomputed {label}: {phrase!r}"
        for phrase, label in expected.items()
        if phrase not in prose
    ]
    if big_sleep_years != {"2025"}:
        failures.append(f"Big Sleep years are {sorted(big_sleep_years)}, expected 2025")
    if not shared_fort:
        failures.append("Stanislav Fort is not present in both finder tables")
    for failure in failures:
        print(failure)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
