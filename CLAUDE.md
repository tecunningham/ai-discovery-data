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
- The Monday digest (`.github/workflows/weekly-update.yml`, driven by
  `tools/weekly_update.py`) refetches everything, diffs it against the
  committed data and emails what moved. It commits nothing and opens no PR;
  the refetched CSVs are in the run's artifact.

## Bringing the repository up to date

Done on request, usually after a digest. On a branch from main:

1. `python3 tools/weekly_update.py fetch` with `AI_DISCOVERY_AS_OF=<today>`
   in the environment, then `python3 tools/weekly_update.py bump-as-of`
   (same variable) so `AS_OF_DATE` matches the fetch day.
2. Anything the fetch reports as needing a person (exit `NEEDS_PERSON`, the
   ⚠️ lines) is a staleness probe: transcribe the new rows by hand from the
   upstream it names, and attribute any AI credit from primary sources.
3. `make check`; restate every README fact it reports, in the phrasing the
   folder's `check.py` recomputes. A changed Verdict term, a new AI credit,
   or a coding choice the folder's rules don't settle is a judgment call:
   list it in the commit message under `Judgment calls:` and in the PR body.
4. `make figures`, `make docs`, `make index`, `make docs` (index rewrites
   tables the index pages embed), `make check`; commit and open one PR.

In a Claude Code cloud session the pinned renderer works once Docker is
started (`dockerd &`). The image build needs the sandbox proxy's CA for pip,
passed as a build secret so it never lands in the image: build from a copy
of `tools/figures.Dockerfile` whose `RUN pip install` line is prefixed with
`--mount=type=secret,id=ca PIP_CERT=/run/secrets/ca`, with
`docker build --network host --secret id=ca,src=$CA_BUNDLE --tag
ai-discovery-data-figures:python3.12.13 ...`, then run the Make targets with
`FIGURE_IMAGE_PRELOADED=1`. If the untouched folders' PNGs byte-compare
clean under `make index`, the image is right.

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
byte-compares figures needs Docker for the pinned renderer.
