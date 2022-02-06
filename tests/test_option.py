from textwrap import dedent

import pytest

from pytest_md_report._const import Option


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


@pytest.mark.parametrize(
    ["option", "value"],
    [
        [Option.MD_REPORT, None],
        [Option.MD_REPORT_VERBOSE, 1],
        [Option.MD_REPORT_COLOR, "auto"],
        [Option.MD_REPORT_MARGIN, 1],
        [Option.MD_REPORT_ZEROS, "empty"],
        [Option.MD_REPORT_SUCCESS_COLOR, "green"],
        [Option.MD_REPORT_SKIP_COLOR, "yellow"],
        [Option.MD_REPORT_ERROR_COLOR, "red"],
    ],
)
def test_pytest_md_report_option(testdir, option, value):
    testdir.makepyfile(PYFILE_MIX_TESTS)

    assert testdir.runpytest(option, value)
