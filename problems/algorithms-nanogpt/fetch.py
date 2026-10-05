#!/usr/bin/env python3
"""Probe the modded-nanogpt README for new records; vendor and vet open claims.

Run: python3 problems/algorithms-nanogpt/fetch.py

Accepted records are transcribed by hand: each row carries the agent and the
credited AI system, which the README states in prose that needs judgment to
attribute. For those this script is a staleness probe — it reports, and exits
NEEDS_PERSON, when the README lists a record past the vendored series.

Open claims it does vendor. An entrant opens a pull request naming a time
("New Record: 0.665 minutes (39.9 seconds)", "9.65 s?? ...", "(40.0s →
21.56s)") before the maintainer reproduces it. Every open Track 1 pull request
whose title claims a time below the standing record, opened on or before
lib/dates.py's AS_OF_DATE, becomes a row: ``record`` is ``PR<number>``,
``date`` the day it was opened, ``minutes`` the claimed time, ``agent`` and
``ai_system`` empty because attribution waits for acceptance.

Which kind of row depends on whether the claim meets the bar the leaderboard
itself sets for acceptance, read from the files the pull request adds:

1. evidence: a statistics or README file under records/track_1_short/ states
   a p-value below 0.01 that mean validation loss is at most 3.28 (rule 2);
2. hardware: that file names 8xH100 runs, and the title does not say the
   result still needs validating there;
3. baseline: a baseline/ file names a merged record ("record #92"), not an
   open pull request ("PR #367") — a time measured against an unaccepted
   stack is not a step below the standing record (rule 4);
4. review: no reviewer's latest review requests changes.

A claim that passes all four is ``kind=pending``; one that fails any is
``kind=claim``, with what it failed in ``note``. The size of the claimed step
is deliberately not a test: record #92 cut the time by 46% and was accepted.
Rows of both kinds are machine-owned: a claim that is merged becomes a
hand-transcribed record, one that is closed disappears, and the next run
rewrites the set either way. Nothing counts either kind as a record — not the
fact lines, not the figures — but the comparison page's tentative view draws
the pending rows, which is what they are for.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.dates import AS_OF_DATE  # noqa: E402
from lib.table import read_csv, write_csv  # noqa: E402
from lib.web import NEEDS_PERSON, fetch, fetch_json  # noqa: E402

URL = ("https://raw.githubusercontent.com/KellerJordan/modded-nanogpt/"
       "master/README.md")
API = "https://api.github.com/repos/KellerJordan/modded-nanogpt"
PULLS = f"{API}/pulls?state=open&per_page=100"
GITHUB_JSON = "application/vnd.github+json"
CSV = HERE / "nanogpt-records.csv"
FIELDS = ["record", "kind", "date", "minutes", "agent", "ai_system", "note"]
MACHINE_KINDS = ("pending", "claim")

# A time in a title: "0.665 minutes", "1.167 min", "39.9 seconds", "21.56s",
# "9.65 s??". A number signed + or - is a delta ("-34.0s"), not a time, and
# "3250 steps" is a step count. The smallest time in the title is the claim:
# "(40.0s → 21.56s)" names the old time first.
TIME = re.compile(r"(?i)(?<![\d.+\-−])(\d+(?:\.\d+)?)\s*"
                  r"(min(?:ute)?s?|s(?:ec(?:ond)?s?)?)(?![a-z])")
OTHER_TRACK = re.compile(r"(?i)\btrack[\s_-]*[23]\b|\bmedium\b")
UNVALIDATED = re.compile(r"(?i)needs? validation")
P_VALUE = 0.01


def claimed_minutes(title: str) -> float | None:
    times = [float(n) / (60 if unit.lower().startswith("s") else 1)
             for n, unit in TIME.findall(title)]
    # Rounded to the leaderboard's own precision, so "39.9 seconds" is the
    # 0.665 minutes it restates rather than a hair below it.
    return round(min(times), 3) if times else None


def added_record_files(pull: dict) -> dict[str, str]:
    """The text of every statistics/README file the PR adds under records/."""
    files, page = [], 1
    while True:
        batch = fetch_json(f"{API}/pulls/{pull['number']}/files?per_page=100&page={page}",
                           refresh=True, accept=GITHUB_JSON)
        files += batch
        if len(batch) < 100:
            break
        page += 1
    head = f"https://raw.githubusercontent.com/{pull['head']['repo']['full_name']}/{pull['head']['sha']}/"
    return {f["filename"]: fetch(head + f["filename"], refresh=True).decode("utf-8", "replace")
            for f in files
            if f["filename"].startswith("records/track_1_short/")
            and f["filename"].lower().endswith(("statistics.md", "readme.md"))
            and f["status"] != "removed"}


def p_values(text: str) -> list[float]:
    """p-values stated against the 3.28 gate: a table row's last cell, or "p = x"."""
    found = []
    for line in text.splitlines():
        if "3.28" not in line or not re.search(r"(?i)\bp\b|p-value", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and len(cells) > 1:
            match = re.fullmatch(r"<?\s*(\d+(?:\.\d+)?(?:e-?\d+)?)", cells[-1])
        else:
            match = re.search(r"(?i)\bp\s*[=<]\s*(\d+(?:\.\d+)?(?:e-?\d+)?)", line)
        if match:
            found.append(float(match.group(1)))
    return found


def shortfalls(pull: dict) -> list[str]:
    """Which of the four acceptance tests the claim fails; empty if none."""
    files = added_record_files(pull)
    ours = {k: v for k, v in files.items() if "/baseline/" not in k}
    baselines = [v for k, v in files.items() if "/baseline/" in k]
    failed = []
    if not any(p < P_VALUE for text in ours.values() for p in p_values(text)):
        failed.append("no p<0.01 against the 3.28 gate in its record files")
    if UNVALIDATED.search(pull["title"]) or not any(
            re.search(r"(?i)8\s*x\s*H100", text) for text in ours.values()):
        failed.append("no 8xH100 runs")
    heads = [text.lstrip().splitlines()[0] for text in baselines if text.strip()]
    if any(re.search(r"(?i)\bPR\s*#\d+", head) for head in heads):
        failed.append("baseline is an open pull request, not a merged record")
    elif not any(re.search(r"(?i)\brecord\s*#\d+", head) for head in heads):
        failed.append("no same-hardware baseline of a merged record")
    reviews = fetch_json(f"{API}/pulls/{pull['number']}/reviews?per_page=100",
                         refresh=True, accept=GITHUB_JSON)
    latest = {}
    for review in reviews:
        if review["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[review["user"]["login"]] = review["state"]
    if "CHANGES_REQUESTED" in latest.values():
        failed.append("a reviewer requested changes")
    return failed


def claim_rows(standing: float) -> list[dict[str, str]]:
    """Open Track 1 pull requests claiming a time below the standing record."""
    pulls = fetch_json(PULLS, refresh=True, accept=GITHUB_JSON)
    rows = []
    for pull in pulls:
        minutes = claimed_minutes(pull["title"])
        opened = pull["created_at"][:10]
        if (minutes is None or minutes >= standing or OTHER_TRACK.search(pull["title"])
                or date.fromisoformat(opened) > AS_OF_DATE):
            continue
        failed = shortfalls(pull)
        note = f"open pull request #{pull['number']}: {pull['title']}"
        if failed:
            note += " — not vetted: " + "; ".join(failed)
        rows.append({
            "record": f"PR{pull['number']}", "kind": "claim" if failed else "pending",
            "date": opened, "minutes": f"{minutes:.4g}", "agent": "", "ai_system": "",
            "note": note,
        })
    return sorted(rows, key=lambda row: (row["date"], row["record"]))


def probe(records: list[dict[str, str]]) -> str | None:
    """Report when the README lists an accepted record past the vendored ones."""
    last_n = int(records[-1]["record"]) if records else 0
    last_minutes = records[-1]["minutes"] if records else "?"
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    # Record rows look like: "86 | 1.266 minutes | <description> | 05/27/26 | ..."
    rows = re.findall(r"(?m)^(\d+) \| ([\d.]+) minutes \|", text)
    if not rows:
        return ("nanogpt-records.csv: no record-table rows parsed from the "
                "README — its format changed; check by hand")
    newest_n, newest_minutes = max((int(n), m) for n, m in rows)
    if newest_n > last_n:
        return (f"nanogpt-records.csv: README now has record {newest_n} at "
                f"{newest_minutes} min; vendored series ends at record {last_n} "
                f"({last_minutes} min) — update the CSV and this folder's "
                "README.md by hand (authorship needs judgment)")
    return None


def main() -> int:
    vendored = read_csv(CSV)
    kept = [row for row in vendored if row["kind"] not in MACHINE_KINDS]
    records = [row for row in kept if row["kind"] == "record"]
    standing = float(records[-1]["minutes"]) if records else float("inf")

    claims = claim_rows(standing)
    before = [row for row in vendored if row["kind"] in MACHINE_KINDS]
    vetted = sum(1 for row in claims if row["kind"] == "pending")
    if claims != before:
        write_csv(CSV, kept + claims, FIELDS)
        print(f"wrote {CSV.name}: {len(claims)} open claim(s), {vetted} vetted "
              f"({len(before)} before)")
    else:
        print(f"{CSV.name}: {len(claims)} open claim(s), {vetted} vetted, unchanged")
    for row in claims:
        print(f"  {row['record']} {row['date']} {row['minutes']} min {row['kind']}")

    message = probe(records)
    if message:
        print(f"⚠️  {message}")
        return NEEDS_PERSON
    print("nanogpt-records.csv: README lists no record past the vendored series")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
