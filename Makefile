PYTHON := python3

AUTHOR := Tsuyoshi Hombashi
FIRST_RELEASE_YEAR := 2020
LAST_UPDATE_YEAR := $(shell git log -1 --format=%cd --date=format:%Y)


.PHONY: build
build: clean
	@$(PYTHON) -m tox -e build
	ls -lh dist/*

.PHONY: check
check:
	@$(PYTHON) -m tox -e lint

.PHONY: clean
clean:
	$(PYTHON) -m tox -e clean

.PHONY: fmt
fmt:
	@$(PYTHON) -m tox -e fmt

.PHONY: release
release:
	$(PYTHON) -m tox -e release

.PHONY: setup-ci
setup-ci:
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade pip
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade tox

.PHONY: setup-dev
setup-dev: setup-ci
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .[test]
	$(PYTHON) -m pip check

.PHONY: examples
examples:
	cd examples; \
	pytest .; \
	pytest . --md-report-exclude-outcomes failed error xfailed -v ; \
	pytest . --md-report-flavor gfm --md-report-output gfm_report.md

.PHONY: test
test:
	$(PYTHON) -m tox -e py

.PHONY: update-copyright
update-copyright:
	sed -i "s/f\"Copyright .*/f\"Copyright $(FIRST_RELEASE_YEAR)-$(LAST_UPDATE_YEAR), {__author__}\"/" pytest_md_report/__version__.py
	sed -i "s/^Copyright (c) .* $(AUTHOR)/Copyright (c) $(FIRST_RELEASE_YEAR)-$(LAST_UPDATE_YEAR) $(AUTHOR)/" LICENSE
