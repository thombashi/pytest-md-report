import os
from collections import defaultdict
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, cast

from _pytest.config import Config
from _pytest.terminal import TerminalReporter
from pytablewriter import TableWriterFactory
from pytablewriter.style import Cell, Style
from pytablewriter.writer import AbstractTableWriter
from typepy import Bool, Integer, StrictLevel
from typepy.error import TypeConversionError

from ._const import BGColor, ColorPolicy, Default, FGColor, Header, HelpMsg, Option, ZerosRender


def zero_to_nullstr(value) -> str:
    if value == 0:
        return ""

    return value


def pytest_addoption(parser):
    group = parser.getgroup("md report", "make test results report with markdown table format")

    group.addoption(
        Option.MD_REPORT.cmdoption_str,
        action="store_true",
        default=None,
        help=Option.MD_REPORT.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_VERBOSE.cmdoption_str,
        metavar="VERBOSITY_LEVEL",
        type=int,
        default=None,
        help=Option.MD_REPORT_VERBOSE.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_VERBOSE.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_OUTPUT.cmdoption_str,
        metavar="FILEPATH",
        default=None,
        help=Option.MD_REPORT_OUTPUT.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_OUTPUT.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_TEE.cmdoption_str,
        action="store_true",
        help=Option.MD_REPORT_TEE.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_TEE.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_COLOR.cmdoption_str,
        choices=ColorPolicy.LIST,
        default=None,
        help=Option.MD_REPORT_COLOR.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_COLOR.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_MARGIN.cmdoption_str,
        metavar="MARGIN",
        type=int,
        default=None,
        help=Option.MD_REPORT_MARGIN.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_MARGIN.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_ZEROS.cmdoption_str,
        choices=ZerosRender.LIST,
        default=None,
        help=Option.MD_REPORT_ZEROS.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_ZEROS.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_SUCCESS_COLOR.cmdoption_str,
        default=None,
        help=Option.MD_REPORT_SUCCESS_COLOR.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_SUCCESS_COLOR.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_SKIP_COLOR.cmdoption_str,
        default=None,
        help=Option.MD_REPORT_SKIP_COLOR.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_SKIP_COLOR.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_ERROR_COLOR.cmdoption_str,
        default=None,
        help=Option.MD_REPORT_ERROR_COLOR.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_ERROR_COLOR.envvar_str),
    )

    parser.addini(
        Option.MD_REPORT.inioption_str, type="bool", default=False, help=Option.MD_REPORT.help_msg
    )
    parser.addini(
        Option.MD_REPORT_VERBOSE.inioption_str, default=None, help=Option.MD_REPORT_VERBOSE.help_msg
    )
    parser.addini(
        Option.MD_REPORT_COLOR.inioption_str, default=None, help=Option.MD_REPORT_COLOR.help_msg
    )
    parser.addini(
        Option.MD_REPORT_OUTPUT.inioption_str, default=None, help=Option.MD_REPORT_OUTPUT.help_msg
    )
    parser.addini(
        Option.MD_REPORT_TEE.inioption_str, default=None, help=Option.MD_REPORT_TEE.help_msg
    )
    parser.addini(
        Option.MD_REPORT_MARGIN.inioption_str, default=None, help=Option.MD_REPORT_MARGIN.help_msg
    )
    parser.addini(
        Option.MD_REPORT_ZEROS.inioption_str, default=None, help=Option.MD_REPORT_ZEROS.help_msg
    )
    parser.addini(
        Option.MD_REPORT_SUCCESS_COLOR.inioption_str,
        default=None,
        help=Option.MD_REPORT_SUCCESS_COLOR.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_SKIP_COLOR.inioption_str,
        default=None,
        help=Option.MD_REPORT_SKIP_COLOR.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_ERROR_COLOR.inioption_str,
        default=None,
        help=Option.MD_REPORT_ERROR_COLOR.help_msg,
    )


def is_make_md_report(config: Config) -> bool:
    if config.option.help:
        return False

    make_report = config.option.md_report

    if make_report is None:
        try:
            make_report = Bool(
                os.environ.get(Option.MD_REPORT.envvar_str), strict_level=StrictLevel.MIN
            ).convert()
        except TypeConversionError:
            make_report = None

    if make_report is None:
        make_report = config.getini(Option.MD_REPORT.inioption_str)

    if make_report is None:
        return False

    return make_report


def _is_ci() -> bool:
    # most of the CI services will be set CI environment to 'true'
    CI = os.environ.get("CI")
    if not CI:
        return False

    return CI.lower() == "true"


def _is_travis_ci() -> bool:
    # https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
    return os.environ.get("TRAVIS") == "true"


def _is_appveyor_ci() -> bool:
    # https://www.appveyor.com/docs/environment-variables/
    APPVEYOR = os.environ.get("APPVEYOR")
    if not APPVEYOR:
        return False

    return APPVEYOR.lower() == "true"


def _to_int(value) -> Optional[int]:
    try:
        return Integer(value, strict_level=StrictLevel.MIN).convert()
    except TypeConversionError:
        return None


def retrieve_verbosity_level(config: Config) -> int:
    verbosity_level = config.option.md_report_verbose

    if verbosity_level is not None and verbosity_level < 0:
        verbosity_level = None

    if verbosity_level is None:
        verbosity_level = _to_int(os.environ.get(Option.MD_REPORT_VERBOSE.envvar_str))

    if verbosity_level is None:
        verbosity_level = _to_int(config.getini(Option.MD_REPORT_VERBOSE.inioption_str))

    if verbosity_level is None:
        verbosity_level = config.option.verbose

    return verbosity_level


def retrieve_output_filepath(config: Config) -> Optional[str]:
    output_filepath = config.option.md_report_output

    if not output_filepath:
        output_filepath = os.environ.get(Option.MD_REPORT_OUTPUT.envvar_str)

    if not output_filepath:
        output_filepath = config.getini(Option.MD_REPORT_OUTPUT.inioption_str)

    return output_filepath


def retrieve_tee(config: Config) -> bool:
    tee = config.option.md_report_tee

    if not tee:
        tee = os.environ.get(Option.MD_REPORT_TEE.envvar_str, False)

    if not tee:
        tee = config.getini(Option.MD_REPORT_TEE.inioption_str)

    return tee


def retrieve_report_color(config: Config) -> str:
    report_color = config.option.md_report_color

    if not report_color:
        report_color = os.environ.get(Option.MD_REPORT_COLOR.envvar_str)

    if not report_color:
        report_color = config.getini(Option.MD_REPORT_COLOR.inioption_str)

    if not report_color:
        return Default.COLOR

    return report_color


def retrieve_report_margin(config: Config) -> int:
    margin = config.option.md_report_margin

    if margin is None:
        margin = _to_int(os.environ.get(Option.MD_REPORT_MARGIN.envvar_str))

    if margin is None:
        margin = _to_int(config.getini(Option.MD_REPORT_MARGIN.inioption_str))

    if margin is None:
        return Default.MARGIN

    return margin


def retrieve_report_zeros(config: Config) -> str:
    report_zeros = config.option.md_report_zeros

    if not report_zeros:
        report_zeros = os.environ.get(Option.MD_REPORT_ZEROS.envvar_str)

    if not report_zeros:
        report_zeros = config.getini(Option.MD_REPORT_ZEROS.inioption_str)

    if not report_zeros and _is_ci():
        report_zeros = ZerosRender.EMPTY

    if not report_zeros:
        report_zeros = Default.ZEROS

    return report_zeros


def retrieve_report_results_color(config: Config, color_option: Option, default: str) -> str:
    results_color = getattr(config.option, color_option.inioption_str)

    if not results_color:
        results_color = os.environ.get(color_option.envvar_str)

    if not results_color:
        results_color = config.getini(color_option.inioption_str)

    if not results_color:
        results_color = default

    return results_color


def _normalize_stat_name(name: str) -> str:
    if name == "error":
        return "errors"

    return name


def retrieve_stat_count_map(reporter: TerminalReporter) -> Dict[str, int]:
    stat_count_map = {}

    for name in ["failed", "passed", "skipped", "error", "xfailed", "xpassed"]:
        count = len(reporter.getreports(name))
        stat_count_map[name] = count

    return stat_count_map


class ColorRetriever:
    def __init__(
        self, row: int, is_grayout: bool, report_color: str, color_map: Dict[str, str]
    ) -> None:
        self.__row = row
        self.__is_grayout = is_grayout
        self.__report_color = report_color
        self.__color_map = color_map

    def retrieve_fg_bg_color(self, base_color: str) -> Tuple[str, Optional[str]]:
        bg_color: Optional[str] = None

        if (self.__row % 2) == 0:
            fg_color = self.__color_map[FGColor.GRAYOUT] if self.__is_grayout else base_color
            bg_color = BGColor.EVEN_ROW if self.__report_color == ColorPolicy.AUTO else None
        else:
            fg_color = self.__color_map[FGColor.GRAYOUT] if self.__is_grayout else base_color
            bg_color = BGColor.ODD_ROW if self.__report_color == ColorPolicy.AUTO else None

        return (fg_color, bg_color)


def style_filter(cell: Cell, **kwargs: Dict[str, Any]) -> Optional[Style]:
    writer = cast(AbstractTableWriter, kwargs["writer"])
    report_color = cast(str, kwargs["report_color"])
    color_map = kwargs["color_map"]
    num_rows = cast(int, kwargs["num_rows"])
    fg_color = None
    bg_color = None

    is_grayout = False
    if cell.value == 0:
        is_grayout = True

    if cell.is_header_row():
        if all([writer.value_matrix[r][cell.col] == 0 for r in range(len(writer.value_matrix))]):
            return Style(color=color_map[FGColor.GRAYOUT], font_weight="bold")

        return Style(font_weight="bold")

    retriever = ColorRetriever(cell.row, is_grayout, report_color, color_map)
    is_passed = False
    is_failed = False
    is_skipped = False

    headers = writer.headers
    if headers[cell.col] in (Header.FILEPATH, Header.TESTFUNC, Header.SUBTOTAL):
        error_ct_list = []
        if "failed" in headers:
            error_ct_list.append(writer.value_matrix[cell.row][headers.index("failed")])
        if "error" in headers:
            error_ct_list.append(writer.value_matrix[cell.row][headers.index("error")])

        skip_ct_list = []
        if "skipped" in headers:
            skip_ct_list.append(writer.value_matrix[cell.row][headers.index("skipped")])
        if "xfailed" in headers:
            skip_ct_list.append(writer.value_matrix[cell.row][headers.index("xfailed")])
        if "xpassed" in headers:
            skip_ct_list.append(writer.value_matrix[cell.row][headers.index("xpassed")])

        error_ct = sum(error_ct_list)
        skip_ct = sum(skip_ct_list)

        is_failed = error_ct > 0
        is_skipped = skip_ct > 0
        is_passed = error_ct == 0 and skip_ct == 0

    if is_passed or headers[cell.col] in ("passed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SUCCESS])
    elif is_failed or headers[cell.col] in ("failed", "error"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.ERROR])
    elif is_skipped or headers[cell.col] in ("skipped", "xfailed", "xpassed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SKIP])

    if cell.row == num_rows - 1:
        bg_color = BGColor.TOTAL_ROW

    return Style(color=fg_color, bg_color=bg_color)


def col_separator_style_filter(
    left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: Dict[str, Any]
) -> Optional[Style]:
    num_rows = cast(int, kwargs["num_rows"])
    fg_color = None
    bg_color = None
    row = left_cell.row if left_cell else cast(Cell, right_cell).row

    if row == num_rows - 1:
        bg_color = BGColor.TOTAL_ROW
    elif row % 2 == 0:
        bg_color = BGColor.EVEN_ROW
    elif row >= 0:
        bg_color = BGColor.ODD_ROW

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None


def extract_pytest_stats(
    reporter: TerminalReporter, outcomes: Sequence[str], verbosity_level: int
) -> Mapping[Tuple, Mapping[str, int]]:
    results_per_testfunc: Dict[Tuple, Dict[str, int]] = {}

    for stat_key, values in reporter.stats.items():
        if stat_key not in outcomes:
            continue

        for value in values:
            try:
                filesystempath, lineno, domaininfo = value.location
            except AttributeError:
                continue

            testfunc = value.head_line.split("[")[0]

            if verbosity_level == 0:
                key: Tuple = (filesystempath,)
            elif verbosity_level >= 1:
                key = (filesystempath, testfunc)

            if key not in results_per_testfunc:
                results_per_testfunc[key] = defaultdict(int)
            results_per_testfunc[key][stat_key] += 1

    return results_per_testfunc


def make_md_report(
    config: Config, reporter: TerminalReporter, total_stats: Mapping[str, int]
) -> str:
    verbosity_level = retrieve_verbosity_level(config)

    outcomes = ["passed", "failed", "error", "skipped", "xfailed", "xpassed"]
    outcomes = [key for key in outcomes if total_stats.get(key, 0) > 0]
    results_per_testfunc = extract_pytest_stats(
        reporter=reporter, outcomes=outcomes, verbosity_level=verbosity_level
    )

    writer = TableWriterFactory.create_from_format_name("md")

    matrix = [
        list(key) + [results.get(key, 0) for key in outcomes] + [sum(results.values())]
        for key, results in results_per_testfunc.items()
    ]
    if verbosity_level == 0:
        writer.headers = [Header.FILEPATH] + outcomes + [Header.SUBTOTAL]
        matrix.append(
            ["TOTAL"]
            + [total_stats.get(key, 0) for key in outcomes]  # type: ignore
            + [sum(total_stats.values())]  # type: ignore
        )
    elif verbosity_level >= 1:
        writer.headers = [Header.FILEPATH, Header.TESTFUNC] + outcomes + [Header.SUBTOTAL]
        matrix.append(
            ["TOTAL", ""]
            + [total_stats.get(key, 0) for key in outcomes]  # type: ignore
            + [sum(total_stats.values())]  # type: ignore
        )

    writer.margin = retrieve_report_margin(config)
    writer.value_matrix = matrix

    report_color = retrieve_report_color(config)
    if report_color != ColorPolicy.NEVER:
        writer.style_filter_kwargs = {
            "report_color": report_color,
            "color_map": {
                FGColor.SUCCESS: retrieve_report_results_color(
                    config, Option.MD_REPORT_SUCCESS_COLOR, Default.FGColor.SUCCESS
                ),
                FGColor.ERROR: retrieve_report_results_color(
                    config, Option.MD_REPORT_ERROR_COLOR, Default.FGColor.ERROR
                ),
                FGColor.SKIP: retrieve_report_results_color(
                    config, Option.MD_REPORT_SKIP_COLOR, Default.FGColor.SKIP
                ),
                FGColor.GRAYOUT: Default.FGColor.GRAYOUT,
            },
            "num_rows": len(writer.value_matrix),
        }

        if not _is_travis_ci():
            writer.add_style_filter(style_filter)

        if report_color == ColorPolicy.AUTO and not _is_ci():
            writer.add_col_separator_style_filter(col_separator_style_filter)

    report_zeros = retrieve_report_zeros(config)
    if report_zeros == ZerosRender.EMPTY:
        writer.register_trans_func(zero_to_nullstr)

    return writer.dumps()


def pytest_unconfigure(config):
    if not is_make_md_report(config):
        return

    reporter = config.pluginmanager.get_plugin("terminalreporter")
    stat_count_map = retrieve_stat_count_map(reporter)
    report = make_md_report(config, reporter, stat_count_map)
    output_filepath = retrieve_output_filepath(config)
    is_tee = retrieve_tee(config)

    if is_tee or not output_filepath:
        reporter._tw.write(report)

    if not output_filepath:
        return

    with open(output_filepath, "w") as f:
        f.write(report)
