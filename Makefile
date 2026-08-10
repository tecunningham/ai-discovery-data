.PHONY: help figures figure check check-figures index fetch fetch-one sync clean

BLOG ?= $(HOME)/tecunningham.github.io

# Every problem folder builds itself. There is no central generator, so the
# target is a loop over the folders rather than a list to keep in sync.
FIGURE_SCRIPTS := $(wildcard problems/*/figure.py)
# math-antedb is excluded: it needs a checkout of github.com/teorth/expdb and a
# cddlib-backed pycddlib<3, so it is run by hand and its output vendored.
FETCH_SCRIPTS := $(filter-out problems/math-antedb/fetch.py, $(wildcard problems/*/fetch.py))

help:
	@echo "figures            redraw every problems/*/*.png from its folder's CSVs (no network)"
	@echo "figure PROBLEM=x   redraw one folder"
	@echo "check              verify every folder accounts for its data, figure and sources"
	@echo "check-figures      also redraw every figure and compare it with the committed one"
	@echo "index              rewrite README's series index and status table (runs check-figures)"
	@echo "fetch              refetch every automatable series from upstream (network, slow)"
	@echo "fetch-one PROBLEM=x  refetch one folder"
	@echo "sync               copy the figures into the blog repo (BLOG=$(BLOG))"

figures:
	@for script in $(FIGURE_SCRIPTS); do python3 $$script || exit 1; done

figure:
	python3 problems/$(PROBLEM)/figure.py

check:
	python3 tools/check.py

# Separate from `check` only because it is ten seconds rather than one: it runs
# every figure.py and compares the result with what is committed.
check-figures:
	python3 tools/check.py --reproduce

index:
	python3 tools/check.py --write-index

# Kept out of `figures` because these need the network and several sources
# rate-limit. Responses are cached for the day under .cache/, so two folders
# sharing an upstream do not fetch it twice.
fetch:
	@status=0; \
	for script in $(FETCH_SCRIPTS); do \
		echo "== $$script"; \
		python3 $$script || status=1; \
	done; \
	if [ $$status -ne 0 ]; then \
		echo "one or more fetchers reported stale data or failed" >&2; \
	fi; \
	echo "problems/math-antedb/fetch.py needs github.com/teorth/expdb and pycddlib<3; run it by hand"; \
	exit $$status

fetch-one:
	python3 problems/$(PROBLEM)/fetch.py

sync:
	python3 tools/sync_to_blog.py --blog $(BLOG)

clean:
	rm -f problems/*/*.png
