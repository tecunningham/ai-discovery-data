#!/usr/bin/env python3
"""Copy the canonical data and figures into the blog repository.

    python3 tools/sync_to_blog.py --blog ~/tecunningham.github.io
    python3 tools/sync_to_blog.py --check          # report drift, write nothing

This repository owns the series; the blog repository holds working copies so its
own figure code, claim audits, and validators keep running offline and in CI.
That means the copies can drift, which is what --check is for: it is the one
command that says whether the blog is rendering something this repository no
longer believes.

Sync is one-directional on purpose. Editing a CSV in the blog repo and syncing
back would silently make the blog canonical again, so this script never reads
the blog's version as an input.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

# Where each kind of file lands in the blog repo. The blog's tools read the
# apple-picking data directory and the shared images directory by absolute
# convention, so these paths are fixed rather than configurable.
DATA_DEST = "posts/data/apple-picking"
FIGURE_DEST = "posts/images"

# The one file this repository does not own. The prestige-list ledger is
# transcribed by hand inside the blog's own famous_problem_lists() figure code,
# which writes the CSV as a side effect, so copying our snapshot over the blog's
# copy would silently revert a transcription made there. We hold a vendored
# snapshot to plot from and leave the blog's copy alone.
NOT_OURS = {"famous-open-problem-lists.csv"}


def pairs(blog: Path) -> list[tuple[Path, Path]]:
    out = []
    for source, dest in ((DATA, DATA_DEST), (FIGURES, FIGURE_DEST)):
        for path in sorted(source.iterdir()):
            if path.suffix in {".csv", ".png"} and path.name not in NOT_OURS:
                out.append((path, blog / dest / path.name))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blog", type=Path, default=Path.home() / "tecunningham.github.io")
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()

    blog = args.blog.expanduser().resolve()
    if not (blog / DATA_DEST).is_dir():
        print(f"not a blog checkout: {blog} has no {DATA_DEST}", file=sys.stderr)
        return 2

    stale, missing, copied = [], [], []
    for source, dest in pairs(blog):
        if not dest.exists():
            missing.append(dest)
        elif not filecmp.cmp(source, dest, shallow=False):
            stale.append(dest)
        else:
            continue
        if not args.check:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            copied.append(dest)

    def names(paths: list[Path]) -> str:
        return ", ".join(p.name for p in paths)

    if args.check:
        if not stale and not missing:
            print(f"blog copies match ({len(pairs(blog))} files)")
            return 0
        if missing:
            print(f"absent from the blog ({len(missing)}): {names(missing)}")
        if stale:
            print(f"differs from canonical ({len(stale)}): {names(stale)}")
        return 1

    if copied:
        print(f"synced {len(copied)} file(s) to {blog}: {names(copied)}")
    else:
        print(f"nothing to do; blog already matches ({len(pairs(blog))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
