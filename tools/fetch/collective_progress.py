#!/usr/bin/env python3
"""Vendor two series of *collective* progress — the accumulated state of the art.

Writes data/curl-vulnerabilities.csv and
erdos-database-history.csv.

Why these two. Most AI evidence in this log measures model capability: how many
steps a model completes, what time horizon it reaches. Capability series cannot
answer whether AI changed the rate of progress, because they do not exist before
the models. What can answer it is a quantity measuring what humanity collectively
knows or has found, measured the same way before and after AI arrived. curl's
vulnerability history is that for cyber — a single codebase, tracked since 2000,
with every finder credited — and the Erdős database is a partial version of it
for math.

Both inputs are fetched live, so this is run by hand and its output vendored,
the same arrangement as the ANTEDB extraction.

    python3 tools/collective_progress.py

curl: https://curl.se/docs/vuln.json is the project's own OSV-format record of
every CVE, with `published`, `credits` naming finders, and a severity. The AI
attribution below is by explicit textual marker in a finder credit and is
therefore a *lower bound*: a researcher using a model without saying so is
counted as human.

Erdős: github.com/teorth/erdosproblems ships data/statistics_history.csv, a
per-commit snapshot of how many problems the database holds and how many are
recorded as solved. Note the confound, which is severe before April 2026: the
corpus was still being catalogued, so `solved` rose partly because
already-solved problems were being added. From 2026-04 the total is fixed at
1217, and after that a rise in `solved` is a genuine new resolution.
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_CURL = ROOT / "data/curl-vulnerabilities.csv"
OUT_ERDOS = ROOT / "data/erdos-database-history.csv"
OUT_NVD = ROOT / "data/nvd-kev-by-year.csv"
OUT_NVD_Q = ROOT / "data/nvd-kev-by-quarter.csv"
OUT_CURL_Q = ROOT / "data/curl-vulnerabilities-quarterly.csv"
OUT_FIREFOX = ROOT / "data/firefox-advisories.csv"
OUT_OSSFUZZ = ROOT / "data/ossfuzz-discoveries.csv"
OUT_OPENSSL = ROOT / "data/openssl-vulnerabilities.csv"
# Finder-level counts, because the concentration of AI-credited discovery in a
# few named people is the most load-bearing claim these series support and the
# year-aggregated files cannot evidence it.
OUT_FINDERS = ROOT / "data/discovery-finders.csv"

CURL_URL = "https://curl.se/docs/vuln.json"
ERDOS_URL = ("https://raw.githubusercontent.com/teorth/erdosproblems/"
             "main/data/statistics_history.csv")

# Explicit markers only. Every one of these names either contains "AI"/"agent",
# names a known AI vulnerability-finding system, or names a lab whose stated
# purpose is AI-driven code security. Anything else counts as human, so the
# resulting share understates AI involvement.
AI_MARKERS = re.compile(
    r"big sleep|mythos|openai|anthropic|antaisecuritylab|aisle research"
    r"|autonomous code security|xbow|zeropath|\bagent\b",
    re.I,
)
SEVERITIES = ["Low", "Medium", "High", "Critical"]


def fetch(url: str) -> bytes:
    result = subprocess.run(["curl", "-sL", "--max-time", "120", url],
                            capture_output=True)
    if result.returncode != 0 or not result.stdout:
        raise SystemExit(f"failed to fetch {url}")
    return result.stdout


def fetch_json(url: str, attempts: int = 6, base_delay: float = 8.0):
    """Fetch and parse JSON, retrying on the rate-limit responses NVD returns.

    Unkeyed NVD callers get 5 requests per 30 seconds and, when they exceed it,
    an HTML error page rather than a JSON error — so a bare json.loads fails
    with "Expecting value" and the whole run dies partway. Back off and retry.
    """
    import time

    last = ""
    for attempt in range(attempts):
        raw = fetch(url)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            last = raw[:120].decode("utf-8", "replace").replace("\n", " ")
            wait = base_delay * (attempt + 1)
            print(f"    non-JSON reply, retrying in {wait:.0f}s ({last[:60]}...)")
            time.sleep(wait)
    raise SystemExit(f"gave up on {url}: {last}")


def build_curl() -> list[dict]:
    entries = json.loads(fetch(CURL_URL))
    per_year: dict[int, Counter] = defaultdict(Counter)
    latest = ""
    for entry in entries:
        published = entry.get("published") or ""
        if not published[:4].isdigit():
            continue
        year = int(published[:4])
        latest = max(latest, published[:10])
        finders = [c["name"] for c in entry.get("credits", [])
                   if c.get("type") == "FINDER"]
        is_ai = any(AI_MARKERS.search(name) for name in finders)
        severity = (entry.get("database_specific") or {}).get("severity", "unknown")
        bucket = per_year[year]
        bucket["total"] += 1
        bucket["ai_attributed" if is_ai else "other_attributed"] += 1
        bucket[f"sev_{severity}"] += 1
        bucket[("ai_sev_" if is_ai else "other_sev_") + severity] += 1

    rows = []
    for year in sorted(per_year):
        bucket = per_year[year]
        row = {"year": year, "total": bucket["total"],
               "ai_attributed": bucket["ai_attributed"],
               "other_attributed": bucket["other_attributed"]}
        for severity in SEVERITIES:
            row[f"sev_{severity.lower()}"] = bucket[f"sev_{severity}"]
            row[f"ai_sev_{severity.lower()}"] = bucket[f"ai_sev_{severity}"]
            row[f"other_sev_{severity.lower()}"] = bucket[f"other_sev_{severity}"]
        row["partial_year"] = "yes" if year == int(latest[:4]) else "no"
        row["data_through"] = latest if year == int(latest[:4]) else ""
        rows.append(row)
    print(f"curl: {sum(r['total'] for r in rows)} CVEs, "
          f"{rows[0]['year']}–{rows[-1]['year']}, latest {latest}")
    print(f"  AI-attributed by year: "
          + ", ".join(f"{r['year']}:{r['ai_attributed']}/{r['total']}"
                      for r in rows if r["ai_attributed"]))
    return rows


def build_curl_quarterly() -> list[dict]:
    """curl disclosures per calendar quarter, with the AI-credited share.

    curl publishes in batches at releases, so a quarter is about the finest
    grain at which the series is not just release timing. Severity is left out
    here: at three to twelve issues a quarter the mix is sampling noise, and it
    stays on the annual series.
    """
    entries = json.loads(fetch(CURL_URL))
    per_quarter: dict[str, Counter] = defaultdict(Counter)
    for entry in entries:
        published = entry.get("published") or ""
        if not published[:4].isdigit():
            continue
        year, month = int(published[:4]), int(published[5:7])
        key = f"{year}-Q{(month - 1) // 3 + 1}"
        bucket = per_quarter[key]
        finders = [c["name"] for c in entry.get("credits", [])
                   if c.get("type") == "FINDER"]
        bucket["total"] += 1
        bucket["ai_attributed" if any(AI_MARKERS.search(n) for n in finders)
               else "other_attributed"] += 1
    rows = [{"quarter": q, "total": per_quarter[q]["total"],
             "ai_attributed": per_quarter[q]["ai_attributed"],
             "other_attributed": per_quarter[q]["other_attributed"]}
            for q in sorted(per_quarter)]
    print(f"curl quarterly: {len(rows)} non-empty quarters, "
          f"{rows[0]['quarter']}–{rows[-1]['quarter']}")
    return rows


# Mozilla names a reporter per CVE, so the same attribution the curl record
# allows is possible for Firefox. AI and fuzzing are kept apart deliberately:
# a fuzzer is automated but is not an AI system, and merging them would credit
# a decade of fuzzing to models.
FIREFOX_AI = re.compile(
    r"\bclaude\b|\banthropic\b|\bopenai\b|\bgpt\b|big sleep|mythos|\bgemini\b"
    r"|antaisecuritylab|aisle research|autonomous code security|xbow|zeropath"
    r"|\bLLM\b|\bagent\b|using AI\b", re.I)
FIREFOX_FUZZ = re.compile(r"fuzz", re.I)


def build_firefox() -> list[dict]:
    """Firefox CVEs per year from Mozilla's advisory repository, by reporter type.

    Mozilla publishes one YAML file per advisory with a `reporter` string against
    each CVE, which makes Firefox a second fixed codebase with named finders —
    the only other one in this log. Counts are by the advisory's `announced`
    year. Pre-2016 advisories do not list CVEs in this structure, so the series
    starts there.
    """
    import io as _io
    import tarfile

    import yaml

    # codeload's /tar.gz/<branch> form 404s for this repo; the archive URL works.
    blob = fetch("https://github.com/mozilla/foundation-security-advisories/"
                 "archive/refs/heads/master.tar.gz")
    per_year: dict[str, Counter] = defaultdict(Counter)
    ai_reporters: Counter = Counter()
    with tarfile.open(fileobj=_io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar.getmembers():
            if "/announce/" not in member.name or not member.name.endswith(".yml"):
                continue
            handle = tar.extractfile(member)
            if handle is None:
                continue
            text = handle.read().decode("utf-8", "replace")
            match = re.search(r"^announced:\s*.*?(20\d{2})", text, re.M | re.S)
            if match:
                year = match.group(1)
            else:
                fallback = re.search(r"mfsa(20\d{2})", member.name)
                if not fallback:
                    continue
                year = fallback.group(1)
            try:
                parsed = yaml.safe_load(text) or {}
            except Exception:
                continue
            for key, value in (parsed.get("advisories") or {}).items():
                if not str(key).startswith("CVE"):
                    continue
                reporter = str((value or {}).get("reporter", "")) if isinstance(value, dict) else ""
                bucket = per_year[year]
                bucket["total"] += 1
                if FIREFOX_AI.search(reporter):
                    bucket["ai_attributed"] += 1
                    ai_reporters[reporter[:90]] += 1
                elif FIREFOX_FUZZ.search(reporter):
                    bucket["fuzz_attributed"] += 1
                else:
                    bucket["other_attributed"] += 1
    this_year = str(datetime.now(timezone.utc).year)
    rows = [{"year": int(y), "total": per_year[y]["total"],
             "ai_attributed": per_year[y]["ai_attributed"],
             "fuzz_attributed": per_year[y]["fuzz_attributed"],
             "other_attributed": per_year[y]["other_attributed"],
             "partial_year": "yes" if y == this_year else "no"}
            for y in sorted(per_year) if per_year[y]["total"]]
    print(f"firefox: {sum(r['total'] for r in rows)} CVEs, "
          f"{rows[0]['year']}–{rows[-1]['year']}")
    print("  AI-attributed reporter strings: "
          + "; ".join(f"{c}x {n[:52]}" for n, c in ai_reporters.most_common(4)))
    return rows


# OpenSSL credits a finder per CVE under "Found by", so it takes the same
# treatment as curl and Firefox. Shared marker sets, so the three codebases are
# classified identically.
DISCOVERY_AI = re.compile(
    r"\bclaude\b|\banthropic\b|\bopenai\b|\bgpt\b|big sleep|mythos|\bgemini\b"
    r"|antaisecuritylab|aisle research|\baisle\b|autonomous code security|xbow"
    r"|zeropath|\bLLM\b|\bagent\b|using AI\b", re.I)
DISCOVERY_FUZZ = re.compile(r"fuzz", re.I)


def build_openssl() -> list[dict]:
    """OpenSSL CVEs per year with finder attribution, scraped from its own page.

    OpenSSL publishes no machine-readable feed — the JSON and XML endpoints that
    once existed both 404 — so this parses the HTML vulnerability index, which
    lists a severity, a publication date and a "Found by" credit per CVE. The
    parse is deliberately tolerant: severity is optional, because the older
    entries do not all carry one, and any record without a parseable date is
    dropped and counted so the coverage is visible.
    """
    import html as _html

    raw = fetch("https://openssl-library.org/news/vulnerabilities/")
    text = _html.unescape(re.sub(r"<[^>]+>", "|", raw.decode("utf-8", "replace")))
    gap = r"[|\s]+"
    pattern = re.compile(
        r"(CVE-\d{4}-\d{4,7})"
        + r"(?:" + gap + r"Severity" + gap + r"([A-Za-z]+))?"
        + gap + r"Published at" + gap + r"(\d{1,2} [A-Z][a-z]+ \d{4})"
        + r"(?:" + gap + r"Title" + gap + r"[^|]{0,200})?"
        + r"(?:" + gap + r"Found by" + gap + r"([^|]{0,160}))?")
    seen: set = set()
    per_year: dict[str, Counter] = defaultdict(Counter)
    ai_names: Counter = Counter()
    for match in pattern.finditer(text):
        cve = match.group(1)
        if cve in seen:
            continue
        seen.add(cve)
        year = match.group(3).split()[-1]
        finder = (match.group(4) or "").strip()
        bucket = per_year[year]
        bucket["total"] += 1
        if DISCOVERY_AI.search(finder):
            bucket["ai_attributed"] += 1
            ai_names[finder[:70]] += 1
        elif DISCOVERY_FUZZ.search(finder):
            bucket["fuzz_attributed"] += 1
        else:
            bucket["other_attributed"] += 1
    total_cves = len(set(re.findall(r"CVE-\d{4}-\d{4,7}", text)))
    this_year = str(datetime.now(timezone.utc).year)
    rows = [{"year": int(y), "total": per_year[y]["total"],
             "ai_attributed": per_year[y]["ai_attributed"],
             "fuzz_attributed": per_year[y]["fuzz_attributed"],
             "other_attributed": per_year[y]["other_attributed"],
             "partial_year": "yes" if y == this_year else "no"}
            for y in sorted(per_year)]
    print(f"openssl: {len(seen)} CVEs parsed with dates of {total_cves} named on the "
          f"page, {rows[0]['year']}–{rows[-1]['year']}")
    print("  AI-credited finders: "
          + "; ".join(f"{c}x {n[:44]}" for n, c in ai_names.most_common(4)))
    return rows


def build_ossfuzz() -> list[dict]:
    """OSS-Fuzz discoveries per year, from OSV's OSS-Fuzz archive.

    This is the automated-but-not-AI baseline: a decade of continuous fuzzing
    over hundreds of open-source projects. The year is taken from the OSV *id*
    (OSV-YYYY-N), not from `published`, because records predating 2020 were
    backfilled into OSV in 2021 and their published dates all land in that year.
    The two agree from 2020 onward, so the series is reported from 2020.
    """
    import io as _io
    import zipfile

    blob = fetch("https://osv-vulnerabilities.storage.googleapis.com/"
                 "OSS-Fuzz/all.zip")
    by_id: Counter = Counter()
    by_published: Counter = Counter()
    with zipfile.ZipFile(_io.BytesIO(blob)) as archive:
        for name in archive.namelist():
            match = re.match(r"OSV-(\d{4})-", name)
            if match:
                by_id[match.group(1)] += 1
    rows = [{"year": int(y), "discoveries": by_id[y],
             "partial_year": "yes" if int(y) == datetime.now(timezone.utc).year else "no"}
            for y in sorted(by_id) if int(y) >= 2020]
    dropped = sum(v for k, v in by_id.items() if int(k) < 2020)
    print(f"oss-fuzz: {sum(r['discoveries'] for r in rows)} records 2020 onward "
          f"({dropped} earlier ones dropped as backfilled)")
    return rows


def classify(finder: str) -> str:
    if DISCOVERY_AI.search(finder or ""):
        return "ai"
    if DISCOVERY_FUZZ.search(finder or ""):
        return "fuzz"
    return "other"


def build_finders() -> list[dict]:
    """(project, year, finder, category, cves) across the three fixed codebases.

    One row per finder per project-year, so claims about how concentrated the
    AI-credited work is can be recomputed rather than taken on trust. Finder
    strings are kept verbatim, including the multi-person credit lines, because
    splitting them on commas would silently invent individual attributions.
    """
    rows: list[dict] = []

    # curl
    for entry in json.loads(fetch(CURL_URL)):
        published = entry.get("published") or ""
        if not published[:4].isdigit():
            continue
        for credit in entry.get("credits", []):
            if credit.get("type") != "FINDER":
                continue
            rows.append({"project": "curl", "year": int(published[:4]),
                         "finder": credit["name"], "category": classify(credit["name"])})

    # OpenSSL
    import html as _html
    raw = _html.unescape(re.sub(
        r"<[^>]+>", "|",
        fetch("https://openssl-library.org/news/vulnerabilities/").decode("utf-8", "replace")))
    gap = r"[|\s]+"
    pattern = re.compile(
        r"(CVE-\d{4}-\d{4,7})"
        + r"(?:" + gap + r"Severity" + gap + r"([A-Za-z]+))?"
        + gap + r"Published at" + gap + r"(\d{1,2} [A-Z][a-z]+ \d{4})"
        + r"(?:" + gap + r"Title" + gap + r"[^|]{0,200})?"
        + r"(?:" + gap + r"Found by" + gap + r"([^|]{0,160}))?")
    seen: set = set()
    for match in pattern.finditer(raw):
        if match.group(1) in seen:
            continue
        seen.add(match.group(1))
        finder = (match.group(4) or "").strip()
        if finder:
            rows.append({"project": "openssl", "year": int(match.group(3).split()[-1]),
                         "finder": finder, "category": classify(finder)})

    # Firefox
    import io as _io
    import tarfile

    import yaml
    blob = fetch("https://github.com/mozilla/foundation-security-advisories/"
                 "archive/refs/heads/master.tar.gz")
    with tarfile.open(fileobj=_io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar.getmembers():
            if "/announce/" not in member.name or not member.name.endswith(".yml"):
                continue
            handle = tar.extractfile(member)
            if handle is None:
                continue
            body = handle.read().decode("utf-8", "replace")
            found = re.search(r"^announced:\s*.*?(20\d{2})", body, re.M | re.S)
            if found:
                year = int(found.group(1))
            else:
                alt = re.search(r"mfsa(20\d{2})", member.name)
                if not alt:
                    continue
                year = int(alt.group(1))
            try:
                parsed = yaml.safe_load(body) or {}
            except Exception:
                continue
            for key, value in (parsed.get("advisories") or {}).items():
                if not str(key).startswith("CVE") or not isinstance(value, dict):
                    continue
                finder = str(value.get("reporter", "")).strip()
                if finder:
                    rows.append({"project": "firefox", "year": year,
                                 "finder": finder, "category": classify(finder)})

    grouped: dict = defaultdict(int)
    for row in rows:
        grouped[(row["project"], row["year"], row["finder"], row["category"])] += 1
    out = [{"project": p, "year": y, "finder": f, "category": c, "cves": n}
           for (p, y, f, c), n in sorted(grouped.items(),
                                         key=lambda kv: (kv[0][0], kv[0][1], -kv[1]))]
    ai = [r for r in out if r["category"] == "ai"]
    print(f"finders: {len(out)} project-year-finder rows, {len(ai)} AI-credited")
    for project in ("curl", "openssl", "firefox"):
        top = [r for r in ai if r["project"] == project]
        top.sort(key=lambda r: -r["cves"])
        if top:
            print(f"  {project}: top AI finder {top[0]['cves']} CVEs — "
                  f"{top[0]['finder'][:56]}")
    return out


def build_erdos() -> list[dict]:
    text = fetch(ERDOS_URL).decode("utf-8", "replace")
    monthly: dict[str, dict] = {}
    for record in csv.DictReader(io.StringIO(text)):
        date = (record.get("date") or "")[:10]
        if len(date) != 10:
            continue
        try:
            monthly[date[:7]] = {
                "month": date[:7],
                "date": date,
                "total_problems": int(record["total_problems"]),
                "total_solved": int(record["total_solved"]),
                "lean_formalized": int(record["lean_formalized"]),
            }
        except (KeyError, ValueError):
            continue
    rows = [monthly[k] for k in sorted(monthly)]
    # Once the catalogue count stops changing, a rise in `solved` cannot be
    # caused by adding a newly catalogued, already-solved problem. The cohort
    # and statuses remain editable, and status dates are not solution dates.
    final_total = rows[-1]["total_problems"]
    for row in rows:
        row["catalogue_count_unchanged"] = (
            "yes" if row["total_problems"] == final_total else "no")
    unchanged = [r for r in rows if r["catalogue_count_unchanged"] == "yes"]
    print(f"erdos: {len(rows)} months, {rows[0]['month']}–{rows[-1]['month']}; "
          f"catalogue count unchanged at {final_total} from "
          f"{unchanged[0]['month']}")
    print(f"  solved {rows[0]['total_solved']} → {rows[-1]['total_solved']} overall; "
          f"{unchanged[0]['total_solved']} → {unchanged[-1]['total_solved']} "
          f"(net +{unchanged[-1]['total_solved'] - unchanged[0]['total_solved']}) "
          "while catalogue count unchanged")
    return rows


def build_nvd_and_kev(first_year: int = 2016) -> list[dict]:
    """Published CVEs per year (NVD) beside newly-exploited CVEs per year (CISA KEV).

    The pair is the point. NVD counts what gets *found*; the Known Exploited
    Vulnerabilities catalog counts what gets *used against someone*. A surge in
    the first without a surge in the second is the single most important thing
    to know about the 2026 vulnerability numbers, and each series is only
    interpretable next to the other.

    NVD caps a query window at 120 days and rate-limits unkeyed callers, so the
    year is fetched in quarters with a pause between calls. `totalResults` is
    read rather than the records themselves.
    """
    import time
    import urllib.parse

    today = datetime.now(timezone.utc).date()
    per_year: dict[int, int] = {}
    per_quarter: dict[str, int] = {}
    for year in range(first_year, today.year + 1):
        edges = [f"{year}-01-01", f"{year}-04-01", f"{year}-07-01",
                 f"{year}-10-01", f"{year + 1}-01-01"]
        total = 0
        for start, end in zip(edges, edges[1:]):
            if datetime.fromisoformat(start).date() > today:
                break
            params = urllib.parse.urlencode({
                "resultsPerPage": 1,
                "pubStartDate": f"{start}T00:00:00.000",
                "pubEndDate": f"{min(end, today.isoformat())}T00:00:00.000",
            })
            data = fetch_json(
                f"https://services.nvd.nist.gov/rest/json/cves/2.0?{params}")
            count = int(data.get("totalResults", 0))
            total += count
            quarter = (datetime.fromisoformat(start).month - 1) // 3 + 1
            per_quarter[f"{year}-Q{quarter}"] = count
            time.sleep(8.0)  # unkeyed NVD allows 5 requests per 30 seconds
        per_year[year] = total
        print(f"  NVD {year}: {total}")

    kev = fetch_json(
        "https://www.cisa.gov/sites/default/files/feeds/"
        "known_exploited_vulnerabilities.json")
    added: Counter = Counter()
    added_q: Counter = Counter()
    for item in kev.get("vulnerabilities", []):
        date = item.get("dateAdded", "")
        if date[:4].isdigit():
            added[int(date[:4])] += 1
            added_q[f"{date[:4]}-Q{(int(date[5:7]) - 1) // 3 + 1}"] += 1
    print(f"  KEV catalog: {len(kev.get('vulnerabilities', []))} entries, "
          f"{kev.get('count', '?')} declared")

    rows = []
    for year in sorted(per_year):
        rows.append({
            "year": year,
            "nvd_published": per_year[year],
            "kev_added": added.get(year, 0),
            "partial_year": "yes" if year == today.year else "no",
            "data_through": today.isoformat() if year == today.year else "",
        })
    # The final quarter is incomplete; flag it rather than letting it read as a dip.
    current_q = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
    qrows = [{"quarter": q, "nvd_published": per_quarter[q],
              "kev_added": added_q.get(q, 0),
              "partial_quarter": "yes" if q == current_q else "no",
              "data_through": today.isoformat() if q == current_q else ""}
             for q in sorted(per_quarter)]
    print(f"  quarterly: {len(qrows)} quarters, {qrows[0]['quarter']}–{qrows[-1]['quarter']}"
          f" (final one partial through {today.isoformat()})")
    return rows, qrows


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path.relative_to(ROOT)}")


def main() -> int:
    write(OUT_CURL, build_curl())
    write(OUT_CURL_Q, build_curl_quarterly())
    write(OUT_FIREFOX, build_firefox())
    write(OUT_OPENSSL, build_openssl())
    write(OUT_FINDERS, build_finders())
    write(OUT_OSSFUZZ, build_ossfuzz())
    write(OUT_ERDOS, build_erdos())
    yearly, quarterly = build_nvd_and_kev()
    write(OUT_NVD, yearly)
    write(OUT_NVD_Q, quarterly)
    return 0


if __name__ == "__main__":
    sys.exit(main())
