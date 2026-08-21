#!/usr/bin/env python3
"""Rebuild this folder's four CSVs from Microsoft's Security Update Guide API.

Run: python3 problems/cyber-microsoft/fetch.py

MSRC publishes one CVRF document per monthly release ("Patch Tuesday") at
https://api.msrc.microsoft.com/cvrf/v3.0/, from January 2016 onward. Each
document lists every vulnerability entry in that release with acknowledgments
against most of them, which makes Microsoft a fixed (if enormous) vendor whose
finders are usually named.

The counting rule is stricter than the raw documents, because a monthly
document also republishes CVEs Microsoft did not author: Chromium fixes shipped
through Edge, and from 2023 the Linux CVEs of Azure Linux (CBL-Mariner). Each
entry carries a note naming the issuing CNA, so the rule is: count an entry
when its CNA note says Microsoft, or when it has no CNA note at all, which is
the pre-2018 document format. Everything excluded by that rule in the vendored
data is verifiably third-party (Chromium, Linux distributions, curl, vim, and
so on). Non-CVE advisory IDs (ADV..., "Mariner" rows) are skipped.

A CVE is dated by the earliest revision in its history, across every document
that mentions it, so an out-of-band fix released late in a month lands in the
month it actually shipped rather than the document it was filed under.
Documents released after lib/dates.py's AS_OF_DATE are skipped, and so are
entries first published after it: the vendored CSVs are a snapshot as of that
date, and a refetch after the date is bumped picks the newer releases up.

AI attribution is by explicit marker in the acknowledgment strings (see
lib/credits.py), which separates a named AI method from a bare AI-company
affiliation and carries error in both directions. Acknowledgment strings can
contain HTML links and anonymized hex handles; tags are stripped and handles
kept, since an anonymous credit is still a credit. A handful of upstream
strings carry unmatched parentheses — typos in MSRC's own text, verified
against the raw API — and the unmatched characters are dropped so the shared
split-credit check flags real parser damage rather than upstream typos.
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import Signals, signals  # noqa: E402
from lib.dates import AS_OF_DATE  # noqa: E402
from lib.table import write_csv  # noqa: E402
from lib.web import fetch_json  # noqa: E402

API = "https://api.msrc.microsoft.com/cvrf/v3.0"
JSON = "application/json"

TAGS = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")


def monthly_documents(cutoff: date) -> list[str]:
    """IDs of every monthly security-update document released by the cutoff.

    Matched on the document title, not the ID, because the IDs are irregular:
    February 2018 is "2018-FEB" and an out-of-band May 2017 release is
    "2017-May-B".
    """
    index = fetch_json(f"{API}/updates", accept=JSON)
    docs = [
        update["ID"]
        for update in index["value"]
        if "Security Updates" in (update.get("DocumentTitle") or "")
        and (update.get("InitialReleaseDate") or "9999")[:10] <= cutoff.isoformat()
    ]
    return sorted(docs)


def cna(entry: dict) -> str | None:
    """The issuing CNA named in the entry's type-8 note, if any."""
    for note in entry.get("Notes") or []:
        if note.get("Type") == 8:
            return note.get("Title")
    return None


def balance(text: str) -> str:
    """Drop unmatched parentheses, keeping everything else verbatim."""
    kept = []
    depth = 0
    for character in text:
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                continue
            depth -= 1
        kept.append(character)
    while depth:
        depth -= 1
        del kept[len(kept) - 1 - kept[::-1].index("(")]
    return "".join(kept)


def credits(entry: dict) -> list[str]:
    """One cleaned string per acknowledgment, HTML stripped."""
    out = []
    for acknowledgment in entry.get("Acknowledgments") or []:
        names = [
            name.get("Value") or ""
            for name in acknowledgment.get("Name") or []
        ]
        text = balance(TAGS.sub(" ", html.unescape(" ".join(names))))
        text = SPACE.sub(" ", text).strip()
        if text:
            out.append(text)
    return out


def records(cutoff: date) -> dict[str, dict]:
    """One record per Microsoft-issued CVE, dated by its earliest revision."""
    cves: dict[str, dict] = {}
    documents = monthly_documents(cutoff)
    for doc_id in documents:
        document = fetch_json(f"{API}/cvrf/{doc_id}", accept=JSON)
        for entry in document.get("Vulnerability") or []:
            cve = entry.get("CVE") or ""
            if not cve.startswith("CVE-"):
                continue
            issuer = cna(entry)
            if issuer is not None and issuer != "Microsoft":
                continue
            title = (entry.get("Title") or {}).get("Value") or ""
            if title.startswith("Chromium:"):
                continue
            dates = [
                revision["Date"][:10]
                for revision in entry.get("RevisionHistory") or []
                if revision.get("Date")
            ]
            if not dates:
                continue
            initial = min(dates)
            record = cves.setdefault(
                cve, {"initial": initial, "credits": [], "no_action": False}
            )
            record["initial"] = min(record["initial"], initial)
            for credit in credits(entry):
                if credit not in record["credits"]:
                    record["credits"].append(credit)
            for note in entry.get("Notes") or []:
                if (note.get("Type") == 6
                        and note.get("Title") == "Customer Action Required"
                        and TAGS.sub("", note.get("Value") or "").strip() == "No"):
                    record["no_action"] = True
    kept = {
        cve: record
        for cve, record in cves.items()
        if record["initial"] <= cutoff.isoformat()
    }
    print(
        f"msrc: {len(documents)} monthly documents, {len(kept)} Microsoft-issued "
        f"CVEs through {cutoff.isoformat()} ({len(cves) - len(kept)} past the "
        "snapshot date dropped)"
    )
    return kept


def build_annual(cves: dict[str, dict], cutoff: date) -> list[dict]:
    """Annual counts of CVEs by band, with acknowledgment coverage alongside.

    A CVE's signals are unioned across all its credit strings before the
    display precedence picks its band, mirroring the Firefox series. The
    no_customer_action column counts the cloud-service CVEs Microsoft patches
    itself, which exist as a category only from 2024.
    """
    per_year: dict[int, Counter] = defaultdict(Counter)
    latest = ""
    ai_credits: Counter = Counter()
    for record in cves.values():
        year = int(record["initial"][:4])
        latest = max(latest, record["initial"])
        marks = Signals(explicit_ai=False, ai_affiliated=False, fuzz=False)
        for credit in record["credits"]:
            found = signals(credit, year)
            marks = Signals(
                explicit_ai=marks.explicit_ai or found.explicit_ai,
                ai_affiliated=marks.ai_affiliated or found.ai_affiliated,
                fuzz=marks.fuzz or found.fuzz,
            )
            if found.any_ai_marker:
                ai_credits[f"{year} {credit[:80]}"] += 1
        bucket = per_year[year]
        bucket["cves"] += 1
        bucket[marks.band] += 1
        if record["credits"]:
            bucket["acknowledged"] += 1
        if record["no_action"]:
            bucket["no_customer_action"] += 1
    annual = [
        {
            "year": year,
            "cves": per_year[year]["cves"],
            "explicit_ai": per_year[year]["explicit_ai"],
            "ai_affiliated": per_year[year]["ai_affiliated"],
            "fuzz": per_year[year]["fuzz"],
            "other": per_year[year]["other"],
            "acknowledged": per_year[year]["acknowledged"],
            "no_customer_action": per_year[year]["no_customer_action"],
            "partial_year": "yes" if year == cutoff.year else "no",
            "data_through": latest if year == cutoff.year else "",
        }
        for year in sorted(per_year)
    ]
    print(
        f"msrc: {sum(row['cves'] for row in annual)} CVEs, "
        f"{annual[0]['year']}–{annual[-1]['year']}, latest {latest}"
    )
    for line, count in sorted(ai_credits.items()):
        print(f"  AI-marked: {count}x {line}")
    return annual


def build_monthly(cves: dict[str, dict]) -> list[dict]:
    """CVEs per month by band, the release's native cadence.

    Patch Tuesday is a monthly ritual, and the record releases the documents
    describe — June and July 2026 — are monthly facts an annual bar hides.
    Bands use the same union-then-precedence rule as build_annual, so a month
    column sums to the same CVEs its year's row counts.
    """
    per_month: dict[str, Counter] = defaultdict(Counter)
    for record in cves.values():
        month = record["initial"][:7]
        year = int(record["initial"][:4])
        marks = Signals(explicit_ai=False, ai_affiliated=False, fuzz=False)
        for credit in record["credits"]:
            found = signals(credit, year)
            marks = Signals(
                explicit_ai=marks.explicit_ai or found.explicit_ai,
                ai_affiliated=marks.ai_affiliated or found.ai_affiliated,
                fuzz=marks.fuzz or found.fuzz,
            )
        per_month[month]["cves"] += 1
        per_month[month][marks.band] += 1
    return [
        {
            "month": month,
            "cves": per_month[month]["cves"],
            "explicit_ai": per_month[month]["explicit_ai"],
            "ai_affiliated": per_month[month]["ai_affiliated"],
            "fuzz": per_month[month]["fuzz"],
            "other": per_month[month]["other"],
        }
        for month in sorted(per_month)
    ]


def build_ai_cves(cves: dict[str, dict]) -> list[dict]:
    """One row per AI-marked CVE, with every credit string kept as evidence.

    Small enough to read in full, and the only place the per-team claims in the
    document can be recomputed from, because the annual counts collapse CVEs
    into bands.
    """
    rows = []
    for cve, record in sorted(cves.items(), key=lambda item: item[1]["initial"]):
        year = int(record["initial"][:4])
        marks = [signals(credit, year) for credit in record["credits"]]
        if not any(mark.any_ai_marker for mark in marks):
            continue
        band = ("explicit_ai" if any(m.explicit_ai for m in marks)
                else "ai_affiliated")
        rows.append({
            "cve": cve,
            "date": record["initial"],
            "band": band,
            "credits": " | ".join(record["credits"]),
        })
    print(f"msrc AI-marked CVEs: {len(rows)}")
    return rows


def build_finders(cves: dict[str, dict]) -> list[dict]:
    """One row per credit string per year.

    Credit strings stay verbatim, the multi-person ones included, because
    splitting them on commas would invent individual attributions.
    """
    counted: dict[tuple, int] = defaultdict(int)
    for record in cves.values():
        year = int(record["initial"][:4])
        for credit in record["credits"]:
            counted[(year, credit, signals(credit, year).band)] += 1
    out = [
        {"year": year, "finder": finder, "category": category, "cves": count}
        for (year, finder, category), count in sorted(
            counted.items(), key=lambda item: (item[0][0], -item[1])
        )
    ]
    ai = [row for row in out if row["category"] in ("explicit_ai", "ai_affiliated")]
    print(f"msrc finders: {len(out)} year-finder rows, {len(ai)} AI-marked")
    return out


def main() -> None:
    cutoff = AS_OF_DATE
    cves = records(cutoff)
    write_csv(HERE / "msrc-cves.csv", build_annual(cves, cutoff))
    write_csv(HERE / "msrc-monthly.csv", build_monthly(cves))
    write_csv(HERE / "msrc-finders.csv", build_finders(cves))
    write_csv(HERE / "msrc-ai-cves.csv", build_ai_cves(cves))


if __name__ == "__main__":
    main()
