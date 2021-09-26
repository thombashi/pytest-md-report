AUTHOR := thombashi
PACKAGE := pytest-md-report
BUILD_WORK_DIR := _work
PKG_BUILD_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)
PYTHON := python3


.PHONY: build
build: clean
	@tox -e build
	ls -lh dist/*

.PHONY: build-remote
build-remote: clean
	@mkdir -p $(BUILD_WORK_DIR)
	@cd $(BUILD_WORK_DIR) && \
		git clone https://github.com/$(AUTHOR)/$(PACKAGE).git --depth 1 && \
		cd $(PACKAGE) && \
		tox -e build
	ls -lh $(PKG_BUILD_DIR)/dist/*

.PHONY: check
check:
	@tox -e lint

.PHONY: clean
clean:
	rm -rf $(BUILD_WORK_DIR)
	@tox -e clean

.PHONY: fmt
fmt:
	@tox -e fmt

.PHONY: release
release:
	@cd $(PKG_BUILD_DIR) && $(PYTHON) setup.py release --sign --search-dir pytest_md_report
	@make clean

.PHONY: setup
setup:
	@$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .[test] releasecmd tox
	@$(PYTHON) -m pip check
