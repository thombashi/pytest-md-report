import difflib
import sys
from textwrap import dedent

import pytest
from pytablewriter.writer.text import MarkdownFlavor

from pytest_md_report.plugin import (
    ColorPolicy,
    extract_file_color_policy,
    is_apply_ansi_escape_to_file,
    is_apply_ansi_escape_to_term,
)


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


@pytest.mark.parametrize(
    ["color_policy", "is_output_file", "expected"],
    [
        [ColorPolicy.AUTO, False, True],
        [ColorPolicy.AUTO, True, False],
        [ColorPolicy.TEXT, False, True],
        [ColorPolicy.TEXT, True, True],
        [ColorPolicy.NEVER, False, False],
        [ColorPolicy.NEVER, True, False],
    ],
)
def test_is_apply_ansi_escape_to_file(color_policy, is_output_file, expected):
    assert is_apply_ansi_escape_to_file(color_policy, is_output_file) == expected


@pytest.mark.parametrize(
    ["color_policy", "expected"],
    [
        [ColorPolicy.AUTO, True],
        [ColorPolicy.TEXT, True],
        [ColorPolicy.NEVER, False],
    ],
)
def test_is_apply_ansi_escape_to_term(color_policy, expected):
    assert is_apply_ansi_escape_to_term(color_policy) == expected


@pytest.mark.parametrize(
    ["color_policy", "is_output_file", "flavor", "expected"],
    [
        [ColorPolicy.AUTO, False, MarkdownFlavor.GFM, ColorPolicy.AUTO],
        [ColorPolicy.AUTO, True, MarkdownFlavor.GFM, ColorPolicy.AUTO],
        [ColorPolicy.AUTO, False, MarkdownFlavor.COMMON_MARK, ColorPolicy.AUTO],
        [ColorPolicy.AUTO, True, MarkdownFlavor.COMMON_MARK, ColorPolicy.NEVER],
        [ColorPolicy.TEXT, False, MarkdownFlavor.GFM, ColorPolicy.TEXT],
        [ColorPolicy.TEXT, True, MarkdownFlavor.GFM, ColorPolicy.TEXT],
        [ColorPolicy.NEVER, False, MarkdownFlavor.GFM, ColorPolicy.NEVER],
        [ColorPolicy.NEVER, True, MarkdownFlavor.GFM, ColorPolicy.NEVER],
    ],
)
def test_extract_file_color_policy(color_policy, is_output_file, flavor, expected):
    assert extract_file_color_policy(color_policy, is_output_file, flavor) == expected


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
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-output",
        output_filepath,
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


def test_pytest_md_report_flavor(testdir):
    testdir.makepyfile(test_passed=PYFILE_PASS_TEST)
    testdir.makepyfile(test_skipped=PYFILE_SKIP_TEST)
    out_dir = testdir.mkdir("outputs")
    out_file = out_dir.join("report.md")
    testdir.runpytest("--md-report", "--md-report-flavor", "github", "--md-report-output", out_file)

    with open(out_file) as f:
        report = f.read()
        print(report)
        assert (
            report
            == r"""|    filepath     | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{skipped}}$$ | SUBTOTAL |
| --------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{test\\_passed.py}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{test\\_skipped.py}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{2}}$$ |
"""
        )


def test_pytest_md_report_exclude_outcomes(testdir):
    testdir.makepyfile(PYFILE_MIX_TESTS)
    expected = dedent(
        """\
        |                 filepath                  | failed | error | xfailed | SUBTOTAL |
        | ----------------------------------------- | -----: | ----: | ------: | -------: |
        | test_pytest_md_report_exclude_outcomes.py |      1 |     1 |       1 |        3 |
        | TOTAL                                     |      1 |     1 |       1 |        6 |
        """
    )
    output_filepath = testdir.tmpdir.join("report.md")
    testdir.runpytest(
        "--md-report",
        "--md-report-exclude-outcomes",
        "passed",
        "skipped",
        "xpassed",
        "--md-report-output",
        output_filepath,
    )
    with open(output_filepath) as f:
        report = f.read()
        print(report)
        assert report == expected
