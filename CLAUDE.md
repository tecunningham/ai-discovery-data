# Working in this repository

Data repository of discovery-rate time series. One folder per problem under
`problems/<slug>/`: the README (per [FORMAT.md](FORMAT.md)), the vendored
CSVs, `fetch.py` (rebuilds them), `figure.py` (draws the PNGs), `check.py`
(recomputes the numbers the prose states), `chart_spec.py` (declares the docs
page's interactive charts), and the committed PNGs.

## Hard rules

- **Never run a `figure.py` directly.** Committed PNGs are byte-reproducible
  only in the pinned container: `make figure PROBLEM=<slug>` or
  `make figures`. The save helper rejects any other renderer.
- **Never hand-edit a PNG, a `cumulative-<slug>.json`, `docs/*.html`, or
  the generated blocks in README.md / CUMULATIVE.md** (between `BEGIN/END
  GENERATED` markers). They are outputs: `make figures` (PNGs and the JSON
  beside each cumulative panel), `make docs`, `make index`.
- **Do not rename CSVs or PNGs casually.** The blog at tecunningham.github.io
  resolves CSVs by bare filename and embeds the PNGs by URL, so a rename here
  needs a matching change there. Filenames are unique across all folders.
- **Do not bump requirements.txt pins on their own.** They are the figure
  ABI; a bump changes PNG bytes and comes with a full `make figures` +
  `make index`.

## Routine sequences

- Edited data or prose in a folder → `make check`, then `make index` (rewrites
  the generated tables; containerized) and `make docs`, and commit the
  regenerated files with the change. CI byte-compares all of them.
- `make fetch` pulled data newer than `AS_OF_DATE` in `lib/dates.py` → bump
  the date, `make figures`, `make index`, `make docs`.
- Adding a series → a new folder with all the files above; FORMAT.md is the
  contract for the README, and `tools/check.py` (run by `make check`) will
  list everything missing, including the `discovery-<slug>.png` /
  `cumulative-<slug>.png` names the index pages find figures by.
- The Monday refresh (`.github/workflows/weekly-update.yml`, driven by
  `tools/weekly_update.py`) runs the fetch → bump → prose → figures → index →
  docs sequence unattended and opens a PR named `auto/weekly-refresh-<date>`.
  It merges itself only when every check passes and no Verdict term moved;
  otherwise the PR waits for a person. If you are the Claude step inside it,
  edit only `problems/*/README.md` and write anything that was more than
  arithmetic to `.weekly/judgment-calls.md`. If you are instead the
  scheduled session finishing an open `auto/weekly-refresh-*` PR: same
  rules, but do not run `make index` or `make docs` (no pinned renderer
  there); push the README edits and let
  `.github/workflows/refresh-finish.yml` regenerate, re-check and merge.
  Put judgment calls in the commit message under a `Judgment calls:` line
  (or in a PR comment opening with `**Judgment calls**`); either holds the
  PR for a person.

## Layout of the shared code

- `lib/chart.py`, `lib/families.py`, `lib/cumulative.py` — matplotlib chart
  styling and shared shapes for the PNGs.
- `lib/vega.py` — the same idea for the interactive pages.
- `lib/dates.py`, `lib/palette.py`, `lib/document.py`, `lib/prose.py`,
  `lib/table.py`, `lib/web.py`, `lib/credits.py` — matplotlib-free helpers
  (snapshot date, colours, front-matter parsing, prose recomputation, CSV IO,
  cached fetching, credit classification).
- `tools/check.py` — the validator; `tools/tables.py` — the generated-table
  renderer; `tools/build_docs.py` — the docs/ builder.

`make check` runs host-side with no matplotlib. Anything that draws or
byte-compares figures needs Docker for the pinned renderer. A checkout
without Docker (a Claude Code session on the web, for one) gets its outputs
from `.github/workflows/render.yml`: push the work to a branch named
`render/<anything>`, wait for the "Render: figures, index and docs" commit it
pushes back, and pull that commit into the working branch.
