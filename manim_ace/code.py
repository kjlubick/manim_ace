from manim import *

import re

from typing import Optional

from .colors import (BLACK_07, IBM_CYAN_20, IBM_RED_20, IBM_PURPLE_30,
                     USER_FUNCTION_COLOR, BLACK_12)
from .fonts import ROBOTO_MONO

FOR_SCOPE_COLOR = BLACK_07
NESTED_SCOPE_COLOR = BLACK_12
IF_SCOPE_COLOR = IBM_CYAN_20
ELSE_SCOPE_COLOR = IBM_RED_20
ELIF_SCOPE_COLOR = IBM_PURPLE_30


class CodeWithPalette(Code):
    def _gen_code_json(self):
        super()._gen_code_json()
        palette_swap = {
            # purple used by if and for is just a little too light
            # for me
            '#A90D91': '#900A7F',
        }
        # print(self.code_json)
        for line in self.code_json:
            for entry in line:
                entry[1] = palette_swap.get(entry[1], entry[1])


class CodeWindow(VDict):
    def __init__(self, source_code: str, tab_width: int = 4,
                 start_at_line=1):
        super().__init__()
        self.line_offset = start_at_line - 1

        code = CodeWithPalette(
            code=source_code,
            # The default for rendered indentation is 3 (ick).
            tab_width=tab_width,
            # Indentation of this type will be converted to tabs before rendering.
            # For convenience, align it to the rendered width so the input source
            # code aligns with the rendered version.
            indentation_chars=" " * tab_width,
            line_spacing=0.6,
            background_stroke_width=1,
            background_stroke_color=GREY,
            insert_line_no=True,
            style="xcode",
            background="rectangle",
            language="python",
            font=ROBOTO_MONO,
            name="source_code",
            line_no_from=start_at_line,
        )
        self.indent_chars = tab_width

        # Ignore outline (code[0])
        for i in range(0, len(code[1])):
            # Line numbers with 1 in the low digit are a bit
            # wonky, alignment wise.
            if (i + start_at_line) % 10 == 1:
                code[1][i].shift(LEFT * 0.04)
            # Reduce the gap between line and code a bit
            code[1][i].shift(RIGHT * 0.1)

            # Code turns leading tabs or spaces into invisible Dots.
            # These Dots are not located properly either (as of v0.17.2)
            # This is non-intuitive, so we remove them.
            to_remove = []
            for j in range(0, len(code[2][i])):
                if type(code[2][i][j]) == Dot:
                    to_remove.append(code[2][i][j])
                else:
                    break
            code[2][i].remove(*to_remove)

            self.add([
                (f"label_{i + start_at_line}", code[1][i]),
                (f"line_{i + start_at_line}", code[2][i]),
            ])
        self.total_lines = len(code[1])
        self.scopes = VGroup()
        # Insert it in front of the background behind everything else
        self.submobjects.insert(0, self.scopes)
        self.code_area = code[2]

    def line_width(self) -> float:
        """Returns the maximum width of a line of code."""
        return self.lines(1, self.total_lines).width

    def lines(self, start: int, end: Optional[int]):
        """Both arguments are inclusive."""
        vg = VGroup()
        if end is None:
            end = self.total_lines - 1 + self.line_offset
        for i in range(start, end + 1):
            vg.add(self[f"line_{i}"])
        return vg

    def add_scope_rectangle(self, key: str, mobj: Mobject):
        self.submob_dict[key] = mobj
        self.scopes.add(mobj)

    def highlight_scope(self, scope_type: str, lines: int, indents: int,
                        line: int, start: int, end: int,
                        body_lines_offset=1) -> Animation:
        if scope_type == 'for':
            color = FOR_SCOPE_COLOR
        elif scope_type == 'for2':
            color = NESTED_SCOPE_COLOR
        elif scope_type == 'if':
            color = IF_SCOPE_COLOR
        elif scope_type == 'else':
            color = ELSE_SCOPE_COLOR
        elif scope_type == 'elif':
            color = ELIF_SCOPE_COLOR
        elif scope_type == 'def':
            color = USER_FUNCTION_COLOR
        elif scope_type == 'while':
            color = FOR_SCOPE_COLOR
        else:
            assert False

        # TODO these numbers seem a bit magical. Probably should do better
        # measuring
        lines_padding = 0.1
        body_vg = self.lines(line + body_lines_offset, line + body_lines_offset + lines - 1)
        keyword_vg = self[f'line_{line}'][start:end]
        scope_lines = Rectangle(height=body_vg.height + lines_padding,
                                width=abs(keyword_vg.get_left() - self.code_area.get_right())[0] + 0.1,
                                fill_color=color, stroke_width=0, fill_opacity=1.0)
        top_padding = 0.01
        height = (keyword_vg.get_top() - body_vg.get_top())[1] + top_padding
        scope_kw = Rectangle(height=height,
                             width=keyword_vg.width + 0.02,
                             fill_color=color, stroke_width=0, fill_opacity=1.0)
        scope_kw.align_to(keyword_vg.get_corner(UL) + [-0.01, top_padding, 0], UL)
        scope_lines.align_to(scope_kw.get_corner(DL) + [0, 0.05, 0], UL)

        new_scope = VGroup(scope_lines, scope_kw)
        new_scope.set_opacity(0)
        self.add_scope_rectangle(f'scope_{line}', new_scope)
        return new_scope.animate.set_opacity(1.0)
