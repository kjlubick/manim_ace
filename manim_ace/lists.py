from manim import *

from .fonts import LM_MONO

_EMPTY = '<empty>'


class List(VDict):
    def __init__(self, initial_contents=[],
                 horizontal=True):
        super().__init__()

        self.contents = initial_contents
        self.horizontal = horizontal

        if len(initial_contents) == 0:
            data = ['<empty>']
            # I get paranoid about using an empty list
            # from the default parameters.
            self.contents = []
        else:
            data = []
            for item in initial_contents:
                if isinstance(item, str):
                    data.append('"' + item + '"')
                elif isinstance(item, List):
                    data.append('<list>')
                else:
                    data.append(str(item))

        if horizontal:
            two_d_data = [data]
            name_mobj = create_horizontal_list(two_d_data)
        else:
            two_d_data = []
            for d in data:
                two_d_data.append([d])
            name_mobj = create_vertical_list(two_d_data)

        self.add(name_mobj.items())
        last = len(initial_contents)
        # For convenience, add div aliases
        if horizontal:
            self.zeroth_alias = (f'div_-1_0', 'left_line')
            self.last_alias = (f'div_{last - 1}_{last}', 'right_line')
        else:
            self.zeroth_alias = ('div_-1_0', 'top_line')
            self.last_alias = (f'div_{last - 1}_{last}', 'bottom_line')

        self['background_rect'].set_opacity(1.0)

    def __getitem__(self, key: typing.Hashable):
        if key == self.zeroth_alias[0]:
            key = self.zeroth_alias[1]
        elif key == self.last_alias[0]:
            key = self.last_alias[1]
        return super().__getitem__(key)

    def animate_append(self, new_item, source=None,
                       new_scale=None, new_align=None):
        if not new_scale:
            new_scale = 1.0
        if not new_align:
            new_align = (self, UL)
        new_list = List(self.contents + [new_item],
                        horizontal=self.horizontal)
        new_list.scale(new_scale).align_to(new_align[0], new_align[1])
        resize_anims = []
        for key in ['background_rect', 'top_line', 'bottom_line', 'left_line', 'right_line']:
            resize_anims.append(Transform(self[key], new_list[key]))

        copy_anims = []
        if len(self.contents) == 0:
            resize_anims.append(FadeOut(self['index_0'].copy()))
            if source is None:
                self['index_0'].become(new_list['index_0']).set_opacity(0)
                copy_anims.append(self['index_0'].animate.set_opacity(1.0))
            else:
                self['index_0'].become(source)
                copy_anims.append(Transform(self['index_0'], new_list['index_0']))
        else:
            # Relocate existing dividers and items
            for i in range(1, len(self.contents)):
                resize_anims.append(Transform(self[f'div_{i - 1}_{i}'],
                                              new_list[f'div_{i - 1}_{i}']))

            # Relocate existing items
            for i in range(0, len(self.contents)):
                resize_anims.append(Transform(self[f'index_{i}'],
                                              new_list[f'index_{i}']))

            # Create the new divider.
            new_index = len(self.contents)
            new_div = new_list[f'div_{new_index - 1}_{new_index}'].set_opacity(0)
            self.add([(f'div_{new_index - 1}_{new_index}', new_div)])
            # This can look a bit strange on Vertical lists if the width
            # changes, but I don't feel like making a better custom Animation
            # right now
            resize_anims.append(new_div.animate.set_opacity(1.0))

            # Create the new item
            new_item_mobj = new_list[f'index_{new_index}']
            target_item = new_item_mobj.copy()
            if source is None:
                new_item_mobj.set_opacity(0)
            else:
                new_item_mobj.become(source)
            self.add([(f'index_{new_index}', new_item_mobj)])
            copy_anims.append(Transform(new_item_mobj, target_item))

        self.contents.append(new_item)
        return resize_anims, copy_anims

    def animate_set(self, index: int, new_value, source: Mobject = None,
                    resize=False):
        assert len(self.contents) > 0, 'Should use append'
        assert not resize, 'Not implemented yet'
        new_align = (self, UL)
        self.contents[index] = new_value
        new_list = List(self.contents,
                        horizontal=self.horizontal)
        new_list.scale_to_fit_width(self.width).align_to(new_align[0], new_align[1])

        target_mobj = new_list[f'index_{index}']
        old_item = self[f'index_{index}'].copy()
        if source:
            source_mobj = self[f'index_{index}']
            source_mobj.become(source)
            copy_anims = [
                Transform(source_mobj, target_mobj),
                FadeOut(old_item),
            ]
        else:
            self[f'index_{index}'].become(target_mobj).set_opacity(0)
            copy_anims = [
                self[f'index_{index}'].animate.set_opacity(1),
                FadeOut(old_item),
            ]

        return [], copy_anims

    def add_background_for_cell(self, index: int, color) -> Mobject:
        back = SurroundingRectangle(VGroup(
            self[f'div_{index - 1}_{index}'],
            self[f'div_{index}_{index + 1}']),
            stroke_width=0, fill_color=color,
            fill_opacity=1.0, buff=0)
        self.submob_dict[f'back_{index}'] = back
        # Insert it in front of the background, but
        # behind everything else
        self.submobjects.insert(1, back)
        return back


def cell_fn(s, **kwargs):
    assert isinstance(s, str), s
    return Text(s, font_size=18, font=LM_MONO).set_color(BLACK).scale(1.25)


def create_horizontal_list(data):
    assert len(data) == 1, data
    assert len(data[0]) > 0, data
    data = Table(data,
                 include_outer_lines=True,
                 line_config={'stroke_width': 2, "color": BLACK},
                 element_to_mobject=cell_fn,
                 include_background_rectangle=True,
                 background_rectangle_color=WHITE,
                 h_buff=0.3, v_buff=0.2)
    name_mobj = {
        'background_rect': data[0],
        'top_line': data[2],
        'bottom_line': data[3],
        'left_line': data[4],
        'right_line': data[5],
        'index_0': data[1][0],
    }
    for i in range(1, len(data[1])):
        name_mobj[f'index_{i}'] = data[1][i]
        name_mobj[f'div_{i - 1}_{i}'] = data[5 + i]
    return name_mobj


def create_vertical_list(data):
    assert len(data) > 0, data
    assert len(data[0]) == 1, data
    data = Table(data,
                 include_outer_lines=True,
                 line_config={'stroke_width': 2, "color": BLACK},
                 element_to_mobject=cell_fn,
                 include_background_rectangle=True,
                 background_rectangle_color=WHITE,
                 h_buff=0.3, v_buff=0.2)
    name_mobj = {
        'background_rect': data[0],
        'top_line': data[2],
        'bottom_line': data[3],
        'left_line': data[-2],
        'right_line': data[-1],
        'index_0': data[1][0],
    }
    for i in range(1, len(data[1])):
        name_mobj[f'index_{i}'] = data[1][i]
        name_mobj[f'div_{i - 1}_{i}'] = data[3 + i]
    return name_mobj


# TODO This would probably be more convenient if it
# also included the <list> or <dictionary> part also
class Pointer(VDict):
    def __init__(self, start, end, tip_size=0.25, stroke_width=5):
        super().__init__()
        line = Line(start=start, end=end, stroke_width=stroke_width,
                    stroke_color=BLACK, buff=0.03)
        tip = _ArrowTriangleTip(stroke_width=0, fill_opacity=1.0,
                                length=tip_size, width=tip_size,
                                stroke_color=BLACK, fill_color=BLACK)
        line.add_tip(tip)
        self.start = start
        self.end = end
        self.tip_size = tip_size
        self.stroke_width = stroke_width

        self.add([('line', line), ('tip', tip)])

    def point_to(self, end) -> Animation:
        new_pointer = Pointer(start=self.start,
                              end=end,
                              tip_size=self.tip_size,
                              stroke_width=self.stroke_width)
        self.end = end
        return Transform(self, new_pointer)

    def point_from(self, start) -> Animation:
        new_pointer = Pointer(start=start,
                              end=self.end,
                              tip_size=self.tip_size,
                              stroke_width=self.stroke_width)
        self.start = start
        return Transform(self, new_pointer)

    def relocate(self, start, end) -> Animation:
        new_pointer = Pointer(start=start,
                              end=end,
                              tip_size=self.tip_size,
                              stroke_width=self.stroke_width)
        self.start = start
        self.end = end
        return Transform(self, new_pointer)


# not exported from Manim proper, probably by mistake
class _ArrowTriangleTip(ArrowTip, Triangle):
    r"""Triangular arrow tip."""

    def __init__(
            self,
            fill_opacity=0,
            stroke_width=3,
            length=DEFAULT_ARROW_TIP_LENGTH,
            width=DEFAULT_ARROW_TIP_LENGTH,
            start_angle=PI,
            **kwargs,
    ):
        Triangle.__init__(
            self,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            start_angle=start_angle,
            **kwargs,
        )
        self.width = width

        self.stretch_to_fit_width(length)
        self.stretch_to_fit_height(width)
