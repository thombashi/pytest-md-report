.. contents:: **pytest-md-report**
   :backlinks: top
   :depth: 2


Summary
============================================
.. image:: https://badge.fury.io/py/pytest-md-report.svg
    :target: https://badge.fury.io/py/pytest-md-report
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/pytest-md-report.svg
    :target: https://pypi.org/project/pytest-md-report
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/pytest-md-report.svg
    :target: https://pypi.org/project/pytest-md-report
    :alt: Supported Python implementations

.. image:: https://github.com/thombashi/pytest-md-report/workflows/Tests/badge.svg
    :target: https://github.com/thombashi/pytest-md-report/actions?query=workflow%3ATests
    :alt: Linux/macOS/Windows CI status

.. image:: https://github.com/thombashi/pytest-md-report/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/thombashi/pytest-md-report/actions/workflows/codeql-analysis.yml
    :alt: CodeQL

A pytest plugin to make a test results report with Markdown table format.


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

Not rendering results of zero value (``--md-report-zeros emmpty`` option):

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


Options
============================================

Command options
--------------------------------------------
::

    make test results report with markdown table format:
      --md-report           create markdown report. you can also specify the value
                            with PYTEST_MD_REPORT environment variable.
      --md-report-verbose=VERBOSITY_LEVEL
                            verbosity level for pytest-md-report. if not set, using
                            verbosity level of pytest.
                            defaults to 0.
                            you can also specify the value with
                            PYTEST_MD_REPORT_VERBOSE environment variable.
      --md-report-output=FILEPATH
                            path to a file that outputs test report.
                            overwrite a file content if the file already exists.
                            you can also specify the value with
                            PYTEST_MD_REPORT_OUTPUT environment variable.
      --md-report-tee       output test report for both standard output and a file.
                            you can also specify the value with PYTEST_MD_REPORT_TEE
                            environment variable.
      --md-report-color={auto,text,never}
                            auto: display colored (text and background) reports by
                            using ANSI escape codes.
                            text: display colored (text) reports by using ANSI
                            escape codes.
                            never: display report without color.
                            defaults to 'auto'.
                            you can also specify the value with
                            PYTEST_MD_REPORT_COLOR environment variable.
      --md-report-margin=MARGIN
                            margin size for each cells.
                            defaults to 1.
                            you can also specify the value with
                            PYTEST_MD_REPORT_MARGIN environment variable.
      --md-report-zeros={number,empty}
                            rendering method for results of zero values.
                            number: render as a digit number (0).
                            empty: not rendering.
                            defaults to number. defaults to empty when execution in
                            ci.
                            you can also specify the value with
                            PYTEST_MD_REPORT_ZEROS environment variable.
      --md-report-success-color=MD_REPORT_SUCCESS_COLOR
                            text color of succeeded results.
                            specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            defaults to light_green.
                            you can also specify the value with
                            PYTEST_MD_REPORT_SUCCESS_COLOR environment variable.
      --md-report-skip-color=MD_REPORT_SKIP_COLOR
                            text color of skipped results.
                            specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            defaults to light_yellow.
                            you can also specify the value with
                            PYTEST_MD_REPORT_SKIP_COLOR environment variable.
      --md-report-error-color=MD_REPORT_ERROR_COLOR
                            text color of failed results.
                            specify a color name (one of the black/red/green/yellow/
                            blue/magenta/cyan/white/lightblack/lightred/lightgreen/l
                            ightyellow/lightblue/lightmagenta/lightcyan/lightwhite)
                            or a color code (e.g. #ff1020).
                            defaults to light_red.
                            you can also specify the value with
                            PYTEST_MD_REPORT_ERROR_COLOR environment variable.

ini-options
--------------------------------------------
[pytest] ini-options in the first ``pytest.ini``/``tox.ini``/``setup.cfg``/``pyproject.toml (pytest 6.0.0 or later)`` file found:

::

  md_report (bool):     create markdown report.
  md_report_verbose (string):
                        verbosity level for pytest-md-report. if not set, using
                        verbosity level of pytest. defaults to 0.
  md_report_color (string):
                        auto: display colored (text and background) reports by
                        using ANSI escape codes. text: display colored (text)
                        reports by using ANSI escape codes. never: display
                        report without color. defaults to 'auto'.
  md_report_output (string):
                        path to a file that outputs test report. overwrite a
                        file content if the file already exists.
  md_report_tee (string):
                        output test report for both standard output and a file.
  md_report_margin (string):
                        margin size for each cells. defaults to 1.
  md_report_zeros (string):
                        rendering method for results of zero values. number:
                        render as a digit number (0). empty: not rendering.
                        defaults to number. defaults to empty when execution in
                        ci.
  md_report_success_color (string):
                        text color of succeeded results. specify a color name
                        (one of the black/red/green/yellow/blue/magenta/cyan/whi
                        te/lightblack/lightred/lightgreen/lightyellow/lightblue/
                        lightmagenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). defaults to light_green.
  md_report_skip_color (string):
                        text color of skipped results. specify a color name (one
                        of the black/red/green/yellow/blue/magenta/cyan/white/li
                        ghtblack/lightred/lightgreen/lightyellow/lightblue/light
                        magenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). defaults to light_yellow.
  md_report_error_color (string):
                        text color of failed results. specify a color name (one
                        of the black/red/green/yellow/blue/magenta/cyan/white/li
                        ghtblack/lightred/lightgreen/lightyellow/lightblue/light
                        magenta/lightcyan/lightwhite) or a color code (e.g.
                        #ff1020). defaults to light_red.


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


Dependencies
============================================
- Python 3.6+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/pytest-md-report/network/dependencies>`__
