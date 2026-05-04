import difflib
import re
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
PYFILE_PARAMETIZED_TESTS = dedent(
    """\
    import pytest

    @pytest.mark.parametrize("param", [1, 2, 3])
    def test_param(param):
        assert param == 1
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


def test_pytest_md_report_verbose(testdir):
    testdir.makepyfile(PYFILE_PARAMETIZED_TESTS)
    expected = dedent(
        """\
        |             filepath             |  function  | passed | failed | SUBTOTAL |
        | -------------------------------- | ---------- | -----: | -----: | -------: |
        | test_pytest_md_report_verbose.py | test_param |      1 |      2 |        3 |
        | TOTAL                            |            |      1 |      2 |        3 |"""
    )
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-verbose", "1"
    )
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)
    assert out == expected

    expected = dedent(
        """\
        |             filepath             |  function  | params | passed | failed | SUBTOTAL |
        | -------------------------------- | ---------- | -----: | -----: | -----: | -------: |
        | test_pytest_md_report_verbose.py | test_param |      1 |      1 |      0 |        1 |
        | test_pytest_md_report_verbose.py | test_param |      2 |      0 |      1 |        1 |
        | test_pytest_md_report_verbose.py | test_param |      3 |      0 |      1 |        1 |
        | TOTAL                            |            |        |      1 |      2 |        3 |"""
    )
    result = testdir.runpytest(
        "--md-report", "--md-report-color", "never", "--md-report-verbose", "2"
    )
    out = "\n".join(result.outlines[-6:])
    print_test_result(expected=expected, actual=out)
    assert out == expected


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


PYFILE_MARKED_TESTS = dedent(
    """\
    import pytest

    @pytest.mark.id("TC-001")
    @pytest.mark.priority("high")
    def test_alpha():
        assert True

    @pytest.mark.id("TC-002")
    @pytest.mark.priority("low")
    def test_beta():
        assert True

    def test_gamma():
        assert True
    """
)

PYFILE_MARKED_PARAMETRIZED_TESTS = dedent(
    """\
    import pytest

    @pytest.mark.parametrize(
        "param",
        [
            pytest.param(1, marks=pytest.mark.id("TC-101")),
            pytest.param(2, marks=pytest.mark.id("TC-102")),
        ],
    )
    def test_param(param):
        assert True
    """
)


def test_pytest_md_report_mark_cols_verbose1(testdir):
    testdir.makepyfile(test_marks=PYFILE_MARKED_TESTS)
    expected = dedent(
        """\
        |   filepath    |  function  |   id   | priority | passed | SUBTOTAL |
        | ------------- | ---------- | ------ | -------- | -----: | -------: |
        | test_marks.py | test_alpha | TC-001 | high     |      1 |        1 |
        | test_marks.py | test_beta  | TC-002 | low      |      1 |        1 |
        | test_marks.py | test_gamma |        |          |      1 |        1 |
        | TOTAL         |            |        |          |      3 |        3 |"""
    )
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-mark-cols",
        "id",
        "priority",
    )
    out = "\n".join(result.outlines[-6:])
    print_test_result(expected=expected, actual=out)
    assert out == expected


def test_pytest_md_report_mark_cols_aggregate_parametrize(testdir):
    testdir.makepyfile(test_marks_param=PYFILE_MARKED_PARAMETRIZED_TESTS)
    expected = dedent(
        """\
        |      filepath       |  function  |       id       | passed | SUBTOTAL |
        | ------------------- | ---------- | -------------- | -----: | -------: |
        | test_marks_param.py | test_param | TC-101, TC-102 |      2 |        2 |
        | TOTAL               |            |                |      2 |        2 |"""
    )
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-mark-cols",
        "id",
    )
    out = "\n".join(result.outlines[-4:])
    print_test_result(expected=expected, actual=out)
    assert out == expected


def test_pytest_md_report_mark_cols_verbose2(testdir):
    testdir.makepyfile(test_marks_param=PYFILE_MARKED_PARAMETRIZED_TESTS)
    expected = dedent(
        """\
        |      filepath       |  function  | params |   id   | passed | SUBTOTAL |
        | ------------------- | ---------- | -----: | ------ | -----: | -------: |
        | test_marks_param.py | test_param |      1 | TC-101 |      1 |        1 |
        | test_marks_param.py | test_param |      2 | TC-102 |      1 |        1 |
        | TOTAL               |            |        |        |      2 |        2 |"""
    )
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "2",
        "--md-report-mark-cols",
        "id",
    )
    out = "\n".join(result.outlines[-5:])
    print_test_result(expected=expected, actual=out)
    assert out == expected


PYFILE_DURATION_TESTS = dedent(
    """\
    import time

    import pytest

    def test_a():
        time.sleep(0.02)
        assert True

    def test_b():
        time.sleep(0.04)
        assert True

    @pytest.mark.parametrize("p", [1, 2])
    def test_param(p):
        time.sleep(0.01)
        assert True
    """
)


def _parse_md_table_row(line: str) -> list[str]:
    parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return parts


def _extract_table(outlines: list[str]) -> list[list[str]]:
    table: list[list[str]] = []
    for line in outlines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if set(stripped.replace("|", "").replace(" ", "").replace(":", "")) <= {"-"}:
            continue
        table.append(_parse_md_table_row(line))
    return table


def test_pytest_md_report_show_duration_header(testdir):
    testdir.makepyfile(PYFILE_DURATION_TESTS)
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-show-duration",
    )
    table = _extract_table(result.outlines)
    assert table, "no markdown table found in output"
    headers = table[0]
    assert headers[-1] == "duration"
    assert headers[-2] == "SUBTOTAL"


def test_pytest_md_report_show_duration_off_by_default(testdir):
    testdir.makepyfile(PYFILE_DURATION_TESTS)
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
    )
    table = _extract_table(result.outlines)
    assert table, "no markdown table found in output"
    headers = table[0]
    assert "duration" not in headers


def test_pytest_md_report_show_duration_total_aggregates_rows(testdir):
    testdir.makepyfile(PYFILE_DURATION_TESTS)
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-show-duration",
    )
    table = _extract_table(result.outlines)
    headers = table[0]
    duration_idx = headers.index("duration")

    data_rows = table[1:]
    assert data_rows
    assert data_rows[-1][0] == "TOTAL"

    pattern = re.compile(r"^\d+\.\d{3}$")
    row_durations = []
    for row in data_rows[:-1]:
        cell = row[duration_idx]
        assert pattern.match(cell), f"unexpected duration cell format: {cell!r}"
        row_durations.append(float(cell))

    total_cell = data_rows[-1][duration_idx]
    assert pattern.match(total_cell), f"unexpected TOTAL duration format: {total_cell!r}"
    total_value = float(total_cell)

    # Each row is rounded independently, so the reported TOTAL can drift from
    # the sum of rounded row cells by up to ~(num_rows * 0.5) of the last
    # decimal. Allow a generous tolerance to absorb that rounding noise.
    assert total_value == pytest.approx(sum(row_durations), abs=len(row_durations) * 1e-3)
    assert total_value > 0.0


def test_pytest_md_report_show_duration_aggregates_parametrize_at_verbose1(testdir):
    testdir.makepyfile(test_dur=PYFILE_DURATION_TESTS)
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-show-duration",
    )
    table = _extract_table(result.outlines)
    headers = table[0]
    duration_idx = headers.index("duration")
    function_idx = headers.index("function")

    param_row = next(row for row in table[1:] if row[function_idx] == "test_param")
    a_row = next(row for row in table[1:] if row[function_idx] == "test_a")

    param_duration = float(param_row[duration_idx])
    a_duration = float(a_row[duration_idx])

    assert param_duration > a_duration


def test_pytest_md_report_show_duration_precision(testdir):
    testdir.makepyfile(PYFILE_DURATION_TESTS)
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
        "--md-report-show-duration",
        "--md-report-duration-precision",
        "5",
    )
    table = _extract_table(result.outlines)
    headers = table[0]
    duration_idx = headers.index("duration")

    pattern = re.compile(r"^\d+\.\d{5}$")
    for row in table[1:]:
        cell = row[duration_idx]
        assert pattern.match(cell), f"expected 5-decimal precision, got {cell!r}"


def test_pytest_md_report_show_duration_via_envvar(testdir, monkeypatch):
    testdir.makepyfile(PYFILE_DURATION_TESTS)
    monkeypatch.setenv("PYTEST_MD_REPORT_SHOW_DURATION", "true")
    result = testdir.runpytest(
        "--md-report",
        "--md-report-color",
        "never",
        "--md-report-verbose",
        "1",
    )
    table = _extract_table(result.outlines)
    assert table[0][-1] == "duration"


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
