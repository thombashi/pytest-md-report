import os
import time
from collections import defaultdict
from typing import Mapping  # noqa
from typing import Any, Dict, Optional, Tuple, cast

from _pytest.config import Config
from _pytest.terminal import TerminalReporter
from pytablewriter import TableWriterFactory
from pytablewriter.style import Cell, Style

from ._const import BGColor, FGColor, Header, Ini


def pytest_addoption(parser):
    group = parser.getgroup("md report", "make test results report with markdown table format")

    group.addoption(
        "--md-report", action="store_true", default=None, help="create markdown report",
    )
    group.addoption(
        "--md-report-verbose", type=int, default=None, help="verbosity level",
    )
    group.addoption(
        "--md-report-color",
        choices=["auto", "never"],
        default=None,
        help="""
        auto: colorizing report for terminal with ANSI escape codes,
        never: report without color"
        """
    )

    parser.addini(
        Ini.MD_REPORT, type="bool", default=False, help="create markdown report",
    )
    parser.addini(
        Ini.MD_REPORT_VERBOSE, default=None, help="verbosity level for md report",
    )


def is_make_md_report(config: Config) -> bool:
    make_report = config.option.md_report
    if make_report is None:
        make_report = config.getini(Ini.MD_REPORT)
    if make_report is None:
        make_report = os.environ.get("PYTEST_MD_REPORT")
    if make_report is None:
        return False

    return make_report


def retrieve_verbosity_level(config: Config) -> int:
    verbosity_level = config.option.md_report_verbose

    if verbosity_level is not None and verbosity_level < 0:
        verbosity_level = None

    if verbosity_level is None:
        verbosity_level = config.getini(Ini.MD_REPORT_VERBOSE)
        if verbosity_level is not None:
            try:
                verbosity_level = int(verbosity_level)
            except ValueError:
                verbosity_level = None

    if verbosity_level is None:
        verbosity_level = os.environ.get("PYTEST_MD_REPORT_VERBOSE")

    if verbosity_level is None:
        verbosity_level = config.option.verbose

    return verbosity_level


def retrieve_report_color(config: Config) -> str:
    report_color = config.option.md_report_color
    if report_color is None:
        report_color = config.getini(Ini.MD_REPORT_VERBOSE)
    if report_color is None:
        report_color = os.environ.get("PYTEST_MD_REPORT_COLOR")

    return report_color


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


def retrieve_fg_bg_color(row: int, base_color: str, is_grayout):
    bg_color = None  # type: Optional[str]

    if (row % 2) == 0:
        fg_color = FGColor.GRAYOUT if is_grayout else base_color
        bg_color = BGColor.EVEN_ROW
    else:
        fg_color = FGColor.GRAYOUT if is_grayout else base_color
        bg_color = BGColor.ODD_ROW

    return (fg_color, bg_color)


def style_filter(cell: Cell, **kwargs: Any) -> Optional[Style]:
    writer = kwargs["writer"]
    fg_color = None
    bg_color = None

    is_grayout = False
    if cell.value == 0:
        is_grayout = True

    if cell.row < 0:
        if all([writer.value_matrix[r][cell.col] == 0 for r in range(len(writer.value_matrix))]):
            return Style(color=FGColor.GRAYOUT, font_weight="bold")

        return Style(font_weight="bold")

    headers = writer.headers
    if headers[cell.col] in (Header.FILEPATH, Header.TESTFUNC):
        error_count = sum(
            [
                writer.value_matrix[cell.row][headers.index("failed")],
                writer.value_matrix[cell.row][headers.index("error")],
            ]
        )
        if error_count > 0:
            fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.ERROR, is_grayout)
            return Style(color=fg_color, bg_color=bg_color)

        skip_count = sum(
            [
                writer.value_matrix[cell.row][headers.index("skipped")],
                writer.value_matrix[cell.row][headers.index("xfailed")],
                writer.value_matrix[cell.row][headers.index("xpassed")],
            ]
        )
        if skip_count > 0:
            fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.SKIP, is_grayout)
            return Style(color=fg_color, bg_color=bg_color)

        fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.SUCCESS, is_grayout)
        return Style(color=fg_color, bg_color=bg_color)

    if headers[cell.col] in ("passed"):
        fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.SUCCESS, is_grayout)
    elif headers[cell.col] in ("failed", "error"):
        fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.ERROR, is_grayout)
    if headers[cell.col] in ("skipped", "xfailed", "xpassed"):
        fg_color, bg_color = retrieve_fg_bg_color(cell.row, FGColor.SKIP, is_grayout)

    return Style(color=fg_color, bg_color=bg_color)


def col_separator_style_filter(
    left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: Any
) -> Optional[Style]:
    fg_color = None
    bg_color = None
    row = left_cell.row if left_cell else cast(Cell, right_cell).row
    col = left_cell.col if left_cell else cast(Cell, right_cell).col

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

    writer.margin = 1
    writer.value_matrix = matrix

    if retrieve_report_color(config) != "never":
        writer.add_style_filter(style_filter)
        writer.add_col_separator_style_filter(col_separator_style_filter)

    return writer.dumps()


def pytest_unconfigure(config):
    if not is_make_md_report(config):
        return

    reporter = config.pluginmanager.get_plugin("terminalreporter")

    try:
        duration = time.time() - reporter._sessionstarttime
    except AttributeError:
        return

    stat_count_map = _retrieve_stat_count_map(reporter)
    reporter._tw.write(make_md_report(config, reporter, stat_count_map))
    reporter._tw.write("\n")
