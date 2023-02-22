from manim import *

from typing import Optional

from .colors import SECONDARY_RECT_COLOR, CHARTREUSE
from .fonts import LM_MONO
from .functions import Function
from .utils import surround
from .variables import VariableBox, code_value

class ForRange:
    def __init__(self, loop_var: VariableBox, range_code: VGroup):
        self.loop_var = loop_var
        self.range_code = range_code
        self.code_tracker = None
        self.expanded_range = None
        self.range = []
        self.index = -1


    def expand_range(self, scene: Scene, range_fn: Function,
                     start: int, start_mobj: Mobject,
                     stop: int, stop_mobj: Mobject,
                     step: Optional[int] = None, step_mobj: Optional[Mobject] = None,
                     starting_tracker: Optional[SurroundingRectangle] = None,
                     range_fn_anim: Optional[Animation] = None,
                     wait: float = 1.0):
        """Expand a range into a list without zooming in."""
        code_tracker = SurroundingRectangle(self.range_code[:-1],
                                            color=SECONDARY_RECT_COLOR,
                                            buff=0.05, corner_radius=0.1)
        if starting_tracker is None:
            scene.play(Create(code_tracker))
        else:
            scene.play(ReplacementTransform(starting_tracker,
                                            code_tracker))
        self.code_tracker = code_tracker
        if range_fn_anim is not None:
            scene.play(range_fn_anim)
        scene.wait(wait)

        # move the parameters into place
        target_height = range_fn['input_1'].height - 0.1
        anims = [
            start_mobj.animate.scale_to_fit_height(target_height)
                      .set_color(BLACK)
                      .next_to(range_fn['input_1'], LEFT, buff=0.1),
            stop_mobj.animate.scale_to_fit_height(target_height)
                     .set_color(BLACK)
                     .next_to(range_fn['input_2'], LEFT, buff=0.1),
        ]
        if step_mobj is not None:
            assert step
            anims.append(
                step_mobj.animate.scale_to_fit_height(target_height)
                         .set_color(BLACK)
                         .next_to(range_fn['input_3'], LEFT, buff=0.1))
        else:
            step = 1
            step_mobj = code_value('1')
            step_mobj.scale_to_fit_height(target_height)
            step_mobj.next_to(range_fn['input_3'], LEFT, buff=0.1)
            step_mobj.set_opacity(0.0)
            scene.add(step_mobj, layer=2)
            anims.append(step_mobj.animate.set_opacity(1.0))

        scene.play(AnimationGroup(*anims, lag_ratio=0.5))
        scene.wait(wait)

        self._make_range_and_targets(start, stop, step)

        self.expanded_range.set_opacity(0).move_to(range_fn.get_center())

        scene.play(
            start_mobj.animate.move_to(range_fn.get_center()).set_opacity(0),
            stop_mobj.animate.move_to(range_fn.get_center()).set_opacity(0),
            step_mobj.animate.move_to(range_fn.get_center()).set_opacity(0),
        )
        scene.play(
            self.expanded_range.animate.next_to(range_fn['output_1'], RIGHT, buff=0.2).set_opacity(1),
        )
        scene.remove(start_mobj, stop_mobj, step_mobj)
        scene.wait(0.2)

        target_range_txt = (self.expanded_range.copy()
                              .scale_to_fit_height(self.range_code.height)
                              .align_to(self.range_code, UL))

        scene.play(
            self.expanded_range.animate.scale_to_fit_height(self.range_code.height)
                                       .align_to(self.range_code, UL),
            self.range_code.animate.set_opacity(0.05),
            surround(code_tracker, target_range_txt),
        )

    def show_range(self, scene: Scene, start: int, stop: int, step: int = 1):
        self._make_range_and_targets(start, stop, step)
        self.expanded_range.scale_to_fit_height(self.range_code.height)
        self.expanded_range.align_to(self.range_code, UL)
        self.expanded_range.set_opacity(0)
        scene.add(self.expanded_range)

        self.code_tracker = SurroundingRectangle(self.expanded_range,
                                                 color=SECONDARY_RECT_COLOR,
                                                 buff=0.05, corner_radius=0.1)
        scene.play(
            self.expanded_range.animate.set_opacity(1.0),
            self.range_code.animate.set_opacity(0.05),
            Create(self.code_tracker),
        )

    def _make_range_and_targets(self, start: int, stop: int, step: int):
        self.range = list(range(start, stop, step))
        range_txt = code_value(str(self.range))

        targets = []
        offset = 1
        for i in range(0, len(self.range)):
            new_len = len(str(self.range[i]))
            target = range_txt[offset:offset+new_len]
            # Make the spaces less wide. How much? The width of
            # the opening square brace, which looks less wide than
            # the space.
            target.shift(LEFT * range_txt[0].width * i)
            # Also move commas and closing square brace
            range_txt[offset+new_len].shift(LEFT * range_txt[0].width * i)
            targets.append(target)
            offset += new_len
            offset += 1 # and the comma
        self.targets = targets
        self.expanded_range = range_txt


    def go_next(self, scene: Scene, wait=0.1):
        self.index += 1
        next_target = self.targets[self.index]
        scene.play(surround(self.code_tracker, next_target))
        scene.wait(wait)

        scene.play(*self.loop_var.update_contents(self.range[self.index],
                                                  next_target))


    def finish(self, scene: Scene, skip_highlight = False):
        range_box = self.code_tracker
        scene.play(range_box.animate.next_to(self.expanded_range, RIGHT, buff=0.2))
        if not skip_highlight:
            scene.wait(0.1)
            highlight = range_box.copy().set_color(CHARTREUSE)
            scene.play(Create(highlight))
            scene.wait(0.1)
            scene.play(FadeOut(range_box),
                       FadeOut(self.expanded_range),
                       FadeOut(highlight),
                       self.range_code.animate.set_opacity(1.0))
        else:
            scene.wait(0.2)
            scene.play(FadeOut(range_box),
                       FadeOut(self.expanded_range),
                       self.range_code.animate.set_opacity(1.0))

    def break_anims(self):
        return [
            FadeOut(self.code_tracker),
            FadeOut(self.expanded_range),
            self.range_code.animate.set_opacity(1.0),
        ]



