.. contents:: **pytest-md-report**
   :backlinks: top
   :depth: 2


Summary
============================================

.. image:: https://img.shields.io/travis/thombashi/pytest-md-report/master.svg?label=Linux/macOS%20CI
    :target: https://travis-ci.org/thombashi/pytest-md-report
    :alt: Linux/macOS CI status

.. image:: https://img.shields.io/appveyor/ci/thombashi/pytest-md-report/master.svg?label=Windows%20CI
    :target: https://ci.appveyor.com/project/thombashi/pytest-md-report/branch/master
    :alt: Windows CI status

A pytest plugin to make a test results report with Markdown table format.


Installation
============================================
::

    pip install pytest-md-report


Usage
============================================
::

    $ pytest --md-report

Output:

.. figure:: ss/pytest_md_report_example.png
    :scale: 80%
    :alt: output_example

    Output example


Dependencies
============================================
Python 3.5+

- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
- `pytest <https://docs.pytest.org/en/latest/>`__
