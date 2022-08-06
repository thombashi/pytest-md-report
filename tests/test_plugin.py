import difflib
import sys
from textwrap import dedent

import pytest


PYFILE_PASS_TEST = dedent(
    """\
    import pytest

    def test_pass():
        assert True
    """
)
PYFILE_SKIP_TEST = dedent(
    """\
    import pytest

    def test_skipped():
        pytest.skip()
    """
)
PYFILE_MIX_TESTS = dedent(
    """\
    import pytest

    def test_pass():
        assert True

    def test_failed():
        assert False

    def test_skipped():
        pytest.skip()

    def test_error(invalid_fixture):
        pass

    @pytest.mark.xfail()
    def test_xfailed():
        assert False

    @pytest.mark.xfail()
    def test_xpassed():
        assert True
    """
)


def print_test_result(expected, actual, error=None):
    print(f"[expected]\n{expected}\n")
    print(f"[actual]\n{actual}\n")

    if error:
        print(error, file=sys.stderr)

    print("----------------------------------------")
    d = difflib.Differ()
    diff = d.compare(expected.splitlines(), actual.splitlines())
    for d in diff:
        print(d)


def test_pytest_md_report(testdir):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    expected = dedent(
        """\
        |         filepath         | passed | failed | error | skipped | xfailed | xpassed | SUBTOTAL |
        | ------------------------ | -----: | -----: | ----: | ------: | ------: | ------: | -------: |
        | test_pytest_md_report.py |      1 |      1 |     1 |       1 |       1 |       1 |        6 |
        | TOTAL                    |      1 |      1 |     1 |       1 |       1 |       1 |        6 |"""
    )
    result = testdir.runpytest("--md-report", "--md-report-color", "never")
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)

    assert out == expected


def test_pytest_md_report_output(testdir):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    expected = dedent(
        """\
        |            filepath             | passed | failed | error | skipped | xfailed | xpassed | SUBTOTAL |
        | ------------------------------- | -----: | -----: | ----: | ------: | ------: | ------: | -------: |
        | test_pytest_md_report_output.py |      1 |      1 |     1 |       1 |       1 |       1 |        6 |
        | TOTAL                           |      1 |      1 |     1 |       1 |       1 |       1 |        6 |"""
    )
    output_filepath = testdir.tmpdir.join("report.md")
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-output", output_filepath
    )
    out = "\n".join(result.outlines[-4:])
    assert out != expected
    with open(output_filepath) as f:
        assert f.read().strip() == expected

    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-output",
        output_filepath,
        "--md-report-tee",
    )
    out = "\n".join(result.outlines[-4:])
    assert out == expected
    with open(output_filepath) as f:
        assert f.read().strip() == expected


def test_pytest_md_report_margin(testdir):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    expected = dedent(
        """\
        |           filepath            |passed|failed|error|skipped|xfailed|xpassed|SUBTOTAL|
        |-------------------------------|-----:|-----:|----:|------:|------:|------:|-------:|
        |test_pytest_md_report_margin.py|     1|     1|    1|      1|      1|      1|       6|
        |TOTAL                          |     1|     1|    1|      1|      1|      1|       6|"""
    )
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-margin", "0"
    )
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)

    assert out == expected


def test_pytest_md_report_zeros(testdir):
    testdir.makepyfile(test_passed=PYFILE_PASS_TEST)
    testdir.makepyfile(test_skipped=PYFILE_SKIP_TEST)

    expected = dedent(
        """\
        |    filepath     | passed | skipped | SUBTOTAL |
        | --------------- | -----: | ------: | -------: |
        | test_passed.py  |      1 |         |        1 |
        | test_skipped.py |        |       1 |        1 |
        | TOTAL           |      1 |       1 |        2 |"""
    )
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-zeros", "empty"
    )
    out = "\n".join(result.outlines[-5:])
    print_test_result(expected=expected, actual=out)

    assert out == expected


@pytest.mark.parametrize(
    ["color_option"],
    [
        ["--md-report-success-color"],
        ["--md-report-skip-color"],
        ["--md-report-error-color"],
    ],
)
def test_pytest_md_report_results_color(testdir, color_option):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    org_out = "\n".join(testdir.runpytest("--md-report").outlines[-4:])
    ch_color_out = "\n".join(
        testdir.runpytest("--md-report", color_option, "#ff2a2a").outlines[-4:]
    )

    assert org_out != ch_color_out
