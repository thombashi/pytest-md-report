from enum import Enum, unique
from textwrap import dedent

from tcolorpy import AnsiFGColor


COLOR_NAMES = "/".join([style.name.lower() for style in list(AnsiFGColor)])


class Header:
    FILEPATH = "filepath"
    TESTFUNC = "function"
    SUBTOTAL = "SUBTOTAL"


class ColorPolicy:
    AUTO = "auto"
    TEXT = "text"
    NEVER = "never"
    LIST = (AUTO, TEXT, NEVER)


class ZerosRender:
    NUMBER = "number"
    EMPTY = "empty"
    LIST = (NUMBER, EMPTY)


class FGColor:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIP = "SKIP"
    GRAYOUT = "GRAYOUT"


class BGColor:
    EVEN_ROW = "#202020"
    ODD_ROW = "black"
    TOTAL_ROW = "#000000"


class Default:
    COLOR = ColorPolicy.AUTO
    MARGIN = 1
    ZEROS = ZerosRender.NUMBER

    class FGColor:
        SUCCESS = "light_green"
        ERROR = "light_red"
        SKIP = "light_yellow"
        GRAYOUT = "light_black"


OPTION_PREFIX = "md-report"


@unique
class Option(Enum):
    MD_REPORT = (OPTION_PREFIX, "Create Markdown report.")
    MD_REPORT_VERBOSE = (
        f"{OPTION_PREFIX}-verbose",
        dedent(
            """\
            Verbosity level for pytest-md-report.
            If not set, use the verbosity level of pytest.
            Defaults to 0.
            """
        ),
    )
    MD_REPORT_OUTPUT = (
        f"{OPTION_PREFIX}-output",
        dedent(
            """\
            Path to a file to the outputs test report.
            Overwrite a file content if the file already exists.
            """
        ),
    )
    MD_REPORT_TEE = (
        f"{OPTION_PREFIX}-tee",
        "output test report for both standard output and a file.",
    )
    MD_REPORT_COLOR = (
        f"{OPTION_PREFIX}-color",
        dedent(
            """\
            How to color output reports.
            auto: render colored (text and background) reports using ANSI escape codes.
            text: render colored text reports by using ANSI escape codes.
            never: render report without color.
            Defaults to '{default}'.
            """
        ).format(default=Default.COLOR),
    )
    MD_REPORT_MARGIN = (
        f"{OPTION_PREFIX}-margin",
        dedent(
            """\
            Margin size for each cell.
            Defaults to {default}.
            """
        ).format(default=Default.MARGIN),
    )
    MD_REPORT_ZEROS = (
        f"{OPTION_PREFIX}-zeros",
        dedent(
            """\
            Rendering method for results of zero values.
            number: render as a digit number (0).
            empty: not rendering.
            Defaults to 'empty' when CI environment variable is set to TRUE (case insensitive);
            otherwise '{default}'.
            """
        ).format(default=Default.ZEROS),
    )
    MD_REPORT_SUCCESS_COLOR = (
        f"{OPTION_PREFIX}-success-color",
        dedent(
            """\
            Text color of succeeded results.
            Specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            Defaults to '{default}'.
            """
        ).format(names=COLOR_NAMES, default=Default.FGColor.SUCCESS),
    )
    MD_REPORT_SKIP_COLOR = (
        f"{OPTION_PREFIX}-skip-color",
        dedent(
            """\
            Text color of skipped results.
            Specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            Defaults to '{default}'.
            """
        ).format(names=COLOR_NAMES, default=Default.FGColor.SKIP),
    )
    MD_REPORT_ERROR_COLOR = (
        f"{OPTION_PREFIX}-error-color",
        dedent(
            """\
            Text color of failed results.
            Specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            Defaults to '{default}'.
            """
        ).format(names=COLOR_NAMES, default=Default.FGColor.ERROR),
    )

    @property
    def cmdoption_str(self) -> str:
        return "--" + self.__name.lower()

    @property
    def envvar_str(self) -> str:
        return "PYTEST_" + self.__name.replace("-", "_").upper()

    @property
    def inioption_str(self) -> str:
        return self.__name.replace("-", "_").lower()

    @property
    def help_msg(self) -> str:
        return self.__help_msg

    def __init__(self, name: str, help_msg: str) -> None:
        self.__name = name.strip()
        self.__help_msg = help_msg


class HelpMsg:
    EXTRA_MSG_TEMPLATE = " you can also specify the value with {} environment variable."
