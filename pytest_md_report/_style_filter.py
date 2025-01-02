from typing import Any, Final, Optional, cast

from pytablewriter.style import Cell, Style
from pytablewriter.writer import AbstractTableWriter

from ._const import BGColor, ColorPolicy, FGColor, Header


class ColorRetriever:
    def __init__(
        self,
        row: int,
        is_grayout: bool,
        color_polilcy: ColorPolicy,
        color_map: dict[str, str],
    ) -> None:
        self.__row = row
        self.__is_grayout = is_grayout
        self.__color_polilcy = color_polilcy
        self.__color_map = color_map

    def retrieve_fg_bg_color(self, base_color: str) -> tuple[str, Optional[str]]:
        bg_color: Optional[str] = None

        if (self.__row % 2) == 0:
            fg_color = self.__color_map[FGColor.GRAYOUT] if self.__is_grayout else base_color
            bg_color = BGColor.EVEN_ROW if self.__color_polilcy == ColorPolicy.AUTO else None
        else:
            fg_color = self.__color_map[FGColor.GRAYOUT] if self.__is_grayout else base_color
            bg_color = BGColor.ODD_ROW if self.__color_polilcy == ColorPolicy.AUTO else None

        return (fg_color, bg_color)


def style_filter(cell: Cell, **kwargs: Any) -> Optional[Style]:
    writer = cast(AbstractTableWriter, kwargs["writer"])
    color_policy: Final = cast(ColorPolicy, kwargs["color_policy"])
    color_map: Final = kwargs["color_map"]
    num_rows: Final = cast(int, kwargs["num_rows"])
    headers: Final = writer.headers
    header: Final = headers[cell.col]
    fg_color = None
    bg_color = None

    is_grayout = False
    if cell.value == 0:
        is_grayout = True

    retriever = ColorRetriever(cell.row, is_grayout, color_policy, color_map)

    if cell.is_header_row():
        if all([writer.value_matrix[r][cell.col] == 0 for r in range(len(writer.value_matrix))]):
            return Style(color=color_map[FGColor.GRAYOUT])

        if header in ("passed"):
            fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SUCCESS])
        elif header in ("failed", "error"):
            fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.ERROR])
        elif header in ("skipped", "xfailed", "xpassed"):
            fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SKIP])
        else:
            return None

        return Style(color=fg_color)

    is_passed = False
    is_failed = False
    is_skipped = False

    if header in (Header.FILEPATH, Header.TESTFUNC, Header.SUBTOTAL):
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

    if is_passed or header in ("passed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SUCCESS])
    elif is_failed or header in ("failed", "error"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.ERROR])
    elif is_skipped or header in ("skipped", "xfailed", "xpassed"):
        fg_color, bg_color = retriever.retrieve_fg_bg_color(color_map[FGColor.SKIP])

    if cell.row == num_rows - 1:
        bg_color = BGColor.TOTAL_ROW

    return Style(color=fg_color, bg_color=bg_color)


def col_separator_style_filter(
    left_cell: Optional[Cell], right_cell: Optional[Cell], **kwargs: dict[str, Any]
) -> Optional[Style]:
    num_rows: Final = cast(int, kwargs["num_rows"])
    fg_color = None
    bg_color = None
    row: Final = left_cell.row if left_cell else cast(Cell, right_cell).row

    if row == num_rows - 1:
        bg_color = BGColor.TOTAL_ROW
    elif row % 2 == 0:
        bg_color = BGColor.EVEN_ROW
    elif row >= 0:
        bg_color = BGColor.ODD_ROW

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None
