from manim import *

from .fonts import LM_MONO
from .colors import STANDARD_FUNCTION_COLOR, USER_FUNCTION_COLOR, LIBRARY_FUNCTION_COLOR


class Function(VDict):
    def __init__(self, name: str, desc: str, alignment='center',
                 num_inputs=1, num_outputs=1, user_fn=False, library_fn=False):
        super().__init__()
        assert not (user_fn and library_fn) # cannot be both
        assert num_inputs >= 1 or num_outputs >= 1
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        MIN_HEIGHT = max(num_inputs, num_outputs) * 0.5
        fn_name_text = Text(name, color=BLACK, font_size=24, font=LM_MONO)
        desc_text = Paragraph(desc, color=BLACK, font_size=18,
                              font=LM_MONO, alignment=alignment)
        height = max(desc_text.height + 0.2, MIN_HEIGHT)
        color = STANDARD_FUNCTION_COLOR
        if user_fn:
            color = USER_FUNCTION_COLOR
        if library_fn:
            color = LIBRARY_FUNCTION_COLOR
        fn_box = Rectangle(height=height,
                           width=desc_text.width + 0.2, fill_color=color,
                           color=BLACK, stroke_width=2, fill_opacity=1.0)
        fn_name_text.next_to(fn_box, UP, buff=0.1)
        # Need to draw this as a polygon and not an occluded triangle or
        # fading in looks odd.
        prev_input = Polygon([-0.5, 1, 0], [-1, 0, 0], [1, 0, 0], [0.5, 1, 0],
                             fill_color=color,
                             color=BLACK, stroke_width=2, fill_opacity=1.0)

        prev_input.scale(0.2).rotate(-90 * DEGREES)
        tri_input = VGroup(prev_input)
        if num_inputs > 0:
            self.add([('input_1', prev_input)])
        for i in range(1, num_inputs):
            new_input = prev_input.copy().next_to(prev_input, DOWN, buff=0.1)
            tri_input.add(new_input)
            self.add([(f'input_{i + 1}', new_input)])
            prev_input = new_input

        tri_input.next_to(fn_box, LEFT, buff=0)

        if num_outputs == 1:
            tri_output = prev_input.copy().rotate(180 * DEGREES).next_to(fn_box, RIGHT, buff=0)
            self.add([('output_1', tri_output)])
        elif num_outputs != 0:
            assert False, 'Not yet implemented'

        # Add these last, so they are on top
        self.add([('box', fn_box), ('label', fn_name_text)])
        if not user_fn:
            self.add([('desc_txt', desc_text)])

    def all_inputs(self):
        vg = VGroup()
        for i in range(0, self.num_inputs):
            vg.add(self[f'input_{i + 1}'])
        return vg

