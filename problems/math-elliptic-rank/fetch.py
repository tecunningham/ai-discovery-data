#!/usr/bin/env python3
"""Rebuild this folder's three CSVs from their two upstreams.

Run: python3 problems/math-elliptic-rank/fetch.py

Two upstreams, two different things:

* Dujella's rank-records pages carry the frontier itself — the record rank over
  time — as a fixed-width table inside a <pre> block, with one subpage per
  record holding the curve and its independent points. Both the lower-bound
  frontier and the exactly-known frontier are read from there.
* The ICARM Elliptic Curve Rank Leaderboard publishes every submitted curve at
  /database.json, with exact integers as strings, a submitter and a timestamp.
  That is the certificate layer: each row's rank bound was proved by the site's
  2-descent check before it was recorded.

The credit column is not upstream. Neither source records whether a record was
found with an AI, so CREDITS below is the hand-reviewed part of this folder and
the only place a credit is decided; the evidence backing each entry is quoted in
the document's AI-attribution register.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402
from lib.web import fetch, fetch_json  # noqa: E402

DUJELLA = "https://web.math.pmf.unizg.hr/~duje/tors/rankhist.html"
DUJELLA_BASE = "https://web.math.pmf.unizg.hr/~duje/tors/"
LEADERBOARD = "https://elliptic-rank.icarm.cloud/database.json"

# rank -> (credit, credit_evidence, note). Absent ranks default to human /
# published: every record before 2026 is a paper, a listserver post or a
# personal communication recorded by Dujella, none of which names an AI.
#
# The 2026 row is credited ai on a self-report and is marked as such. The rank
# bound does not depend on that credit — the leaderboard's 2-descent
# certificate proves rank >= 30 from the 30 witness points whoever found them —
# but the attribution rests on one editable commentary field written by a
# pseudonymous account, so it is recorded as self-reported rather than
# published.
CREDITS = {
    30: ("ai", "self-reported",
         "Credited to Claude with Levent Alpoge and Ava Howell in the "
         "leaderboard commentary, edited by the submitting account; no paper "
         "or named-author statement as of 2026-08-20"),
}

# Dujella's table leaves the author column empty for the 2026 row; the record's
# own subpage carries it. Read every subpage rather than only the empty ones, so
# a transcription that drifts from the subpage shows up as a diff.
# Horizontal whitespace only: the 2026 row's author column is empty, and \s
# would run the match past the line break onto the table's closing rule.
RECORD_ROW = re.compile(
    r'<a href="(rk\d+\.html)">(\d+)</a>[^\S\n]+(\d{4})[^\S\n]*([^\n]*?)[^\S\n]*$',
    re.M)
SUBPAGE_CREDIT = re.compile(
    r'<p align=center>\s*(.*?)\s*(?:\((\d{4})\))?\s*</p>', re.I | re.S)
EXACT_LINK = re.compile(r'<a href="(rkeq(\d+)\.html)">')


def text_of(html: str) -> str:
    """Strip tags and collapse whitespace, for a fragment of Dujella's HTML."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", html)).strip()


def normalise_authors(raw: str) -> str:
    """Dujella writes joint credits as "Nagao - Kouya"; the collection en-dashes."""
    return re.sub(r"\s+-\s+", "–", text_of(raw))


def subpage(name: str) -> tuple[str, str]:
    """The (authors, year) line centred at the top of one record's subpage."""
    html = fetch(DUJELLA_BASE + name).decode("utf-8", "replace")
    match = SUBPAGE_CREDIT.search(html)
    if not match:
        raise SystemExit(f"{name}: no centred credit line")
    return normalise_authors(match.group(1)), (match.group(2) or "")


def rank_records(html: str) -> list[dict[str, str]]:
    """The lower-bound frontier: the <pre> table, one row per record rank."""
    block = re.search(r"<pre>(.*?)</pre>", html, re.S)
    if not block:
        raise SystemExit("rankhist.html has no <pre> table")
    rows = []
    for page, rank, year, tail in RECORD_ROW.findall(block.group(1)):
        authors, subpage_year = subpage(page)
        table_authors = normalise_authors(tail)
        if table_authors and table_authors != authors:
            print(f"    note: rank {rank} table says {table_authors!r}, "
                  f"subpage says {authors!r}; keeping the table's")
            authors = table_authors
        if subpage_year and subpage_year != year:
            raise SystemExit(f"rank {rank}: table year {year} but subpage "
                             f"year {subpage_year}")
        credit, evidence, note = CREDITS.get(int(rank),
                                             ("human", "published", ""))
        rows.append({
            "year": year,
            "rank": rank,
            "discoverer": authors,
            "credit": credit,
            "credit_evidence": evidence,
            "source_url": DUJELLA_BASE + page,
            "note": note,
        })
    rows.sort(key=lambda row: int(row["rank"]))
    return rows


def exact_records(html: str) -> list[dict[str, str]]:
    """The second frontier: the largest rank known exactly, not as a bound."""
    seen: dict[str, str] = {}
    for page, rank in EXACT_LINK.findall(html):
        seen[rank] = page
    rows = []
    for rank, page in seen.items():
        authors, year = subpage(page)
        if not year:
            raise SystemExit(f"{page}: centred line carries no year")
        rows.append({
            "year": year,
            "rank": rank,
            "discoverer": authors,
            "source_url": DUJELLA_BASE + page,
        })
    rows.sort(key=lambda row: int(row["rank"]))
    return rows


def leaderboard() -> list[dict[str, str]]:
    """Every curve on the ICARM board, with the sizes the board ranks them by.

    The conductor and discriminant are hundreds of digits long, so the vendored
    columns are their natural logs — the quantities the board actually plots —
    and the exact integers stay upstream. math.log takes an arbitrary-precision
    int without overflowing.
    """
    payload = fetch_json(LEADERBOARD)
    rows = []
    for curve in payload["curves"]:
        conductor = curve.get("conductor")
        rows.append({
            "curve_id": str(curve["id"]),
            "rank": str(curve["rank_lower_bound"]),
            "naive_height": f"{curve['naive_height']:.4f}",
            "faltings_height": f"{curve['faltings_height']:.4f}",
            "log_conductor": f"{math.log(int(conductor)):.4f}" if conductor else "",
            "log_discriminant": f"{math.log(abs(int(curve['discriminant']))):.4f}",
            "points": str(len(curve["points"])),
            "submitter": (curve["submitter"] or "").strip(),
            "date": (curve["created_at"] or "")[:10],
        })
    rows.sort(key=lambda row: int(row["curve_id"]))
    return rows


def main() -> None:
    html = fetch(DUJELLA).decode("utf-8", "replace")
    records = rank_records(html)
    write_csv(HERE / "elliptic-curve-rank-records.csv", records)
    write_csv(HERE / "elliptic-curve-rank-exact.csv", exact_records(html))
    write_csv(HERE / "elliptic-rank-leaderboard.csv", leaderboard())
    print(f"record frontier: rank >= {records[-1]['rank']} "
          f"({records[-1]['discoverer']}, {records[-1]['year']})")


if __name__ == "__main__":
    main()
