from textwrap import dedent


class EnvVar:
    MD_REPORT = "PYTEST_MD_REPORT"
    MD_REPORT_VERBOSE = "PYTEST_MD_REPORT_VERBOSE"
    MD_REPORT_COLOR = "PYTEST_MD_REPORT_COLOR"
    MD_REPORT_MARGIN = "PYTEST_MD_REPORT_MARGIN"
    MD_REPORT_ZEROS = "PYTEST_MD_REPORT_ZEROS"


class Ini:
    MD_REPORT = "md_report"
    MD_REPORT_VERBOSE = "md_report_verbose"
    MD_REPORT_COLOR = "md_report_color"
    MD_REPORT_MARGIN = "md_report_margin"
    MD_REPORT_ZEROS = "md_report_zeros"


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
