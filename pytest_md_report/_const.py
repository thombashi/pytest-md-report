from enum import Enum, unique
from textwrap import dedent

from pathvalidate import replace_symbol


@unique
class Option(Enum):
    MD_REPORT = "md-report"
    MD_REPORT_VERBOSE = "md-report-verbose"
    MD_REPORT_COLOR = "md-report-color"
    MD_REPORT_MARGIN = "md-report-margin"
    MD_REPORT_ZEROS = "md-report-zeros"

    @property
    def cmdoption_str(self) -> str:
        return "--" + replace_symbol(self.__name, "-").lower()

    @property
    def envvar_str(self) -> str:
        return "PYTEST_" + replace_symbol(self.__name, "_").upper()

    @property
    def inioption_str(self) -> str:
        return replace_symbol(self.__name, "_").lower()

    def __init__(self, name: str) -> None:
        self.__name = name.strip()


class Header:
    FILEPATH = "filepath"
    TESTFUNC = "function"


class ColorPoicy:
    AUTO = "auto"
    TEXT = "text"
    NEVER = "never"
    LIST = (AUTO, TEXT, NEVER)


class ZerosRender:
    NUMBER = "number"
    EMPTY = "empty"
    LIST = (NUMBER, EMPTY)


class FGColor:
    SUCCESS = "light_green"
    ERROR = "light_red"
    SKIP = "light_yellow"
    GRAYOUT = "light_black"


class BGColor:
    EVEN_ROW = "#202020"
    ODD_ROW = "black"


class Default:
    COLOR = ColorPoicy.AUTO
    MARGIN = 1
    ZEROS = ZerosRender.NUMBER


class HelpMsg:
    MD_REPORT = "create markdown report."
    MD_REPORT_VERBOSE = dedent(
        """\
        verbosity level for pytest-md-report. if not set, using verbosity level of pytest.
        defaults to 0.
        """
    )
    MD_REPORT_COLOR = dedent(
        """\
        auto: display colored (text and background) reports by using ANSI escape codes.
        text: display colored (text) reports by using ANSI escape codes.
        never: display report without color.
        defaults to '{default}'.
        """
    ).format(default=Default.COLOR)
    MD_REPORT_MARGIN = dedent(
        """\
        margin size for each cells.
        defaults to {default}.
        """
    ).format(default=Default.MARGIN)
    MD_REPORT_ZEROS = dedent(
        """\
        rendering method for results of zero values.
        number: render as a digit number (0).
        empty: not rendering.
        defaults to {default}.
        """
    ).format(default=Default.ZEROS)
    EXTRA_MSG_TEMPLATE = " you can also specify the value with {} environment variable."
