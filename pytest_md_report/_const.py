from textwrap import dedent


class Default:
    COLOR = "auto"


class HelpMsg:
    MD_REPORT = "create markdown report."
    MD_REPORT_VERBOSE = dedent(
        """\
        verbosity level for pytest-md-report. if not set, using verbosity level of pytest.
        """
    )
    MD_REPORT_COLOR = dedent(
        """\
        auto: diplay colorizing report for terminal with ANSI escape codes.
        never: diplay report without color.
        defaults to '{default}'.
        """
    ).format(default=Default.COLOR)


class Ini:
    MD_REPORT = "md_report"
    MD_REPORT_VERBOSE = "md_report_verbose"
    MD_REPORT_COLOR = "md_report_color"


class Header:
    FILEPATH = "filepath"
    TESTFUNC = "function"


class FGColor:
    SUCCESS = "light_green"
    ERROR = "light_red"
    SKIP = "light_yellow"
    GRAYOUT = "light_black"


class BGColor:
    EVEN_ROW = "#202020"
    ODD_ROW = "black"
