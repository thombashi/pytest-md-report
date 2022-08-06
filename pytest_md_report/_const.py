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
    MD_REPORT = (OPTION_PREFIX, "create markdown report.")
    MD_REPORT_VERBOSE = (
        f"{OPTION_PREFIX}-verbose",
        dedent(
            """\
            verbosity level for pytest-md-report. if not set, using verbosity level of pytest.
            defaults to 0.
            """
        ),
    )
    MD_REPORT_OUTPUT = (
        f"{OPTION_PREFIX}-output",
        dedent(
            """\
            path to a file that outputs test report.
            overwrite a file content if the file already exists.
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
            auto: display colored (text and background) reports by using ANSI escape codes.
            text: display colored (text) reports by using ANSI escape codes.
            never: display report without color.
            defaults to '{default}'.
            """
        ).format(default=Default.COLOR),
    )
    MD_REPORT_MARGIN = (
        f"{OPTION_PREFIX}-margin",
        dedent(
            """\
            margin size for each cells.
            defaults to {default}.
            """
        ).format(default=Default.MARGIN),
    )
    MD_REPORT_ZEROS = (
        f"{OPTION_PREFIX}-zeros",
        dedent(
            """\
            rendering method for results of zero values.
            number: render as a digit number (0).
            empty: not rendering.
            defaults to {default}. defaults to empty when execution in ci.
            """
        ).format(default=Default.ZEROS),
    )
    MD_REPORT_SUCCESS_COLOR = (
        f"{OPTION_PREFIX}-success-color",
        dedent(
            """\
            text color of succeeded results.
            specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            defaults to {default}.
            """
        ).format(names=COLOR_NAMES, default=Default.FGColor.SUCCESS),
    )
    MD_REPORT_SKIP_COLOR = (
        f"{OPTION_PREFIX}-skip-color",
        dedent(
            """\
            text color of skipped results.
            specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            defaults to {default}.
            """
        ).format(names=COLOR_NAMES, default=Default.FGColor.SKIP),
    )
    MD_REPORT_ERROR_COLOR = (
        f"{OPTION_PREFIX}-error-color",
        dedent(
            """\
            text color of failed results.
            specify a color name (one of the {names}) or a color code (e.g. #ff1020).
            defaults to {default}.
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
