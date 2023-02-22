from manim import *

from .colors import LIGHT_BROWN
from .fonts import LM_MONO, ROBOTO_MONO
from .lists import List

SHELF_COLOR = LIGHT_BROWN


class VariableBox(VDict):
    def __init__(self, name: str, value):
        super().__init__()
        self.name = name
        self.value = value
        contents = str(value)
        if isinstance(value, str):
            contents = '"' + value + '"'
        elif isinstance(value, List):
            contents = '<list>'
        nameT = Text(name, color=BLACK, font_size=18, font=ROBOTO_MONO)
        text_height = nameT.height
        margin_vert = (0.5 - text_height) / 2

        contentsT = code_value(contents)
        box = Rectangle(height=0.5, width=nameT.width + contentsT.width + 0.5,
                        fill_color=WHITE, fill_opacity=1.0,
                        color=BLACK, stroke_width=1)
        dash = DashedLine([0, 0.45, 0], [0, 0.05, 0], color=BLACK, stroke_width=1)
        box.align_to([0, 0, 0], DL)
        nameT.align_to([0.1, text_height + margin_vert, 0], UL)
        dash.align_to(nameT.get_right() + [0.15, 0, 0], LEFT)
        contentsT.next_to(nameT, RIGHT, buff=0.3)

        # name is centered
        hd_name, hd_contents = has_dipping_char(name), has_dipping_char(contents)
        if hd_name == hd_contents:
            contentsT.align_to(nameT, DOWN).shift(UP * 0.01)
        elif hd_name and not hd_contents:
            # It would be nice if this measured the text instead of hard-coded.
            contentsT.align_to(nameT, DOWN).shift(UP * 0.05)
        else:
            contentsT.align_to(nameT, DOWN).shift(DOWN * 0.05)

        self.add([('box', box), ('name', nameT), ('contents', contentsT),
                  ('divider', dash)])

    def all_but_contents(self):
        return [self['box'], self['name'], self['divider']]

    def update_contents(self, new_value, source):
        self.value = new_value

        new_box = VariableBox(self.name, new_value)
        new_box.align_to(self.get_corner(UL), UL)

        prev_contents = self['contents'].copy()
        self['contents'].become(source)

        return [
            Transform(self['box'], new_box['box']),
            Transform(self['contents'], new_box['contents']),
            FadeOut(prev_contents),
        ]


def code_value(contents, replace_spaces=False):
    contents = str(contents)
    if replace_spaces:
        return TextWithSpaces(contents, color=BLACK, font_size=18, font=LM_MONO)
    else:
        return Text(contents, color=BLACK, font_size=18, font=LM_MONO)


def has_dipping_char(s):
    dips = 'gjpqy'
    for letter in dips:
        if letter in s:
            return True
    return False


def shelf_height(num_entries: int):
    if num_entries == 0:
        return 0.5
    return 0.5 * num_entries + 0.2 + 0.1 * (num_entries - 1)


class VariableScope(VDict):
    def __init__(self, min_variables_width=4.0, height=None,
                 vars_per_row=1):
        super().__init__()
        self.min_variables_width = min_variables_width
        self.vars_per_row = vars_per_row
        if height is None:
            height = shelf_height(0)
        shelf = Rectangle(height=height, width=min_variables_width,
                          fill_color=SHELF_COLOR, color=BLACK,
                          stroke_width=2, fill_opacity=1.0,
                          name='Variable Shelf')
        self.add([('shelf', shelf)])
        # need to keep the render order in a list
        self.variable_boxes = {}

    def create_variable(self, name: str, value, where=None) -> (Animation, VariableBox, float):
        if self.vars_per_row == 1:
            if where is None:
                where = len(self.variable_boxes)
            assert type(where) == int, where

            if len(self.variable_boxes) == 0:
                point = self['shelf'].get_corner(UL) + [0.1, -0.1, 0]
            else:
                point = self.variable_boxes[where - 1]['box'].get_corner(DL) + [0, -0.1, 0]
        elif self.vars_per_row == 2:
            if where is None:
                where = (len(self.variable_boxes) // 2, len(self.variable_boxes) % 2)
            assert len(where) == 2, where

            if where == (0, 0):
                point = self['shelf'].get_corner(UL) + [0.1, -0.1, 0]
            elif where == (0, 1):
                point = self['shelf'].get_edge_center(UP) + [0.1, -0.1, 0]
            else:
                above = self.variable_boxes.get((where[0] - 1, where[1]))
                assert above is not None, where
                y = above['box'].get_corner(DL)[1] - 0.1

                if where[0] == 0:
                    x = above['box'].get_corner(DL)[0]
                else:
                    left = self.variable_boxes.get((where[0], where[1] - 1))
                    if left is not None:
                        x = max(left['box'].get_corner(UR)[0],
                                above['box'].get_corner(DL)[0] - 0.1) + 0.1
                    else:
                        x = above['box'].get_corner(DL)[0]
                point = [x, y, 0]

        else:
            assert False

        new_box = VariableBox(name, value)
        new_box.align_to(point, UL)
        # Start everything off invisible...
        new_box.set_opacity(0)
        # ...but added to the scope
        self.add([(name, new_box)])

        # We don't want to support general re-ordering of variable boxes.
        # Too complex and probably a bit confusion.
        assert where not in self.variable_boxes, (where, self.variable_boxes)
        self.variable_boxes[where] = new_box

        width = max(self.min_variables_width,
                    max([x['box'].width + 0.2 for x in self.variable_boxes.values()]))

        height = max(self['shelf'].height,
                     shelf_height(len(self.variable_boxes) / self.vars_per_row))

        shelf2 = Rectangle(height=height,
                           width=width,
                           fill_color=SHELF_COLOR, color=BLACK,
                           stroke_width=2, fill_opacity=1.0,
                           name='shelf2')
        if shelf2.width <= self['shelf'].width and shelf2.height <= self['shelf'].height:
            return [], new_box, 0
        shelf2.align_to(self['shelf'], direction=UL)
        height_delta = shelf2.height - self['shelf'].height
        expand_anims = [Transform(self['shelf'], shelf2)]

        return expand_anims, new_box, height_delta

    # It is perfectly ok to add mobjects to a scope. It makes it
    # easier to clean things up when they go out of scope.
    # Note that all mobjects in a scope will disappear off the
    # top of the screen when it pops, so probably don't add
    # mobjects that are too far away from the "shelf".
    def add_mobj(self, key: str, mobj: Mobject):
        self.add([(key, mobj)])


class VariableArea(VDict):
    def __init__(self, min_variables_width=4.0, vars_per_row=1):
        super().__init__()
        variables_txt = Text('Variables', color=BLACK, font_size=36,
                             font=LM_MONO)
        scope = VariableScope(min_variables_width,
                              vars_per_row=vars_per_row)
        variables_txt.next_to(scope, direction=UP, buff=0.1)
        self.add([
            ('scope_0', scope),
            ('variables_txt', variables_txt),
        ])
        self.scope_stack = [scope]

    def top_scope(self) -> VariableScope:
        return self.scope_stack[-1]

    def push_variable_stack(self, initial_lines=0, vars_per_row=1):
        prev_scope = self.top_scope()
        new_scope = VariableScope(min_variables_width=prev_scope.width,
                                  height=max(shelf_height(initial_lines), prev_scope.height),
                                  vars_per_row=vars_per_row)

        target = prev_scope.get_corner(UL) + [0.09, -0.09, 0]
        # put it off screen above
        new_scope.align_to(target, LEFT).align_to([0, 4.1, 0], DOWN)
        self.add([(f'scope_{len(self.scope_stack)}', new_scope)])
        self.scope_stack.append(new_scope)
        # The animation to create the new scope will shift it down into place
        return new_scope.animate.align_to(target, UL)

    def pop_variable_stack(self, scene, pop_anims: [Animation] = []):
        old_scope = self.top_scope()
        delta = (scene.camera.frame.get_top()[1] + 0.1 -
                 old_scope.get_bottom()[1])
        scene.play(
            *pop_anims,
            old_scope.animate.shift(UP * delta),
        )
        self.scope_stack.pop()
        self.remove(f'scope_{len(self.scope_stack)}')
        scene.remove(*old_scope)
