import pytest

from pytest_md_report._const import Option


@pytest.mark.parametrize(
    ["option"],
    [
        [Option.MD_REPORT],
        [Option.MD_REPORT_VERBOSE],
        [Option.MD_REPORT_COLOR],
        [Option.MD_REPORT_MARGIN],
        [Option.MD_REPORT_ZEROS],
        [Option.MD_REPORT_SUCCESS_COLOR],
        [Option.MD_REPORT_SKIP_COLOR],
        [Option.MD_REPORT_ERROR_COLOR],
    ],
)
def test_pytest_md_report_results_color(option):

    """
    @property
    def cmdoption_str(self) -> str:
        return "--" + replace_symbol(self.__name, "-").lower()

    @property
    def envvar_str(self) -> str:
        return "PYTEST_" + replace_symbol(self.__name, "_").upper()

    @property
    def inioption_str(self) -> str:
    """
