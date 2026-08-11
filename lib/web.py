"""Fetching upstream sources, with a cache so sibling folders share one request.

Two problem folders sometimes read the same upstream document: the disclosed and
exploited vulnerability counts come from one NVD query and one CISA feed, and
splitting the fetchers means both scripts want them. NVD rate-limits unkeyed
callers to five requests per thirty seconds, so a naive split would double a
run that is already slow. Responses are therefore cached under .cache/ for the
day, and a second caller reuses the first one's bytes.

Pass refresh=True to bypass the cache when checking whether a series has moved.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"


def _cache_path(url: str) -> Path:
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    return CACHE / f"{date.today().isoformat()}-{key}"


def _prune(keep: str) -> None:
    """Drop cache entries from earlier days.

    The cache exists so two folders sharing an upstream fetch it once in one
    run; it is not a history. Keying by date and never sweeping would leave a
    full set of responses per day forever, which is how a scratch directory
    turns into a quiet several-gigabyte pile in a repository nobody expects to
    hold one.
    """
    for stale in CACHE.glob("*-*"):
        if not stale.name.startswith(keep):
            stale.unlink(missing_ok=True)


def fetch(url: str, refresh: bool = False) -> bytes:
    """GET url, reusing today's cached copy unless refresh is set."""
    cached = _cache_path(url)
    if cached.exists() and not refresh:
        return cached.read_bytes()
    result = subprocess.run(
        [
            "curl",
            "--fail",
            "--silent",
            "--show-error",
            "--location",
            "--max-time",
            "120",
            url,
        ],
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"failed to fetch {url}" + (f": {detail}" if detail else ""))
    CACHE.mkdir(exist_ok=True)
    _prune(keep=date.today().isoformat())
    cached.write_bytes(result.stdout)
    return result.stdout


def fetch_json(url: str, attempts: int = 6, base_delay: float = 8.0, refresh: bool = False):
    """Fetch and parse JSON, retrying on the rate-limit replies NVD returns.

    Over quota, NVD answers with an HTML error page rather than a JSON error, so
    a bare json.loads dies partway through a run with "Expecting value". Back
    off and retry instead.
    """
    last = ""
    for attempt in range(attempts):
        raw = fetch(url, refresh=refresh or attempt > 0)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            last = raw[:120].decode("utf-8", "replace").replace("\n", " ")
            wait = base_delay * (attempt + 1)
            print(f"    non-JSON reply, retrying in {wait:.0f}s ({last[:60]}...)")
            time.sleep(wait)
    raise SystemExit(f"gave up on {url}: {last}")
