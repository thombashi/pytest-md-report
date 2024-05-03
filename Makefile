AUTHOR := thombashi
PACKAGE := pytest-md-report
BUILD_WORK_DIR := _work
PKG_BUILD_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)
PYTHON := python3


.PHONY: build
build: clean
	@$(PYTHON) -m tox -e build
	ls -lh dist/*

.PHONY: build-remote
build-remote: clean
	@mkdir -p $(BUILD_WORK_DIR)
	@cd $(BUILD_WORK_DIR) && \
		git clone https://github.com/$(AUTHOR)/$(PACKAGE).git --depth 1 && \
		cd $(PACKAGE) && \
		$(PYTHON) -m tox -e build
	ls -lh $(PKG_BUILD_DIR)/dist/*

.PHONY: check
check:
	@$(PYTHON) -m tox -e lint

.PHONY: clean
clean:
	@rm -rf $(BUILD_WORK_DIR)
	@$(PYTHON) -m tox -e clean

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
