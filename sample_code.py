from manim import *

from manim_ace.code import CodeWindow
from manim_ace.fonts import LM_MONO
from manim_ace.scene import AnimatedCodeScene
from manim_ace.variables import VariableArea

test_code = """
class ExampleScene(AnimatedCodeScene):
    def construct(self):
        super().construct()

        code = CodeWindow(test_code, tab_width=4)
        code.scale(0.8).align_to([-7.0, 3.9, 0], UL)
        self.set_code(code)
        self.pause()

        variables = VariableArea()
        variables.align_to([6.5, 3.9, 0], UR)
        self.set_variables(variables)
        self.play(FadeIn(variables))
        self.pause()

        self.play(self.move_pc(3, 0, None))
        important_txt = Text('super important', font_size=18, font=LM_MONO)
        important_txt.next_to(code['line_3'], RIGHT, buff=0.2)
        self.play(FadeIn(important_txt))
        self.wait(0.5)
        self.play(FadeOut(important_txt))

        # Notice the spaces count as positions
        self.play(self.move_pc(5, 7, None))
        self.pause()
        self.play(self.move_pc(5, 0, 6))
        self.create_variable('code', 'CodeWindow',
                             source=code['line_5'][7:17])
"""


# Render this with
# manim render -qm sample_code.py ExampleScene
class ExampleScene(AnimatedCodeScene):
    def construct(self):
        super().construct()

        code = CodeWindow(test_code, tab_width=4)
        code.scale(0.7).align_to([-7.0, 3.9, 0], UL)
        self.set_code(code)
        self.pause()

        variables = VariableArea()
        variables.align_to([6.5, 3.9, 0], UR)
        self.set_variables(variables)
        self.play(FadeIn(variables))
        self.pause()

        self.play(self.move_pc(3, 0, None))
        important_txt = Text('super important', font_size=18, font=LM_MONO)
        important_txt.next_to(code['line_3'], RIGHT, buff=0.2)
        self.play(FadeIn(important_txt))
        self.wait(0.5)
        self.play(FadeOut(important_txt))

        # Notice the spaces count as positions
        self.play(self.move_pc(5, 7, None))
        self.pause()
        self.play(self.move_pc(5, 0, 6))
        self.create_variable('code', 'CodeWindow',
                             source=code['line_5'][7:17])

        # I like to give a buffer at the end of the video to make
        # editing easier
        self.wait(2)



