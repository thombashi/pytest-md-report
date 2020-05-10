import difflib
import sys
from textwrap import dedent


PYFILE_PASS_TEST = dedent(
    """\
    import pytest

    def test_pass():
        assert True
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
    print("[expected]\n{}\n".format(expected))
    print("[actual]\n{}\n".format(actual))

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
        |         filepath         | passed | failed | error | skipped | xfailed | xpassed |
        |--------------------------|-------:|-------:|------:|--------:|--------:|--------:|
        | test_pytest_md_report.py |      1 |      1 |     1 |       1 |       1 |       1 |
        | TOTAL                    |      1 |      1 |     1 |       1 |       1 |       1 |"""
    )
    result = testdir.runpytest("--md-report", "--md-report-color", "never")
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)

    assert out == expected


def test_pytest_md_report_margin(testdir):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    expected = dedent(
        """\
        |           filepath            |passed|failed|error|skipped|xfailed|xpassed|
        |-------------------------------|-----:|-----:|----:|------:|------:|------:|
        |test_pytest_md_report_margin.py|     1|     1|    1|      1|      1|      1|
        |TOTAL                          |     1|     1|    1|      1|      1|      1|"""
    )
    result = testdir.runpytest("--md-report", "--md-report-color", "never", "--md-report-margin", 0)
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)

    assert out == expected


def test_pytest_md_report_zeros(testdir):
    testdir.makepyfile(PYFILE_PASS_TEST)
    expected = dedent(
        """\
        |            filepath            | passed | failed | error | skipped | xfailed | xpassed |
        |--------------------------------|-------:|--------|-------|---------|---------|---------|
        | test_pytest_md_report_zeros.py |      1 |        |       |         |         |         |
        | TOTAL                          |      1 |        |       |         |         |         |"""
    )
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-zeros", "empty"
    )
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)

    assert out == expected
