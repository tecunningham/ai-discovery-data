#!/usr/bin/env python3
"""Draw this folder's two figures from its annual disclosure counts.

Run: python3 problems/cyber-curl/figure.py

The first figure counts disclosures. The second cuts the same rows by curl's own
severity rating, which is the folder's check on whether a rising count is a
rising amount of harm.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import SEVERITIES  # noqa: E402
from lib.families import cyber_stacked, severity_panels  # noqa: E402
from lib.table import read_csv  # noqa: E402

# The severity drift is a long-run story, but curl disclosed one or two issues in
# some early years and a share computed on two rows is noise drawn at full width.
FROM_YEAR = 2010


def counts(row: dict[str, str], prefix: str = "") -> dict[str, int]:
    return {severity: int(row[f"{prefix}sev_{severity.lower()}"])
            for severity in SEVERITIES}


def totalled(rows: list[dict[str, str]], prefix: str = "") -> dict[str, int]:
    out = {severity: 0 for severity in SEVERITIES}
    for row in rows:
        for severity, value in counts(row, prefix).items():
            out[severity] += value
    return out


def main() -> None:
    cyber_stacked(
        HERE / "curl-vulnerabilities.csv",
        HERE / "discovery-cyber-curl.png",
        "curl vulnerability disclosures",
        "One fixed codebase; annual disclosures split by explicit finder credit",
        "curl vulnerability JSON, counted in the vendored CSV",
        "https://curl.se/docs/vuln.json",
        __file__,
    )

    rows = [row for row in read_csv(HERE / "curl-vulnerabilities.csv")
            if int(row["year"]) >= FROM_YEAR]
    by_year = {row["year"]: counts(row) for row in rows}
    latest = rows[-1]

    # Four cohorts, ordered so the reading runs from the long baseline to the
    # newest AI-marked slice. The middle bar is the one that matters: it is the
    # non-AI drift that was already under way before any AI credit appeared, so
    # the last bar cannot be read as AI having started the shallowing.
    early = [row for row in rows if int(row["year"]) <= 2022]
    recent_human = [row for row in rows if 2023 <= int(row["year"]) <= 2025]
    cohorts = [
        (f"{early[0]['year']}–{early[-1]['year']}, all finders", totalled(early)),
        ("2023–2025, non-AI credits", totalled(recent_human, "other_")),
        (f"{latest['year']}, other credits", counts(latest, "other_")),
        (f"{latest['year']}, AI-marked credits", counts(latest, "ai_")),
    ]

    severity_panels(
        HERE / "severity-cyber-curl.png",
        "curl disclosures by severity",
        "The same rows as the disclosure chart, cut by curl's own severity rating",
        years=[row["year"] for row in rows],
        by_year=by_year,
        cohorts=cohorts,
        severities=SEVERITIES,
        source_label="curl vulnerability JSON, counted in the vendored CSV",
        source_url="https://curl.se/docs/vuln.json",
        built_by=__file__,
        year_caption=(
            f"Shares, so a {min(int(row['total']) for row in rows)}-disclosure year "
            f"is as tall as a {max(int(row['total']) for row in rows)}-disclosure one."
        ),
        cohort_caption="Share of that cohort's disclosures",
    )


if __name__ == "__main__":
    main()
