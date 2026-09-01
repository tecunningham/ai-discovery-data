# Draft: game record time series (mock-ups)

Exploratory mock-ups for a possible `games-` family of problem folders. Nothing
in this directory follows FORMAT.md yet, and nothing here is wired into
`make check` / `make figures` / `make index`: the PNGs are throwaway drafts
drawn by `mockup_figures.py` on stock matplotlib, not pinned-container output.

## Provenance and confidence

The CSVs are hand-transcribed. This session's sandbox could not reach the
upstream sites directly (network egress limited to GitHub/PyPI), so rows were
transcribed from search-result quotations of the sources below plus general
knowledge, and each row carries a `status` column:

- `verified` — date and value quoted from a named source during transcription.
- `approx-date` — value quoted from a source; day (sometimes month) estimated.
- `approx` — value and/or date approximate; confirm before promoting to a
  problem folder.

The figures draw `approx*` rows as open circles so the two grades are visible.

## The four series

| CSV | What it is | Real upstream for a future `fetch.py` |
|---|---|---|
| `speedrun-smb1-anypercent.csv` | Super Mario Bros. any% human world record, 2014–2025 | speedrun.com stats JSON; Epoch AI speedrunning dataset (epochai.org/data/speedrunning, snapshot 2022-10-14) for the cross-game version |
| `chess-ssdf-elo.csv` | best program on the SSDF rating list, 1984–2023 (list discontinued 2023-12-31) | archived SSDF lists (ssdf.bosjo.net via Wayback); CCRL for a continuation past 2023 |
| `tetris-nes-score.csv` | NES Tetris highest score, 2009–2025 | community record tables (nestetris.com, tetris.wiki); hand-scored per FORMAT.md |
| `donkey-kong-score.csv` | Donkey Kong arcade high score, 1982–2021 (standing) | Wikipedia "Donkey Kong high score competition" progression table; Twin Galaxies |

Known caveats already visible in the drafts: the SSDF 2008 jump is partly a
test-hardware change; the 1982 and 2007 Donkey Kong rows are the disputed
Billy Mitchell scores (stricken 2018, reinstated 2020); NES Tetris switches
regime in 2021 when the rolling technique made the 999,999 display cap
irrelevant; the SMB1 record is 0.216 s above the tool-assisted limit.

## Promoting a series

To turn one of these into a real problem folder: re-fetch every `approx*` row
from the upstream in the table (from an environment that can reach it), write
the FORMAT.md README with a proper `fetch.py`/`check.py`/`figure.py`
/`chart_spec.py`, and delete the corresponding CSV here. Delete this directory
once all four are promoted or rejected.
