from enum import Enum, unique
from textwrap import dedent
from typing import Final

from pytablewriter.writer.text import MarkdownFlavor
from tcolorpy import AnsiFGColor


COLOR_NAMES: Final = "/".join([style.name.lower() for style in list(AnsiFGColor)])


class Header:
    FILEPATH: Final = "filepath"
    TESTFUNC: Final = "function"
    SUBTOTAL: Final = "SUBTOTAL"


class ColorPolicy(Enum):
    AUTO = "auto"
    TEXT = "text"
    NEVER = "never"


class ZerosRender:
    NUMBER: Final = "number"
    EMPTY: Final = "empty"
    LIST: Final = (NUMBER, EMPTY)


class FGColor:
    SUCCESS: Final = "SUCCESS"
    ERROR: Final = "ERROR"
    SKIP: Final = "SKIP"
    GRAYOUT: Final = "GRAYOUT"


class BGColor:
    EVEN_ROW: Final = "#202020"
    ODD_ROW: Final = "black"
    TOTAL_ROW: Final = "#000000"


class Default:
    COLOR_POLICY: Final = ColorPolicy.AUTO
    MARGIN: Final = 1
    MARKDOWN_FLAVOR: Final = MarkdownFlavor.COMMON_MARK
    ZEROS: Final = ZerosRender.NUMBER
    EXCLUDE_RESULTS: list[str] = []

    class FGColor:
        SUCCESS: Final = "light_green"
        ERROR: Final = "light_red"
        SKIP: Final = "light_yellow"
        GRAYOUT: Final = "light_black"


OPTION_PREFIX: Final = "md-report"


@unique
class Option(Enum):
    MD_REPORT = (OPTION_PREFIX, "Create a Markdown report.")
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
            How coloring output reports.
            auto: detect the output destination and colorize reports appropriately with the output.
            for terminal output, render colored (text and background) reports using ANSI escape codes.
            for file output, render the report without color.
            text: render colored text reports by using ANSI escape codes.
            never: render report without color.
            Defaults to '{default}'.
            """
        ).format(default=Default.COLOR_POLICY.value),
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
            Automatically set to 'number' when the CI environment variable is set to
            TRUE (case insensitive) to display reports correctly at CI services.
            Defaults to '{default}'.
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
    MD_REPORT_FLAVOR = (
        f"{OPTION_PREFIX}-flavor",
        dedent(
            """\
            Markdown flavor of the output report.
            Defaults to '{default}'.
            """
        ).format(
            default=Default.MARKDOWN_FLAVOR.value,
        ),
    )
    MD_EXCLUDE_OUTCOMES = (
        f"{OPTION_PREFIX}-exclude-outcomes",
        dedent(
            """\
            List of test outcomes to exclude from the report.
            When specifying as an environment variable, pass a comma-separated string
            (e.g. 'passed,skipped').
            Defaults to '{default}'.
            """
        ).format(
            default=Default.EXCLUDE_RESULTS,
        ),
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
    EXTRA_MSG_TEMPLATE: Final = " you can also specify the value with {} environment variable."
