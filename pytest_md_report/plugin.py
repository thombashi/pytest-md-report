import os
from collections import defaultdict
from typing import Mapping  # noqa
from typing import Any, Dict, Optional, Tuple, cast

from _pytest.config import Config
from _pytest.terminal import TerminalReporter
from pytablewriter import TableWriterFactory
from pytablewriter.style import Cell, Style
from typepy import Bool, Integer, StrictLevel
from typepy.error import TypeConversionError

from ._const import BGColor, ColorPoicy, Default, EnvVar, FGColor, Header, HelpMsg, Ini, ZerosRender


def zero_to_nullstr(value) -> str:
    if value == 0:
        return ""

    return value


def pytest_addoption(parser):
    group = parser.getgroup("md report", "make test results report with markdown table format")

    group.addoption(
        "--md-report",
        action="store_true",
        default=None,
        help=HelpMsg.MD_REPORT + HelpMsg.EXTRA_MSG_TEMPLATE.format(EnvVar.MD_REPORT),
    )
    group.addoption(
        "--md-report-verbose",
        metavar="VERBOSITY_LEVEL",
        type=int,
        default=None,
        help=HelpMsg.MD_REPORT_VERBOSE
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(EnvVar.MD_REPORT_VERBOSE),
    )
    group.addoption(
        "--md-report-color",
        choices=ColorPoicy.LIST,
        default=None,
        help=HelpMsg.MD_REPORT_COLOR + HelpMsg.EXTRA_MSG_TEMPLATE.format(EnvVar.MD_REPORT_COLOR),
    )
    group.addoption(
        "--md-report-margin",
        metavar="MARGIN",
        type=int,
        default=None,
        help=HelpMsg.MD_REPORT_MARGIN + HelpMsg.EXTRA_MSG_TEMPLATE.format(EnvVar.MD_REPORT_MARGIN),
    )
    group.addoption(
        "--md-report-zeros",
        choices=ZerosRender.LIST,
        default=None,
        help=HelpMsg.MD_REPORT_ZEROS + HelpMsg.EXTRA_MSG_TEMPLATE.format(EnvVar.MD_REPORT_ZEROS),
    )

    parser.addini(
        Ini.MD_REPORT, type="bool", default=False, help=HelpMsg.MD_REPORT,
    )
    parser.addini(
        Ini.MD_REPORT_VERBOSE, default=None, help=HelpMsg.MD_REPORT_VERBOSE,
    )
    parser.addini(
        Ini.MD_REPORT_COLOR, default=None, help=HelpMsg.MD_REPORT_COLOR,
    )
    parser.addini(
        Ini.MD_REPORT_MARGIN, default=None, help=HelpMsg.MD_REPORT_MARGIN,
    )
    parser.addini(
        Ini.MD_REPORT_ZEROS, default=None, help=HelpMsg.MD_REPORT_ZEROS,
    )


def is_make_md_report(config: Config) -> bool:
    make_report = config.option.md_report

    if make_report is None:
        try:
            make_report = Bool(
                os.environ.get(EnvVar.MD_REPORT), strict_level=StrictLevel.MIN
            ).convert()
        except TypeConversionError:
            make_report = None

    if make_report is None:
        make_report = config.getini(Ini.MD_REPORT)

    if make_report is None:
        return False

    return make_report


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
        verbosity_level = _to_int(os.environ.get(EnvVar.MD_REPORT_VERBOSE))

    if verbosity_level is None:
        verbosity_level = _to_int(config.getini(Ini.MD_REPORT_VERBOSE))

    if verbosity_level is None:
        verbosity_level = config.option.verbose

    return verbosity_level


def retrieve_report_color(config: Config) -> str:
    report_color = config.option.md_report_color

    if not report_color:
        report_color = os.environ.get(EnvVar.MD_REPORT_COLOR)

    if not report_color:
        report_color = config.getini(Ini.MD_REPORT_COLOR)

    if not report_color:
        return Default.COLOR

    return report_color


def retrieve_report_margin(config: Config) -> int:
    margin = config.option.md_report_margin

    if margin is None:
        margin = _to_int(os.environ.get(EnvVar.MD_REPORT_MARGIN))

    if margin is None:
        margin = _to_int(config.getini(Ini.MD_REPORT_MARGIN))

    if margin is None:
        return Default.MARGIN

    return margin


def retrieve_report_zeros(config: Config) -> str:
    report_zeros = config.option.md_report_zeros

    if not report_zeros:
        report_zeros = os.environ.get(EnvVar.MD_REPORT_ZEROS)

    if not report_zeros:
        report_zeros = config.getini(Ini.MD_REPORT_ZEROS)

    if not report_zeros:
        report_zeros = Default.ZEROS

    return report_zeros


def _normalize_stat_name(name: str) -> str:
    if name == "error":
        return "errors"

    return name


def _retrieve_stat_count_map(reporter: TerminalReporter) -> Dict[str, int]:
    stat_count_map = {}

    for name in ["failed", "passed", "skipped", "error", "xfailed", "xpassed"]:
        count = len(reporter.getreports(name))
        stat_count_map[name] = count

    return stat_count_map


class ColorRetriever:
    def __init__(self, row: int, is_grayout: bool, report_color: str) -> None:
        self.__row = row
        self.__is_grayout = is_grayout
        self.__report_color = report_color

    def retrieve_fg_bg_color(self, base_color: str) -> Tuple[str, Optional[str]]:
        bg_color = None  # type: Optional[str]

        if (self.__row % 2) == 0:
            fg_color = FGColor.GRAYOUT if self.__is_grayout else base_color
            bg_color = BGColor.EVEN_ROW if self.__report_color == ColorPoicy.AUTO else None
        else:
            fg_color = FGColor.GRAYOUT if self.__is_grayout else base_color
            bg_color = BGColor.ODD_ROW if self.__report_color == ColorPoicy.AUTO else None

        return (fg_color, bg_color)


def style_filter(cell: Cell, **kwargs: Any) -> Optional[Style]:
    writer = kwargs["writer"]
    report_color = kwargs["report_color"]
    fg_color = None
    bg_color = None

    is_grayout = False
    if cell.value == 0:
        is_grayout = True

    if cell.row < 0:
        if all([writer.value_matrix[r][cell.col] == 0 for r in range(len(writer.value_matrix))]):
            return Style(color=FGColor.GRAYOUT, font_weight="bold")

        return Style(font_weight="bold")

    retriever = ColorRetriever(cell.row, is_grayout, report_color)

    headers = writer.headers
    if headers[cell.col] in (Header.FILEPATH, Header.TESTFUNC):
        error_count = sum(
            [
                writer.value_matrix[cell.row][headers.index("failed")],
                writer.value_matrix[cell.row][headers.index("error")],
            ]
        )
        if error_count > 0:
            fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.ERROR)
            return Style(color=fg_color, bg_color=bg_color)

        skip_count = sum(
            [
                writer.value_matrix[cell.row][headers.index("skipped")],
                writer.value_matrix[cell.row][headers.index("xfailed")],
                writer.value_matrix[cell.row][headers.index("xpassed")],
            ]
        )
        if skip_count > 0:
            fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.SKIP)
            return Style(color=fg_color, bg_color=bg_color)

        fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.SUCCESS)
        return Style(color=fg_color, bg_color=bg_color)

    if headers[cell.col] in ("passed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.SUCCESS)
    elif headers[cell.col] in ("failed", "error"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.ERROR)
    if headers[cell.col] in ("skipped", "xfailed", "xpassed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(FGColor.SKIP)

    return Style(color=fg_color, bg_color=bg_color)


def col_separator_style_filter(
    left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: Any
) -> Optional[Style]:
    fg_color = None
    bg_color = None
    row = left_cell.row if left_cell else cast(Cell, right_cell).row

    if row % 2 == 0:
        bg_color = BGColor.EVEN_ROW
    elif row >= 0:
        bg_color = BGColor.ODD_ROW

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None


def make_md_report(
    config: Config, reporter: TerminalReporter, total_stats: Mapping[str, int]
) -> str:
    verbosity_level = 1
    verbosity_level = retrieve_verbosity_level(config)

    outcomes = ["passed", "failed", "error", "skipped", "xfailed", "xpassed"]
    results_per_testfunc = {}  # type: Dict[Tuple, Dict[str, int]]

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
                key = (filesystempath,)  # type: Tuple
            elif verbosity_level >= 1:
                key = (filesystempath, testfunc)

            if key not in results_per_testfunc:
                results_per_testfunc[key] = defaultdict(int)
            results_per_testfunc[key][stat_key] += 1

    writer = TableWriterFactory.create_from_format_name("md")

    matrix = [
        list(key) + [results.get(key, 0) for key in outcomes]  # type: ignore
        for key, results in results_per_testfunc.items()
    ]
    if verbosity_level == 0:
        writer.headers = [Header.FILEPATH] + outcomes
        matrix.append(["TOTAL"] + [total_stats.get(key, 0) for key in outcomes])  # type: ignore
    elif verbosity_level >= 1:
        writer.headers = [Header.FILEPATH, Header.TESTFUNC] + outcomes
        matrix.append(["TOTAL", ""] + [total_stats.get(key, 0) for key in outcomes])  # type: ignore

    writer.margin = retrieve_report_margin(config)
    writer.value_matrix = matrix

    report_color = retrieve_report_color(config)
    if report_color != ColorPoicy.NEVER:
        writer.style_filter_kwargs = {"report_color": report_color}
        writer.add_style_filter(style_filter)

        if report_color == ColorPoicy.AUTO:
            writer.add_col_separator_style_filter(col_separator_style_filter)

    report_zeros = retrieve_report_zeros(config)
    if report_zeros == ZerosRender.EMPTY:
        writer.register_trans_func(zero_to_nullstr)

    return writer.dumps()


def pytest_unconfigure(config):
    if not is_make_md_report(config):
        return

    reporter = config.pluginmanager.get_plugin("terminalreporter")
    stat_count_map = _retrieve_stat_count_map(reporter)
    reporter._tw.write(make_md_report(config, reporter, stat_count_map))
