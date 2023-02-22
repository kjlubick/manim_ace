from manim import *

from .colors import TRUE_BACKGROUND_COLOR, FALSE_BACKGROUND_COLOR
from .fonts import LM_MONO


MAX_TEXT_HEIGHT = 0.5

class Condition(VDict):
    def __init__(self, surround: Mobject, state: bool):
        super().__init__()
        condition_color = SurroundingRectangle(surround,
                                               corner_radius=0.1, stroke_width=0,
                                               buff=0.02)

        if state:
            result_txt = Text('True', color=BLACK, font_size=18, font=LM_MONO)
            condition_color.set(fill_color=TRUE_BACKGROUND_COLOR)
        else:
            result_txt = Text('False', color=BLACK, font_size=18, font=LM_MONO)
            condition_color.set(fill_color=FALSE_BACKGROUND_COLOR)
        result_txt.scale_to_fit_height(min(condition_color.height - 0.1, MAX_TEXT_HEIGHT))
        result_txt.move_to(condition_color)

        self.add([('background', condition_color),
                  ('text', result_txt)])
