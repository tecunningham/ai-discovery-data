#!/usr/bin/env python3
"""Rebuild this folder's CSVs from Mozilla's security-advisory repository.

Run: python3 problems/cyber-firefox/fetch.py

Mozilla publishes one YAML file per advisory under announce/, with a `reporter`
string and an `impact` rating against each CVE, which makes Firefox a fixed
codebase with named finders and a native severity scale. Counts are by the
advisory's `announced` year. Pre-2016 advisories do not list CVEs in this
structure, so the series starts there. Four views come out of the repository:
one row per distinct CVE (the granular ledger the others summarize), quarterly
counts split by credit band, annual counts split by credit, and one row per
reporter per year. Advisories announced after lib/chart.py's AS_OF_DATE are
skipped, so a refetch reproduces the committed window.

The plotted unit is the distinct CVE. Mozilla repeats one CVE across the Firefox,
Firefox ESR and Thunderbird advisories of a release, so a mention count moves
with Mozilla's packaging as well as with discovery; mention counts are kept as a
sensitivity column rather than as the headline.

AI attribution is by explicit marker in the reporter string (see lib/credits.py),
which separates a named AI method from a bare AI-company affiliation and carries
error in both directions. Fuzz is an independent signal, not a rival category.

Requires PyYAML.
"""

from __future__ import annotations

import io
import re
import sys
import tarfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.credits import Signals, band, classify, signals  # noqa: E402
from lib.table import write_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

# Mozilla's own scale, mildest first. Advisories rate each CVE (or, on older
# files, the advisory as a whole); a CVE mentioned at several impacts keeps the
# most severe, and one with no parseable rating is counted as unrated rather
# than dropped.
IMPACTS = ["Low", "Moderate", "High", "Critical"]


def as_of_date() -> date:
    """The repository's committed snapshot date, read from lib/chart.py.

    Parsed rather than imported so a fetch does not pull in matplotlib; the
    same regex tools/check.py uses to enforce the date against every CSV.
    """
    text = (HERE.parents[1] / "lib/chart.py").read_text(encoding="utf-8")
    match = re.search(
        r"^AS_OF_DATE\s*=\s*date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)", text, re.M
    )
    if not match:
        raise SystemExit("lib/chart.py has no parseable AS_OF_DATE")
    return date(*(int(part) for part in match.groups()))


def normalize_impact(value: str) -> str:
    cleaned = str(value or "").strip().capitalize()
    return cleaned if cleaned in IMPACTS else "Unrated"


def impact_rank(value: str) -> int:
    """Position on Mozilla's scale; Unrated sorts below every real rating."""
    return IMPACTS.index(value) if value in IMPACTS else -1

# codeload's /tar.gz/<branch> form 404s for this repo; the archive URL works.
URL = (
    "https://github.com/mozilla/foundation-security-advisories/"
    "archive/refs/heads/master.tar.gz"
)


def records() -> list[dict]:
    """One record per CVE named in an advisory, carrying its year and reporter."""
    import yaml

    rows = []
    with tarfile.open(fileobj=io.BytesIO(fetch(URL)), mode="r:gz") as tar:
        for member in tar.getmembers():
            if "/announce/" not in member.name or not member.name.endswith(".yml"):
                continue
            handle = tar.extractfile(member)
            if handle is None:
                continue
            text = handle.read().decode("utf-8", "replace")
            # No re.S: the year must come from the announced line itself, not
            # from whatever four-digit number happens to follow in the file.
            announced = re.search(r"^announced:[^\n]*?(20\d{2})", text, re.M)
            if announced:
                year = int(announced.group(1))
            else:
                fallback = re.search(r"mfsa(20\d{2})", member.name)
                if not fallback:
                    continue
                year = int(fallback.group(1))
            try:
                parsed = yaml.safe_load(text) or {}
            except Exception:
                continue
            announced_text = str(parsed.get("announced") or "")
            # A few advisories write ordinals — "December 15th, 2025" — which
            # strptime's %d does not accept.
            plain = re.sub(r"(\d{1,2})(st|nd|rd|th)\b", r"\1", announced_text)
            try:
                announced_date = datetime.strptime(
                    plain, "%B %d, %Y"
                ).date().isoformat()
            except ValueError:
                announced_date = ""
                if announced_text:
                    # The dated maximum decides data_through, so a format this
                    # parser does not know must be said out loud, not dropped.
                    print(f"  unparseable announced date {announced_text!r} "
                          f"in {member.name}")
            advisory_impact = str(parsed.get("impact") or "")
            for key, value in (parsed.get("advisories") or {}).items():
                if not str(key).startswith("CVE"):
                    continue
                reporter = (
                    str(value.get("reporter", "")) if isinstance(value, dict) else ""
                )
                impact = (
                    str(value.get("impact", "")) if isinstance(value, dict) else ""
                )
                rows.append({
                    "year": year,
                    "announced": announced_date,
                    "cve": str(key),
                    "reporter": reporter,
                    "impact": normalize_impact(impact or advisory_impact),
                })
    cutoff = as_of_date()
    kept = [row for row in rows
            if (row["announced"] <= cutoff.isoformat() if row["announced"]
                else row["year"] <= cutoff.year)]
    if len(kept) != len(rows):
        print(f"  {len(rows) - len(kept)} advisory-CVE mentions announced "
              f"after {cutoff.isoformat()} dropped (snapshot cap)")
    return kept


def build_cves(rows: list[dict]) -> list[dict]:
    """One row per distinct CVE per year: the ledger the aggregates summarize.

    Signals are unioned across a year's mentions before the band precedence is
    applied, exactly as build_annual counts them, so summing this file by year
    and band reproduces the annual unique columns. The impact keeps the most
    severe rating any mention carries, and the date is the earliest
    announcement, which is where the quarterly view places the CVE.
    """
    merged: dict[tuple[int, str], dict] = {}
    for record in rows:
        key = (record["year"], record["cve"])
        entry = merged.setdefault(key, {
            "date": record["announced"],
            "impact": record["impact"],
            "signals": Signals(False, False, False),
            "reporters": [],
        })
        if record["announced"]:
            entry["date"] = (min(entry["date"], record["announced"])
                             if entry["date"] else record["announced"])
        if impact_rank(record["impact"]) > impact_rank(entry["impact"]):
            entry["impact"] = record["impact"]
        marks = signals(record["reporter"], record["year"])
        entry["signals"] = Signals(
            explicit_ai=entry["signals"].explicit_ai or marks.explicit_ai,
            ai_affiliated=entry["signals"].ai_affiliated or marks.ai_affiliated,
            fuzz=entry["signals"].fuzz or marks.fuzz,
        )
        reporter = record["reporter"].strip()
        if reporter and reporter not in entry["reporters"]:
            entry["reporters"].append(reporter)
    out = [
        {
            "cve": cve,
            "year": year,
            "quarter": (f"{entry['date'][:4]}-Q{(int(entry['date'][5:7]) + 2) // 3}"
                        if entry["date"] else ""),
            "date": entry["date"],
            "impact": entry["impact"],
            "band": entry["signals"].band,
            "reporters": " | ".join(entry["reporters"]),
        }
        for (year, cve), entry in sorted(
            merged.items(), key=lambda item: (item[1]["date"] or f"{item[0][0]}",
                                              item[0][1])
        )
    ]
    rated = sum(row["impact"] != "Unrated" for row in out)
    print(f"firefox CVE ledger: {len(out)} rows, {rated} carrying an impact "
          f"rating, {sum(not row['date'] for row in out)} without a parseable "
          "date")
    return out


def build_quarterly(cve_rows: list[dict]) -> list[dict]:
    """Distinct CVEs per quarter by band, from the per-CVE ledger.

    Rows without a parseable announcement date cannot be placed in a quarter
    and are dropped here (they stay in the annual counts); build_cves prints
    how many there are, so a quarterly total short of its year's is a stated
    fact rather than a silent loss.
    """
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for row in cve_rows:
        if not row["quarter"]:
            continue
        bucket = per_quarter[row["quarter"]]
        bucket["unique_cves"] += 1
        bucket[row["band"]] += 1
    latest = max((row["date"] for row in cve_rows if row["date"]), default="")
    last_quarter = max(per_quarter) if per_quarter else ""
    return [
        {
            "quarter": quarter,
            "unique_cves": per_quarter[quarter]["unique_cves"],
            "explicit_ai": per_quarter[quarter]["explicit_ai"],
            "ai_affiliated": per_quarter[quarter]["ai_affiliated"],
            "fuzz": per_quarter[quarter]["fuzz"],
            "other": per_quarter[quarter]["other"],
            "partial_quarter": "yes" if quarter == last_quarter else "no",
            "data_through": latest if quarter == last_quarter else "",
        }
        for quarter in sorted(per_quarter)
    ]


def build_annual(rows: list[dict]) -> list[dict]:
    """Annual counts of distinct CVEs by band, with mention counts alongside.

    A CVE repeated across a release's advisories is one discovery, so the band
    columns count distinct CVE IDs. Where the same CVE carries different reporter
    strings in different advisories, its signals are unioned across that year's
    mentions before the display precedence is applied — otherwise which advisory
    happened to be read last would decide the band.
    """
    per_year: dict[int, Counter] = defaultdict(Counter)
    unique_cves: dict[int, set[str]] = defaultdict(set)
    unique_ai_cves: dict[int, set[str]] = defaultdict(set)
    cve_signals: dict[tuple[int, str], Signals] = {}
    ai_reporters: Counter = Counter()
    for record in rows:
        year = record["year"]
        bucket = per_year[year]
        bucket["total"] += 1
        unique_cves[year].add(record["cve"])
        marks = signals(record["reporter"], year)
        key = (year, record["cve"])
        seen = cve_signals.get(key)
        cve_signals[key] = marks if seen is None else Signals(
            explicit_ai=seen.explicit_ai or marks.explicit_ai,
            ai_affiliated=seen.ai_affiliated or marks.ai_affiliated,
            fuzz=seen.fuzz or marks.fuzz,
        )
        bucket[f"mention_{marks.band}"] += 1
        category = classify(record["reporter"], year)
        bucket[f"{category}_attributed"] += 1
        if category == "ai":
            ai_reporters[record["reporter"][:90]] += 1
            unique_ai_cves[year].add(record["cve"])
    unique_bands: dict[int, Counter] = defaultdict(Counter)
    for (year, _cve), marks in cve_signals.items():
        unique_bands[year][marks.band] += 1
    this_year = datetime.now(timezone.utc).year
    latest = max(
        (record["announced"] for record in rows if record["announced"]),
        default="",
    )
    annual = [
        {
            "year": year,
            "unique_cves": len(unique_cves[year]),
            "unique_explicit_ai": unique_bands[year]["explicit_ai"],
            "unique_ai_affiliated": unique_bands[year]["ai_affiliated"],
            "unique_fuzz": unique_bands[year]["fuzz"],
            "unique_other": unique_bands[year]["other"],
            "total": per_year[year]["total"],
            "mentions_explicit_ai": per_year[year]["mention_explicit_ai"],
            "mentions_ai_affiliated": per_year[year]["mention_ai_affiliated"],
            "mentions_fuzz": per_year[year]["mention_fuzz"],
            "mentions_other": per_year[year]["mention_other"],
            "ai_attributed": per_year[year]["ai_attributed"],
            "unique_ai_cves": len(unique_ai_cves[year]),
            "fuzz_attributed": per_year[year]["fuzz_attributed"],
            "other_attributed": per_year[year]["other_attributed"],
            "partial_year": "yes" if year == this_year else "no",
            "data_through": latest if year == this_year else "",
        }
        for year in sorted(per_year)
        if per_year[year]["total"]
    ]
    print(
        f"firefox: {sum(r['unique_cves'] for r in annual)} distinct CVEs across "
        f"{sum(r['total'] for r in annual)} advisory-CVE mentions, "
        f"{annual[0]['year']}–{annual[-1]['year']}"
    )
    print(
        "  AI-attributed reporter strings: "
        + "; ".join(f"{c}x {n[:52]}" for n, c in ai_reporters.most_common(4))
    )
    return annual


def build_finders(rows: list[dict]) -> list[dict]:
    """One row per reporter per year.

    Reporter strings stay verbatim, the multi-person ones included, because
    splitting them on commas would invent individual attributions.
    """
    counted: dict[tuple, int] = defaultdict(int)
    for record in rows:
        finder = record["reporter"].strip()
        if finder:
            counted[
                (record["year"], finder, band(finder, record["year"]))
            ] += 1
    out = [
        {"year": year, "finder": finder, "category": category, "cves": count}
        for (year, finder, category), count in sorted(
            # The finder name breaks count ties: without it the order of tied
            # rows follows the tarball's member order, and a refetch reshuffles
            # rows that did not change.
            counted.items(), key=lambda item: (item[0][0], -item[1], item[0][1])
        )
    ]
    ai = [row for row in out if row["category"] in ("explicit_ai", "ai_affiliated")]
    explicit = [row for row in ai if row["category"] == "explicit_ai"]
    print(f"firefox finders: {len(out)} year-finder rows, {len(ai)} AI-marked "
          f"({len(explicit)} naming a method)")
    if ai:
        top = max(ai, key=lambda row: row["cves"])
        print(f"  top AI finder {top['cves']} advisory-CVE mentions — "
              f"{top['finder'][:56]}")
    return out


def build_ai_cves(rows: list[dict]) -> list[dict]:
    """One row per distinct AI-marked CVE per year, with its credit strings.

    The annual file counts the bands and the finders file counts mentions per
    reporter string; neither says which CVEs the AI bands actually are, so the
    per-team claims in the document were unfalsifiable from vendored data.
    This table closes that, the same role msrc-ai-cves.csv plays for Microsoft.
    """
    marks: dict[tuple[int, str], Signals] = {}
    reporters: dict[tuple[int, str], list[str]] = defaultdict(list)
    for record in rows:
        key = (record["year"], record["cve"])
        found = signals(record["reporter"], record["year"])
        seen = marks.get(key)
        marks[key] = found if seen is None else Signals(
            explicit_ai=seen.explicit_ai or found.explicit_ai,
            ai_affiliated=seen.ai_affiliated or found.ai_affiliated,
            fuzz=seen.fuzz or found.fuzz,
        )
        reporter = record["reporter"].strip()
        if reporter and reporter not in reporters[key]:
            reporters[key].append(reporter)
    out = [
        {"year": year, "cve": cve,
         "band": "explicit_ai" if marked.explicit_ai else "ai_affiliated",
         "reporters": " | ".join(reporters[year, cve])}
        for (year, cve), marked in sorted(marks.items())
        if marked.explicit_ai or marked.ai_affiliated
    ]
    print(f"firefox AI-marked distinct CVEs: {len(out)} rows")
    return out


def main() -> None:
    rows = records()
    cve_rows = build_cves(rows)
    write_csv(HERE / "firefox-cves.csv", cve_rows)
    write_csv(HERE / "firefox-quarterly.csv", build_quarterly(cve_rows))
    write_csv(HERE / "firefox-advisories.csv", build_annual(rows))
    write_csv(HERE / "firefox-finders.csv", build_finders(rows))
    write_csv(HERE / "firefox-ai-cves.csv", build_ai_cves(rows))


if __name__ == "__main__":
    main()
