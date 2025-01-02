import os
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.terminal import TerminalReporter
from pytablewriter import TableWriterFactory
from pytablewriter.writer.text import MarkdownFlavor, normalize_md_flavor
from typepy import Bool, Integer, StrictLevel, is_not_null_string
from typepy.error import TypeConversionError

from ._const import ColorPolicy, Default, FGColor, Header, HelpMsg, Option, ZerosRender
from ._style_filter import col_separator_style_filter, style_filter


def zero_to_nullstr(value: Any) -> Any:
    if value == 0:
        return ""

    return value


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("md report", "generate test outcomes report with markdown table format")

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
        default=None,
        help=Option.MD_REPORT_TEE.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_TEE.envvar_str),
    )
    group.addoption(
        Option.MD_REPORT_COLOR.cmdoption_str,
        choices=[policy.value for policy in ColorPolicy],
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
    group.addoption(
        Option.MD_REPORT_FLAVOR.cmdoption_str,
        choices=[flavor.value for flavor in MarkdownFlavor],
        default=None,
        help=Option.MD_REPORT_FLAVOR.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_REPORT_FLAVOR.envvar_str),
    )
    group.addoption(
        Option.MD_EXCLUDE_OUTCOMES.cmdoption_str,
        nargs="+",
        default=[],
        help=Option.MD_EXCLUDE_OUTCOMES.help_msg
        + HelpMsg.EXTRA_MSG_TEMPLATE.format(Option.MD_EXCLUDE_OUTCOMES.envvar_str),
    )

    parser.addini(
        Option.MD_REPORT.inioption_str,
        type="bool",
        default=False,
        help=Option.MD_REPORT.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_VERBOSE.inioption_str,
        default=None,
        help=Option.MD_REPORT_VERBOSE.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_COLOR.inioption_str,
        default=None,
        help=Option.MD_REPORT_COLOR.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_OUTPUT.inioption_str,
        default=None,
        help=Option.MD_REPORT_OUTPUT.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_TEE.inioption_str,
        default=None,
        help=Option.MD_REPORT_TEE.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_MARGIN.inioption_str,
        default=None,
        help=Option.MD_REPORT_MARGIN.help_msg,
    )
    parser.addini(
        Option.MD_REPORT_ZEROS.inioption_str,
        default=None,
        help=Option.MD_REPORT_ZEROS.help_msg,
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
    parser.addini(
        Option.MD_REPORT_FLAVOR.inioption_str,
        default=None,
        help=Option.MD_REPORT_FLAVOR.help_msg,
    )
    parser.addini(
        Option.MD_EXCLUDE_OUTCOMES.inioption_str,
        type="args",
        default=[],
        help=Option.MD_EXCLUDE_OUTCOMES.help_msg,
    )


def is_make_md_report(config: Config) -> bool:
    if config.option.help:
        return False

    make_report: Optional[bool] = config.option.md_report

    if make_report is None:
        make_report = _to_bool(os.environ.get(Option.MD_REPORT.envvar_str))

    if make_report is None:
        make_report = _to_bool(config.getini(Option.MD_REPORT.inioption_str))

    if make_report is None:
        return False

    return make_report


def is_apply_ansi_escape_to_file(color_policy: ColorPolicy, is_output_file: bool) -> bool:
    if color_policy == ColorPolicy.TEXT:
        return True

    if color_policy == ColorPolicy.AUTO and not is_output_file:
        return True

    return False


def is_apply_ansi_escape_to_term(color_policy: ColorPolicy) -> bool:
    return color_policy in [ColorPolicy.TEXT, ColorPolicy.AUTO]


def _is_ci() -> bool:
    # many CI services will set the CI environment variable to 'true'
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


def _to_int(value: Any) -> Optional[int]:
    try:
        return Integer(value, strict_level=StrictLevel.MIN).convert()
    except TypeConversionError:
        pass

    return None


def _to_bool(value: Any) -> Optional[bool]:
    try:
        return Bool(value, strict_level=StrictLevel.MIN).convert()
    except TypeConversionError:
        pass

    return None


def retrieve_verbosity_level(config: Config) -> int:
    verbosity_level: Optional[int] = config.option.md_report_verbose

    if verbosity_level is not None and verbosity_level < 0:
        verbosity_level = None

    if verbosity_level is None:
        verbosity_level = _to_int(os.environ.get(Option.MD_REPORT_VERBOSE.envvar_str))

    if verbosity_level is None:
        verbosity_level = _to_int(config.getini(Option.MD_REPORT_VERBOSE.inioption_str))

    if verbosity_level is None:
        # use the verbosity level of the pytest if not set
        return config.option.verbose

    return verbosity_level


def retrieve_output_filepath(config: Config) -> Optional[str]:
    output_filepath: Optional[str] = config.option.md_report_output

    if not output_filepath:
        output_filepath = os.environ.get(Option.MD_REPORT_OUTPUT.envvar_str)

    if not output_filepath:
        value = config.getini(Option.MD_REPORT_OUTPUT.inioption_str)
        if value is None:
            return None
        else:
            return str(value)

    return output_filepath


def retrieve_tee(config: Config) -> bool:
    tee: Optional[bool] = config.option.md_report_tee

    if tee is None:
        envvar_str = os.environ.get(Option.MD_REPORT_TEE.envvar_str)
        if envvar_str is not None:
            tee = bool(envvar_str)

    if tee is None:
        inioption_str = config.getini(Option.MD_REPORT_TEE.inioption_str)
        if inioption_str is not None:
            tee = bool(inioption_str)

    return tee if tee is not None else False


def retrieve_md_flavor(config: Config) -> MarkdownFlavor:
    md_flavor = config.option.md_report_flavor

    if not md_flavor:
        md_flavor = os.environ.get(Option.MD_REPORT_FLAVOR.envvar_str)

    if not md_flavor:
        md_flavor = config.getini(Option.MD_REPORT_FLAVOR.inioption_str)

    if not md_flavor:
        return Default.MARKDOWN_FLAVOR

    return normalize_md_flavor(str(md_flavor))


def retrieve_exclude_outcomes(config: Config) -> list[str]:
    def norm_names(names: Sequence[Any]) -> list[str]:
        return [str(name).lower().strip() for name in names]

    exclude_outcomes = config.option.md_report_exclude_outcomes

    if not exclude_outcomes:
        exclude_outcomes = os.environ.get(Option.MD_EXCLUDE_OUTCOMES.envvar_str)
        if exclude_outcomes:
            return norm_names(exclude_outcomes.split(","))

    if not exclude_outcomes:
        exclude_outcomes = config.getini(Option.MD_EXCLUDE_OUTCOMES.inioption_str)

    if not exclude_outcomes:
        return Default.EXCLUDE_RESULTS

    if isinstance(exclude_outcomes, list):
        # list will be passed via pytest config file
        return norm_names(exclude_outcomes)
    elif isinstance(exclude_outcomes, str):
        # comma-separated string (e.g. passed,skipped) will be passed via the command line option
        return norm_names(exclude_outcomes.split(","))

    raise TypeError(f"Unexpected type {type(exclude_outcomes)} for exclude_outcomes")


def retrieve_color_policy(config: Config) -> ColorPolicy:
    color_policy = config.option.md_report_color

    if not color_policy:
        color_policy = os.environ.get(Option.MD_REPORT_COLOR.envvar_str)

    if not color_policy:
        color_policy = config.getini(Option.MD_REPORT_COLOR.inioption_str)

    if not color_policy:
        return Default.COLOR_POLICY

    return ColorPolicy[str(color_policy).upper()]


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

    if _is_ci():
        report_zeros = ZerosRender.NUMBER

    if not report_zeros:
        report_zeros = Default.ZEROS

    return str(report_zeros)


def retrieve_report_results_color(config: Config, color_option: Option, default: str) -> str:
    results_color = getattr(config.option, color_option.inioption_str)

    if not results_color:
        results_color = os.environ.get(color_option.envvar_str)

    if not results_color:
        results_color = config.getini(color_option.inioption_str)

    if not results_color:
        results_color = default

    return str(results_color)


def _normalize_stat_name(name: str) -> str:
    if name == "error":
        return "errors"

    return name


def retrieve_stat_count_map(reporter: TerminalReporter) -> dict[str, int]:
    stat_count_map = {}

    for name in ["failed", "passed", "skipped", "error", "xfailed", "xpassed"]:
        count = len(reporter.getreports(name))
        stat_count_map[name] = count

    return stat_count_map


def extract_pytest_stats(
    reporter: TerminalReporter, outcomes: Sequence[str], verbosity_level: int
) -> Mapping[tuple, Mapping[str, int]]:
    results_per_testfunc: dict[tuple, dict[str, int]] = {}

    for stat_key, values in reporter.stats.items():
        if stat_key not in outcomes:
            continue

        for value in values:
            try:
                filesystempath, lineno, domaininfo = value.location
            except AttributeError:
                continue

            filesystempath = os.path.normpath(filesystempath).replace("\\", "/")
            testfunc = value.head_line.split("[")[0]

            if verbosity_level == 0:
                key: tuple = (filesystempath,)
            elif verbosity_level >= 1:
                key = (filesystempath, testfunc)
            else:
                continue

            if key not in results_per_testfunc:
                results_per_testfunc[key] = defaultdict(int)

            results_per_testfunc[key][stat_key] += 1

    return results_per_testfunc


def make_md_report(
    config: Config,
    reporter: TerminalReporter,
    total_stats: Mapping[str, int],
    color_policy: ColorPolicy,
    apply_ansi_escape: bool,
    md_flavor: MarkdownFlavor,
) -> str:
    verbosity_level = retrieve_verbosity_level(config)
    exclude_outcomes = retrieve_exclude_outcomes(config)

    outcomes = ["passed", "failed", "error", "skipped", "xfailed", "xpassed"]
    outcomes = [key for key in outcomes if key not in exclude_outcomes]
    outcomes = [key for key in outcomes if total_stats.get(key, 0) > 0]

    if not outcomes:
        return ""

    results_per_testfunc = extract_pytest_stats(
        reporter=reporter, outcomes=outcomes, verbosity_level=verbosity_level
    )

    writer = TableWriterFactory.create_from_format_name(
        "md", flavor=md_flavor.value, colorize_terminal=apply_ansi_escape
    )

    matrix = [
        list(key) + [results.get(key, 0) for key in outcomes] + [sum(results.values())]
        for key, results in results_per_testfunc.items()
    ]
    if verbosity_level == 0:
        writer.headers = [Header.FILEPATH] + outcomes + [Header.SUBTOTAL]
        matrix.append(
            ["TOTAL"] + [total_stats.get(key, 0) for key in outcomes] + [sum(total_stats.values())]
        )
    elif verbosity_level >= 1:
        writer.headers = [Header.FILEPATH, Header.TESTFUNC] + outcomes + [Header.SUBTOTAL]
        matrix.append(
            ["TOTAL", ""]
            + [total_stats.get(key, 0) for key in outcomes]
            + [sum(total_stats.values())]
        )

    writer.margin = retrieve_report_margin(config)
    writer.value_matrix = matrix

    if color_policy != ColorPolicy.NEVER:
        writer.style_filter_kwargs = {
            "color_policy": color_policy,
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

        if color_policy == ColorPolicy.AUTO and not _is_ci():
            writer.add_col_separator_style_filter(col_separator_style_filter)

    report_zeros = retrieve_report_zeros(config)
    if report_zeros == ZerosRender.EMPTY:
        writer.register_trans_func(zero_to_nullstr)

    return writer.dumps()


def extract_file_color_policy(
    color_policy: ColorPolicy, is_output_file: bool, md_flavor: MarkdownFlavor
) -> ColorPolicy:
    file_color_policy = color_policy
    if is_output_file and color_policy == ColorPolicy.AUTO:
        if md_flavor != MarkdownFlavor.GFM:
            file_color_policy = ColorPolicy.NEVER

    return file_color_policy


def pytest_unconfigure(config: Config) -> None:
    if not is_make_md_report(config):
        return

    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        return

    stat_count_map = retrieve_stat_count_map(reporter)
    is_tee = retrieve_tee(config)
    output_filepath = retrieve_output_filepath(config)
    color_policy = retrieve_color_policy(config)
    md_flavor = retrieve_md_flavor(config)

    is_output_term = is_tee or not output_filepath
    is_output_file = is_not_null_string(output_filepath)
    term_color_policy = color_policy
    file_color_policy = extract_file_color_policy(color_policy, is_output_file, md_flavor)

    apply_ansi_escape_to_file = is_apply_ansi_escape_to_file(color_policy, is_output_file)
    apply_ansi_escape_to_term = is_apply_ansi_escape_to_term(color_policy)
    term_report = None
    if is_output_term:
        term_report = make_md_report(
            config,
            reporter,
            stat_count_map,
            color_policy=term_color_policy,
            apply_ansi_escape=apply_ansi_escape_to_term,
            md_flavor=md_flavor,
        )
        reporter._tw.write(term_report)

    if not is_output_file:
        return

    file_report = term_report
    gen_report_for_file_output = any(
        [
            not file_report,
            file_color_policy != term_color_policy,
            apply_ansi_escape_to_file != apply_ansi_escape_to_term,
        ]
    )
    if gen_report_for_file_output:
        file_report = make_md_report(
            config,
            reporter,
            stat_count_map,
            color_policy=file_color_policy,
            apply_ansi_escape=apply_ansi_escape_to_file,
            md_flavor=md_flavor,
        )

    if file_report:
        assert output_filepath
        with open(output_filepath, "w") as f:
            f.write(file_report)
