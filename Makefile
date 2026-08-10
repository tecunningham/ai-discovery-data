.PHONY: help figures fetch drift check index sync clean

BLOG ?= $(HOME)/tecunningham.github.io

help:
	@echo "figures  regenerate figures/*.png from data/*.csv (no network)"
	@echo "check    verify every series has a figure, a doc, and a source"
	@echo "index    rewrite the generated series table in README.md"
	@echo "fetch    refetch the automatable series from upstream (network)"
	@echo "drift    report upstream drift without rewriting the CSVs (network)"
	@echo "sync     copy figures/ into the blog repo (BLOG=$(BLOG))"

figures:
	python3 tools/make_figures.py
	python3 tools/make_omnibus.py

check:
	python3 tools/check.py

index:
	python3 tools/check.py --write-index

# Upstream fetchers, each independently runnable. Kept out of `figures` because
# they need the network and several sources rate-limit.
fetch:
	python3 tools/fetch/collective_progress.py
	python3 tools/fetch/alphaevolve_records.py
	python3 tools/fetch/alphaevolve_inventory.py
	python3 tools/fetch/refresh_series.py --write
	@echo "antedb_extract.py needs a checkout of github.com/teorth/expdb; run it by hand"

# Report drift in the living series without touching the vendored copies.
drift:
	python3 tools/fetch/refresh_series.py

sync:
	python3 tools/sync_to_blog.py --blog $(BLOG)

clean:
	rm -f figures/*.png
