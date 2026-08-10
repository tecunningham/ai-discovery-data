#!/usr/bin/env python3
"""Copy the generated figures into the blog repository.

    python3 tools/sync_to_blog.py --blog ~/tecunningham.github.io
    python3 tools/sync_to_blog.py --check          # report drift, write nothing

Only images move. The blog reads the CSVs from this repository directly, through
its own tools/discovery_data.py, so there is exactly one copy of every dataset
and a stale number there fails its audit immediately. Figures are the exception
because Quarto has to find them inside its own project tree to render and
publish them, so the blog keeps copies as build artifacts.

Sync is one-directional on purpose. Copying an edited image back would make the
blog canonical again, so this script never reads the blog's version as an input.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "problems"

# The blog's shared images directory, fixed by its own convention. It is flat,
# so the figures lose their folder on the way over; the names already carry the
# series, and nothing in the blog would find them under a nested path.
FIGURE_DEST = "posts/images"


def pairs(blog: Path) -> list[tuple[Path, Path]]:
    return [(path, blog / FIGURE_DEST / path.name)
            for path in sorted(PROBLEMS.glob("*/*.png"))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blog", type=Path, default=Path.home() / "tecunningham.github.io")
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()

    blog = args.blog.expanduser().resolve()
    if not (blog / FIGURE_DEST).is_dir():
        print(f"not a blog checkout: {blog} has no {FIGURE_DEST}", file=sys.stderr)
        return 2

    stale, absent, copied = [], [], []
    for source, dest in pairs(blog):
        if not dest.exists():
            absent.append(dest)
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
        if not stale and not absent:
            print(f"blog figures match ({len(pairs(blog))} files)")
            return 0
        if absent:
            print(f"absent from the blog ({len(absent)}): {names(absent)}")
        if stale:
            print(f"differs from canonical ({len(stale)}): {names(stale)}")
        return 1

    if copied:
        print(f"synced {len(copied)} figure(s) to {blog}: {names(copied)}")
    else:
        print(f"nothing to do; blog already matches ({len(pairs(blog))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
