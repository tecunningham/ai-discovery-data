#!/usr/bin/env python3
"""Staleness probe for the manually classified MIPLIB release ledger."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import read_csv  # noqa: E402
from lib.web import fetch  # noqa: E402

URL = "https://miplib.zib.de/news.html"


def main() -> int:
    rows = read_csv(HERE / "miplib-solution-releases.csv")
    latest = rows[-1]
    text = fetch(URL, refresh=True).decode("utf-8", errors="replace")
    version = latest["solufile"]
    if not re.search(rf"solufile(?: version)?\s+{re.escape(version)}\b", text, re.I):
        print(f"vendored solufile {version} is absent from the live news log")
        return 1
    newer = [int(x) for x in re.findall(r"solufile(?: version)?\s+(\d+)", text, re.I)]
    if newer and max(newer) > int(version):
        print(f"live news has solufile {max(newer)} after vendored {version}")
        return 1
    print(f"miplib-solution-releases.csv is current through solufile {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
