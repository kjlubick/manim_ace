from manim import *
import numpy as np

import manimpango

from typing import Optional

from .fonts import LM_MONO, ROBOTO_MONO
from .colors import (IBM_RED_60, BLACK_07, IBM_CYAN_20, IBM_RED_20, IBM_CYAN_60,
                     STANDARD_FUNCTION_COLOR, LIBRARY_FUNCTION_COLOR,
                     SECONDARY_RECT_COLOR)
from .code import CodeWindow
from .lists import Pointer
from .utils import surround
from .variables import VariableArea, VariableBox, code_value
from .functions import Function

PC_COLOR = IBM_RED_60

TRUE_BACKGROUND_COLOR = IBM_CYAN_20
FALSE_BACKGROUND_COLOR = IBM_RED_20


class AnimatedCodeScene(MovingCameraScene):
    # It is not recommended to override the __init__ method in user Scenes.
    # For code that should be ran before a Scene is rendered, use Scene.setup() instead
    def setup(self):
        self.pc = None
        self.pc_loc = (-1, 0, 0)
        self.pc_stack = []
        self.code_window: CodeWindow = None
        self.variables: VariableArea = None
        self.functions = VGroup(name="functions")

        self.layers = [
            Group(name="Layer 0 (main)"),
            Group(name="Layer 1"),
            Group(name="Layer 2"),
            Group(name="Layer 3 (pc)"),
        ]

        fonts = manimpango.list_fonts()
        # print(fonts)
        assert (LM_MONO in fonts)
        assert (ROBOTO_MONO in fonts)

    def construct(self):
        self.camera.background_color = WHITE
        self.mobjects += self.layers
        # Make sure these are in the background
        self.add(self.functions, layer=0)

    def add(self, *mobjects, layer=0):
        """Adds the given mobject(s) to the specified layer."""
        self.layers[layer].add(*mobjects)

    def remove(self, *mobjects):
        for mobj in mobjects:
            remove_without_degrouping(self.mobjects, mobj)

    def set_code(self, cw: CodeWindow):
        self.add(cw)
        self.code_window = cw

    def set_variables(self, va: VariableArea):
        self.variables = va

    def move_pc(self, line: int, start: int, end: int):
        self.pc_loc = (line, start, end)
        target = self.code_window[f'line_{line}'][start:end]
        if not self.pc:
            self.pc = create_pc(target)
            self.add(self.pc, layer=len(self.layers) - 1)
            return Create(self.pc)
        new_pc = create_pc(target)
        return Transform(self.pc, new_pc)

    def pc_end_scope(self, line: int, scope_type: str, indents=0,
                     with_anims=[]):
        # Put if scopes slightly higher than for scopes to indicate
        # the former (usually) ends earlier than the latter.
        if scope_type == 'if':
            align = DOWN
        elif scope_type == 'for' or scope_type == 'while':
            align = UP
        else:
            assert False # unsupported

        end_of_line = Rectangle(height=0.05, width=0.3, stroke_width=self.pc.stroke_width,
                                color=PC_COLOR, name="Program Counter")
        end_of_line.align_to(self.code_window[f'label_{line}'].get_bottom(), align)
        # FIXME remove hard-coded indent width
        end_of_line.align_to(self.code_window.code_area.get_left() + 0.32 * indents, LEFT)
        self.play(Transform(self.pc, end_of_line), *with_anims)

    def create_variable(self, name: str, value,
                        source=None, shift_down: [Mobject] = [],
                        where=None, show_value=True,
                        move_pointer: Optional[Pointer] = None,
                        pointer_target: Optional[list[float]] = None):
        scope = self.variables.top_scope()
        assert name not in scope

        # Make sure the VGroup has not been disassembled
        assert scope['shelf'] in scope.submobjects

        expand_anims, new_box, height_delta = scope.create_variable(name, value, where=where)
        for mobj in shift_down:
            expand_anims.append(mobj.animate.shift(DOWN * height_delta))

        if len(expand_anims):
            self.play(*expand_anims, run_time=0.7)

        if source:
            # At this point, the entire new_box is invisible and inside the scope.
            new_box['contents'].set_opacity(1)
            # It is easiest to just make the contents look like the source
            target_contents = new_box['contents'].copy()
            new_box['contents'].become(source)
            # And remove the source.
            self.remove(source)
            # Create the box, animating each part individually, otherwise Manim
            # will add the VGroup of them all, breaking apart the scope
            self.play(*[part.animate.set_opacity(1.0) for part in new_box.all_but_contents()],
                      run_time=0.7)
            # Fill the box by making it look like how it was originally created.
            anims = [Transform(new_box['contents'], target_contents)]
            if move_pointer is not None:
                if pointer_target is None:
                    pointer_target = move_pointer.end
                anims.append(move_pointer.relocate(target_contents.get_bottom(),
                                                   pointer_target))
            self.play(*anims)
            # Make sure the intact VGroup is in the scope (and was not deconstructed)
            assert new_box in scope.submobjects
        else:
            if show_value:
                self.play(new_box.animate.set_opacity(1.0), run_time=1.0)
            else:
                self.play(*[part.animate.set_opacity(1.0) for part in new_box.all_but_contents()],
                          run_time=1.0)
        return new_box

    def update_variable(self, name, new_content, source):
        # TODO may need to resize shelf
        existing_box = self.variables.top_scope()[name]
        assert existing_box

        self.remove(source)
        self.play(*existing_box.update_contents(new_content, source))

    def numeric_calculation(self, first_name, second_name, operation,
                            first_value='', second_value='', scale=1.5,
                            data_type=int):
        if isinstance(first_name, str):
            first_var = self.variables.top_scope()[first_name]
            assert first_var
            first_value = first_var.value
            first_var = first_var['contents'].copy()
        else:
            first_var = first_name
            assert first_value
        if isinstance(second_name, str):
            second_var = self.variables.top_scope()[second_name]
            assert second_var
            second_value = second_var.value
            second_var = second_var['contents'].copy()
        else:
            second_var = second_name
            assert second_value

        first_text = code_value(first_value)
        op_text = code_value(operation).next_to(first_text, RIGHT, buff=0.2)
        second_text = code_value(second_value).next_to(op_text, RIGHT, buff=0.2)
        operation_grp = VGroup(first_text, op_text, second_text)
        operation_grp.scale(scale).next_to(self.variables, DOWN, buff=0.2)

        self.play(AnimationGroup(
            ReplacementTransform(first_var, first_text),
            FadeIn(op_text),
            ReplacementTransform(second_var, second_text),
            run_time=2, lag_ratio=0.8
        ))
        self.remove(first_text, op_text, second_text)
        self.add(operation_grp)
        self.wait(0.5)

        if operation == '*':
            result = data_type(first_value) * data_type(second_value)
        elif operation == '+':
            result = data_type(first_value) + data_type(second_value)
        else:
            assert False
        result = data_type(round(result, 6))
        result_txt = code_value(result).scale(scale)
        result_txt.next_to(self.variables, DOWN, buff=0.2)

        self.play(ReplacementTransform(operation_grp, result_txt))
        return result_txt, result

    def highlight_scope(self, scope_type: str, lines=1, indents=0,
                        loc=None):
        # assume current PC is on the keyword
        if loc is None:
            loc = self.pc_loc
        else:
            assert len(loc) == 3
        return self.code_window.highlight_scope(scope_type, lines, indents,
                                                loc[0], loc[1], loc[2])

    def set_functions_anchor(self, point):
        self.functions.next_to(point, DOWN, buff=0)
        self.functions_anchor = point

    def animate_user_fn(self, user_fn: Function, code_group: VGroup, name_group: VGroup,
                        inputs_group: VGroup, outputs_groups: [VGroup]):
        INTRA_FUNCTION_BUFFER = 0.2
        anchor = self.functions_anchor
        if len(self.functions) > 0:
            anchor = self.functions[-1]
        user_fn.next_to(anchor, DOWN, buff=INTRA_FUNCTION_BUFFER)
        user_fn.set_opacity(0)
        self.functions.add(user_fn)
        self.play(user_fn['box'].animate.set_opacity(1))

        code_copy = code_group.copy().scale_to_fit_width(user_fn['box'].width - 0.1)
        code_copy.move_to(user_fn['box'])
        self.play(ReplacementTransform(code_group.copy(), code_copy))
        self.wait(0.2)
        self.play(FadeOut(code_copy))
        self.pause()

        fn_parts_box1 = SurroundingRectangle(name_group, color=SECONDARY_RECT_COLOR,
                                             buff=0.05, corner_radius=0.1)
        self.play(Create(fn_parts_box1))

        fn_parts_box2 = SurroundingRectangle(user_fn['label'], color=SECONDARY_RECT_COLOR,
                                             buff=0.1, corner_radius=0.1)
        self.play(Create(fn_parts_box2), user_fn['label'].animate.set_opacity(1.0))
        self.pause()

        anims = [surround(fn_parts_box1, inputs_group)]
        if user_fn.num_inputs == 0:
            # Find the output spot, then go the other side.
            anims.append(surround(fn_parts_box2, user_fn['output_1'],
                                  offset=LEFT * (user_fn['box'].width + 0.2)))
        else:
            anims.append(surround(fn_parts_box2, user_fn.all_inputs()))
            for i in range(1, user_fn.num_inputs + 1):
                anims.append(user_fn[f'input_{i}'].animate.set_opacity(1.0))
        self.play(*anims)
        self.pause()

        if user_fn.num_outputs == 0:
            # Find the input spot, then go the other side.
            anims = [surround(fn_parts_box2, user_fn.all_inputs(),
                              offset=RIGHT * (user_fn['box'].width + 0.2))]
        else:
            anims = [
                user_fn['output_1'].animate.set_opacity(1.0),
                surround(fn_parts_box2, user_fn['output_1'])
            ]

        self.remove(fn_parts_box1)
        boxes_to_remove = [fn_parts_box2]
        for og in outputs_groups:
            box = fn_parts_box1.copy()
            self.add(box)
            boxes_to_remove.append(box)
            anims.append(surround(box, og))
        self.play(*anims)
        self.pause()

        self.play(FadeOut(*boxes_to_remove))
        self.remove(*boxes_to_remove)

    def push_pc(self, line, start, end, init_pc):
        self.pc_stack.append([self.pc, self.pc_loc])
        # Make sure we only have one PC in the top layer
        self.layers[-1].remove(self.pc)
        self.add(self.pc, layer=0)
        self.remove(init_pc)
        self.add(init_pc, layer=len(self.layers) - 1)
        self.pc = init_pc
        return self.move_pc(line, start, end)

    def pop_pc(self):
        assert self.pc in self.layers[-1]
        self.layers[-1].remove(self.pc)
        # Bring old PC to the top
        popped = self.pc_stack.pop()
        self.pc = popped[0]
        self.pc_loc = popped[1]
        self.remove(self.pc)
        self.add(self.pc, layer=len(self.layers) - 1)

    def cross_fade(self, start, stop, layer=0):
        temp_stop = stop.copy().move_to(start).set_opacity(0).scale_to_fit_height(start.height)
        self.remove(start)
        self.add(start, layer=layer)
        self.add(temp_stop, layer=layer)
        anim = start.animate.move_to(stop).set_opacity(0).build()
        anim.remover = True
        # Don't use an AnimationGroup - then the animations do not clean up
        # after themselves
        return [
            anim,
            ReplacementTransform(temp_stop, stop),
        ]

    def get_variable(self, name: str) -> VariableBox:
        return self.variables.top_scope()[name]


def remove_without_degrouping(mobjects: [Mobject], target: Mobject):
    if target in mobjects:
        mobjects.remove(target)
        return True
    for m in mobjects:
        if remove_without_degrouping(m.submobjects, target):
            return True
    return False


def create_pc(target: Mobject):
    return SurroundingRectangle(target,
                                buff=0.07,
                                color=PC_COLOR,
                                corner_radius=0.1,
                                name="Program Counter")
