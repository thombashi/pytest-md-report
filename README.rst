.. contents:: **pytest-md-report**
   :backlinks: top
   :depth: 2


Summary
============================================
|PyPI pkg ver| |Supported Python ver| |Supported Python impl| |CI status| |CodeQL|

.. |PyPI pkg ver| image:: https://badge.fury.io/py/pytest-md-report.svg
    :target: https://badge.fury.io/py/pytest-md-report
    :alt: PyPI package version

.. |Supported Python impl| image:: https://img.shields.io/pypi/implementation/pytest-md-report.svg
    :target: https://pypi.org/project/pytest-md-report
    :alt: Supported Python implementations

.. |Supported Python ver| image:: https://img.shields.io/pypi/pyversions/pytest-md-report.svg
    :target: https://pypi.org/project/pytest-md-report
    :alt: Supported Python versions

.. |CI status| image:: https://github.com/thombashi/pytest-md-report/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/thombashi/pytest-md-report/actions/workflows/ci.yml
    :alt: CI status of Linux/macOS/Windows

.. |CodeQL| image:: https://github.com/thombashi/pytest-md-report/actions/workflows/github-code-scanning/codeql/badge.svg
    :target: https://github.com/thombashi/pytest-md-report/actions/workflows/github-code-scanning/codeql
    :alt: CodeQL

A pytest plugin to generate test outcomes reports with markdown table format.

Installation
============================================
::

    pip install pytest-md-report


Usage
============================================
::

    pytest --md-report examples/

.. figure:: https://cdn.jsdelivr.net/gh/thombashi/pytest-md-report@master/ss/pytest_md_report_example.png
    :scale: 80%
    :alt: https://github.com/thombashi/pytest-md-report/blob/master/ss/pytest_md_report_example.png

    Output example


Other examples
--------------------------------------------
Increase verbosity level (``--md-report-verbose`` option):

::

    pytest --md-report --md-report-verbose=1 examples/

.. figure:: https://cdn.jsdelivr.net/gh/thombashi/pytest-md-report@master/ss/pytest_md_report_example_verbose.png
    :scale: 80%
    :alt: https://github.com/thombashi/pytest-md-report/blob/master/ss/pytest_md_report_example_verbose.png

    Output example (verbose)

Not rendering results of zero value (``--md-report-zeros empty`` option):

::

    pytest --md-report --md-report-zeros empty --md-report-color never examples/

::

    |         filepath         | passed | failed | error | skipped | xfailed | xpassed | SUBTOTAL |
    | ------------------------ | -----: | -----: | ----: | ------: | ------: | ------: | -------: |
    | examples/test_error.py   |        |        |     2 |         |         |         |        2 |
    | examples/test_failed.py  |        |      2 |       |         |         |         |        2 |
    | examples/test_pass.py    |      2 |        |       |         |         |         |        2 |
    | examples/test_skipped.py |        |        |       |       2 |         |         |        2 |
    | examples/test_xfailed.py |        |        |       |         |       2 |         |        2 |
    | examples/test_xpassed.py |        |        |       |         |         |       2 |        2 |
    | TOTAL                    |      2 |      2 |     2 |       2 |       2 |       2 |       12 |

Generate GitHub Flavored Markdown (GFM) report:

::

    pytest --md-report --md-report-flavor gfm examples/

GFM rendering result can be seen at `here <https://github.com/thombashi/pytest-md-report/blob/master/examples/gfm_report.md>`__.

Render custom columns from ``pytest.mark`` (``--md-report-mark-cols`` option):

Given test functions decorated with marks such as:

.. code-block:: python

    import pytest

    @pytest.mark.id("TC-001")
    @pytest.mark.priority("high")
    def test_alpha():
        assert True

    @pytest.mark.id("TC-002")
    @pytest.mark.priority("low")
    def test_beta():
        assert True

run pytest with the mark names to render as columns:

::

    pytest --md-report --md-report-color never --md-report-verbose 1 --md-report-mark-cols id priority

::

    |   filepath    |  function  |   id   | priority | passed | SUBTOTAL |
    | ------------- | ---------- | ------ | -------- | -----: | -------: |
    | test_marks.py | test_alpha | TC-001 | high     |      1 |        1 |
    | test_marks.py | test_beta  | TC-002 | low      |      1 |        1 |
    | TOTAL         |            |        |          |      2 |        2 |

Notes:

- The mark's positional args are rendered as a comma-separated string. Keyword args follow as ``key=value``. Marks without args render as ``True``.
- When a function has multiple parametrized cases with different mark values (e.g. via ``pytest.param(..., marks=...)``), values are joined with ``, `` at ``--md-report-verbose 1`` (per-function) and listed individually at ``--md-report-verbose 2`` (per-parameter).
- Custom marks should be `registered <https://docs.pytest.org/en/stable/how-to/mark.html#registering-marks>`__ in your pytest config to avoid ``PytestUnknownMarkWarning``.


Config file examples
--------------------------------------------
You can set configurations with ``pyproject.toml`` or ``setup.cfg`` as follows.

:Example of ``pyproject.toml``:
    .. code-block:: toml

        [tool.pytest.ini_options]
        md_report = true
        md_report_verbose = 0
        md_report_color = "auto"

:Example of ``setup.cfg``:
    .. code-block:: ini

        [tool:pytest]
        md_report = True
        md_report_verbose = 0
        md_report_color = auto


Add report to pull requests
-----------------------------------------------
You can add test reports to pull requests by GitHub actions workflow like the below:

.. code-block:: yaml

    name: md-report - pull request example

    on:
      pull_request:

    jobs:
      run-tests:
        runs-on: ubuntu-latest
        permissions:
          contents: read
          pull-requests: write

        steps:
          - uses: actions/checkout@v4

          - uses: actions/setup-python@v5
            with:
              python-version: '3.12'
              cache: pip

          - name: Install dependencies
            run: pip install --upgrade pytest-md-report

          - name: Run tests
            env:
              REPORT_OUTPUT: md_report.md
            shell: bash
            run: |
              echo "REPORT_FILE=${REPORT_OUTPUT}" >> "$GITHUB_ENV"
              pytest -v --md-report --md-report-flavor gfm --md-report-exclude-outcomes passed skipped xpassed --md-report-output "$REPORT_OUTPUT"

          - name: Render the report to the PR when tests fail
            uses: marocchino/sticky-pull-request-comment@v2
            if: failure()
            with:
              header: test-report
              recreate: true
              path: ${{ env.REPORT_FILE }}

.. figure:: https://cdn.jsdelivr.net/gh/thombashi/pytest-md-report@master/ss/md-report_gha.png
    :scale: 80%
    :alt: https://github.com/thombashi/pytest-md-report/blob/master/ss/md-report_gha.png

    Rendering result


Add report to pull requests: only failed tests
-----------------------------------------------
You can exclude specific test outcomes from the report by using the ``--md-report-exclude-outcomes`` option.
The below example excludes ``passed``, ``skipped``, and ``xpassed`` test outcomes from the report and posts the report to the pull request when tests fail with verbose output.

.. code-block:: yaml

    name: md-report - pull request example

    on:
      pull_request:

    jobs:
      run-tests:
        runs-on: ubuntu-latest
        permissions:
          contents: read
          pull-requests: write

        steps:
          - uses: actions/checkout@v4

          - uses: actions/setup-python@v5
            with:
              python-version: '3.12'
              cache: pip

          - name: Install dependencies
            run: pip install --upgrade pytest-md-report

          - name: Run tests
            env:
              REPORT_OUTPUT: md_report.md
            shell: bash
            run: |
              echo "REPORT_FILE=${report_file}" >> "$GITHUB_ENV"
              pytest -v --md-report --md-report-flavor gfm --md-report-exclude-outcomes passed skipped xpassed --md-report-output "$report_file"

          - name: Render the report to the PR when tests fail
            uses: marocchino/sticky-pull-request-comment@v2
            if: failure()
            with:
              header: test-report
              recreate: true
              path: ${{ env.REPORT_FILE }}

.. figure:: https://cdn.jsdelivr.net/gh/thombashi/pytest-md-report@master/ss/md-report_exclude_outcomes_verbose_output.png
    :scale: 80%
    :alt: https://github.com/thombashi/pytest-md-report/blob/master/ss/md-report_exclude_outcomes_verbose_output.png

    Rendering result


Add reports to the job summary of the GitHub action workflow runs
-----------------------------------------------------------------------------
The below example adds test reports to the job summary of the GitHub action workflow runs when tests fail.

.. code-block:: yaml

    name: md-report - job summary example

    on:
      pull_request:

    jobs:
      run-tests:
        runs-on: ${{ matrix.os }}
        strategy:
          fail-fast: false
          matrix:
            os: [ubuntu-latest, windows-latest]

        steps:
          - uses: actions/checkout@v4

          - uses: actions/setup-python@v5
            with:
              python-version: '3.12'
              cache: pip

          - name: Install dependencies
            run: pip install --upgrade pytest-md-report

          - name: Run tests
            env:
              REPORT_OUTPUT: md_report.md
            shell: bash
            run: |
              echo "REPORT_FILE=${REPORT_OUTPUT}" >> "$GITHUB_ENV"
              pytest -v --md-report --md-report-flavor gfm --md-report-exclude-outcomes passed skipped xpassed --md-report-output "$REPORT_OUTPUT"

          - name: Output reports to the job summary when tests fail
            if: failure()
            shell: bash
            run: |
              if [ -f "$REPORT_FILE" ]; then
                echo "<details><summary>Failed Test Report</summary>" >> $GITHUB_STEP_SUMMARY
                echo "" >> $GITHUB_STEP_SUMMARY
                cat "$REPORT_FILE" >> $GITHUB_STEP_SUMMARY
                echo "" >> $GITHUB_STEP_SUMMARY
                echo "</details>" >> $GITHUB_STEP_SUMMARY
              fi

.. figure:: https://cdn.jsdelivr.net/gh/thombashi/pytest-md-report@master/ss/md-report_job-summary_full.png
    :scale: 80%
    :alt: https://github.com/thombashi/pytest-md-report/blob/master/ss/md-report_job-summary_full.png

    Rendering result


Options
============================================

Command options
--------------------------------------------
::

    generate test outcomes report with markdown table format:
      --md-report           Create a Markdown report. you can also specify the value
                            with PYTEST_MD_REPORT environment variable.
      --md-report-verbose=VERBOSITY_LEVEL
                            Verbosity level for pytest-md-report.
                            0: output test results by test file.
                            1: output test results by test function.
                            2: output test results by test function's parameters.
                            If not set, use the verbosity level of pytest.
                            you can also specify the value with
                            PYTEST_MD_REPORT_VERBOSE environment variable.
      --md-report-output=FILEPATH
                            Path to a file to the outputs test report.
                            Overwrite a file content if the file already exists.
                            you can also specify the value with
                            PYTEST_MD_REPORT_OUTPUT environment variable.
      --md-report-tee       output test report for both standard output and a file.
                            you can also specify the value with PYTEST_MD_REPORT_TEE
                            environment variable.
      --md-report-color={auto,text,never}
                            How coloring output reports.
                            auto: detect the output destination and colorize reports
                            appropriately with the output.
                            for terminal output, render colored (text and
                            background) reports using ANSI escape codes.
                            for file output, render the report without color.
                            text: render colored text reports by using ANSI escape
                            codes.
                            never: render report without color.
                            Defaults to 'auto'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_COLOR environment variable.
      --md-report-margin=MARGIN
                            Margin size for each cell.
                            Defaults to 1.
                            you can also specify the value with
                            PYTEST_MD_REPORT_MARGIN environment variable.
      --md-report-zeros={number,empty}
                            Rendering method for results of zero values.
                            number: render as a digit number (0).
                            empty: not rendering.
                            Automatically set to 'number' when the CI environment
                            variable is set to
                            TRUE (case insensitive) to display reports correctly at
                            CI services.
                            Defaults to 'number'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_ZEROS environment variable.
      --md-report-success-color=MD_REPORT_SUCCESS_COLOR
                            Text color of succeeded results.
                            Specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            Defaults to 'light_green'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_SUCCESS_COLOR environment variable.
      --md-report-skip-color=MD_REPORT_SKIP_COLOR
                            Text color of skipped results.
                            Specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            Defaults to 'light_yellow'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_SKIP_COLOR environment variable.
      --md-report-error-color=MD_REPORT_ERROR_COLOR
                            Text color of failed results.
                            Specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            Defaults to 'light_red'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_ERROR_COLOR environment variable.
      --md-report-flavor={common_mark,github,gfm,jekyll,kramdown}
                            Markdown flavor of the output report.
                            Defaults to 'common_mark'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_FLAVOR environment variable.
      --md-report-exclude-outcomes=MD_REPORT_EXCLUDE_OUTCOMES [MD_REPORT_EXCLUDE_OUTCOMES ...]
                            List of test outcomes to exclude from the report.
                            When specifying as an environment variable, pass a
                            comma-separated string
                            (e.g. 'passed,skipped').
                            Defaults to '[]'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_EXCLUDE_OUTCOMES environment variable.
      --md-report-mark-cols=MD_REPORT_MARK_COLS [MD_REPORT_MARK_COLS ...]
                            List of pytest mark names to render as additional report
                            columns.
                            For each test, the mark's args (and kwargs) are rendered
                            in the
                            corresponding column. When the same mark appears
                            multiple times for
                            a row (e.g. via parametrize), values are joined with ' |
                            '.
                            When specifying as an environment variable, pass a
                            comma-separated
                            string (e.g. 'id,priority').
                            Defaults to '[]'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_MARK_COLS environment variable.


ini-options
--------------------------------------------
[pytest] ini-options in the first ``pytest.ini``/``tox.ini``/``setup.cfg``/``pyproject.toml (pytest 6.0.0 or later)`` file found:

::

  md_report (bool):     Create a Markdown report.
  md_report_verbose (string):
                        Verbosity level for pytest-md-report. 0: output test
                        results by test file. 1: output test results by test
                        function. 2: output test results by test function's
                        parameters. If not set, use the verbosity level of
                        pytest.
  md_report_color (string):
                        How coloring output reports. auto: detect the output
                        destination and colorize reports appropriately with the
                        output. for terminal output, render colored (text and
                        background) reports using ANSI escape codes. for file
                        output, render the report without color. text: render
                        colored text reports by using ANSI escape codes. never:
                        render report without color. Defaults to 'auto'.
  md_report_output (string):
                        Path to a file to the outputs test report. Overwrite a
                        file content if the file already exists.
  md_report_tee (string):
                        output test report for both standard output and a file.
  md_report_margin (string):
                        Margin size for each cell. Defaults to 1.
  md_report_zeros (string):
                        Rendering method for results of zero values. number:
                        render as a digit number (0). empty: not rendering.
                        Automatically set to 'number' when the CI environment
                        variable is set to TRUE (case insensitive) to display
                        reports correctly at CI services. Defaults to 'number'.
  md_report_success_color (string):
                        Text color of succeeded results. Specify a color name
                        (one of the black/red/green/yellow/blue/magenta/cyan/whi
                        te/lightblack/lightred/lightgreen/lightyellow/lightblue/
                        lightmagenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). Defaults to 'light_green'.
  md_report_skip_color (string):
                        Text color of skipped results. Specify a color name (one
                        of the black/red/green/yellow/blue/magenta/cyan/white/li
                        ghtblack/lightred/lightgreen/lightyellow/lightblue/light
                        magenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). Defaults to 'light_yellow'.
  md_report_error_color (string):
                        Text color of failed results. Specify a color name (one
                        of the black/red/green/yellow/blue/magenta/cyan/white/li
                        ghtblack/lightred/lightgreen/lightyellow/lightblue/light
                        magenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). Defaults to 'light_red'.
  md_report_flavor (string):
                        Markdown flavor of the output report. Defaults to
                        'common_mark'.
  md_report_exclude_outcomes (args):
                        List of test outcomes to exclude from the report. When
                        specifying as an environment variable, pass a
                        comma-separated string (e.g. 'passed,skipped'). Defaults
                        to '[]'.
  md_report_mark_cols (args):
                        List of pytest mark names to render as additional report
                        columns. For each test, the mark's args (and kwargs) are
                        rendered in the corresponding column. When the same mark
                        appears multiple times for a row (e.g. via parametrize),
                        values are joined with ' | '. When specifying as an
                        environment variable, pass a comma-separated string
                        (e.g. 'id,priority'). Defaults to '[]'.


Dependencies
============================================
- Python 3.10+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/pytest-md-report/network/dependencies>`__
