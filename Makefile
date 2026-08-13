.PHONY: help figure-image figures figure check check-figures check-links index docs fetch fetch-one clean

FIGURE_IMAGE ?= ai-discovery-data-figures:python3.12.13
FIGURE_PLATFORM := linux/amd64
FIGURE_DOCKERFILE := tools/figures.Dockerfile
FIGURE_RUN = docker run --rm --platform $(FIGURE_PLATFORM) \
	--user "$$(id -u):$$(id -g)" \
	--volume "$(CURDIR):/repo" \
	--workdir /repo \
	$(FIGURE_IMAGE)

# Every problem folder builds itself. There is no central generator, so the
# target is a loop over the folders rather than a list to keep in sync.
FIGURE_SCRIPTS := $(wildcard problems/*/figure.py)
# math-antedb is excluded: it needs a checkout of github.com/teorth/expdb and a
# cddlib-backed pycddlib<3, so it is run by hand and its output vendored.
FETCH_SCRIPTS := $(filter-out problems/math-antedb/fetch.py, $(wildcard problems/*/fetch.py))

help:
	@echo "figure-image       build the pinned Linux renderer (requires Docker)"
	@echo "figures            redraw every problems/*/*.png in that renderer (no data network)"
	@echo "figure PROBLEM=x   redraw one folder in that renderer"
	@echo "check              verify every folder accounts for its data, figure and sources"
	@echo "check-figures      redraw and byte-compare in the same renderer used by CI"
	@echo "check-links        check every documented URL (network, may see transient failures)"
	@echo "index              rewrite README's and CUMULATIVE.md's generated tables (runs check-figures)"
	@echo "docs               rebuild the interactive chart pages in docs/ (GitHub Pages)"
	@echo "fetch              refetch every automatable series from upstream (network, slow)"
	@echo "fetch-one PROBLEM=x  refetch one folder"

figure-image:
	docker build --platform $(FIGURE_PLATFORM) --file $(FIGURE_DOCKERFILE) --tag $(FIGURE_IMAGE) .

figures: figure-image
	@$(FIGURE_RUN) sh -c 'for script in $(FIGURE_SCRIPTS); do python3 "$$script" || exit 1; done'

figure: figure-image
	$(FIGURE_RUN) python3 problems/$(PROBLEM)/figure.py

check:
	python3 tools/check.py

# Separate from `check` because it needs Docker and is slower: it runs every
# figure.py and compares the result with what is committed.
check-figures: figure-image
	$(FIGURE_RUN) python3 tools/check.py --reproduce

check-links:
	python3 tools/check.py --links

index: figure-image
	$(FIGURE_RUN) python3 tools/check.py --write-index

# The interactive companions to the committed PNGs. Pure Python, no Docker:
# the pages embed the CSV rows and a Vega-Lite spec, so rebuild whenever a
# vendored CSV changes, alongside `make figures`.
docs:
	python3 tools/build_docs.py

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
	echo "if any series now reaches past lib/chart.py's AS_OF_DATE, bump it and rerun make index"; \
	exit $$status

fetch-one:
	python3 problems/$(PROBLEM)/fetch.py

# The figures are committed, so this is "throw them away and rebuild", not a
# routine step. .cache/ holds today's upstream responses and is never part of a
# build, so it goes too.
clean:
	rm -f problems/*/*.png
	rm -rf .cache
