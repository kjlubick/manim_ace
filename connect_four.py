from manim import *
import numpy as np
import math

from manim_ace.code import CodeWindow
from manim_ace.colors import (IBM_BLUE_60, IBM_RED_60, BLACK_19, TRUE_BACKGROUND_COLOR, FALSE_BACKGROUND_COLOR,
                              IBM_CYAN_60, IBM_MAGENTA_60, IBM_PURPLE_60,
                              SECONDARY_RECT_COLOR, IBM_GREEN_20,
                              IBM_BLUE_20, TOL_ORANGE)
from manim_ace.conditionals import Condition
from manim_ace.fonts import LM_MONO, ROBOTO_MONO
from manim_ace.functions import Function
from manim_ace.lists import List, Pointer
from manim_ace.loops import ForRange
from manim_ace.scene import AnimatedCodeScene, create_pc
from manim_ace.utils import become_in_place, surround, occlude
from manim_ace.variables import VariableArea, code_value

PLAYER_ONE_COLOR = IBM_GREEN_20
PLAYER_ONE_TOKEN = 'G'
PLAYER_TWO_COLOR = IBM_BLUE_20
PLAYER_TWO_TOKEN = 'B'


# https://replit.com/@kjlubick/HarshTremendousScript#main.py
first_scene_code = """
def make_board(width, height):
  b = []
  for row in range(0, height):
    b.append([" "] * width)
  return b

def add_token(col, player, board):
  if board[0][col] != " ":
    return
  for row in range(1, len(board)):
    if board[row][col] != " ":
      board[row - 1][col] = player
      return
  board[row][col] = player

game_board = make_board(7, 6)
add_token(2, "G", game_board)
add_token(4, "B", game_board)
add_token(2, "G", game_board)
add_token(2, "B", game_board)
"""

third_scene_code = """
def winner_horizontal(b):
  for row in range(0, len(b)):
    for col in range(0, len(b[row]) - 3):
      if b[row][col] == " ":
        continue
      if (b[row][col] == b[row][col + 1] and
          b[row][col] == b[row][col + 2] and
          b[row][col] == b[row][col + 3]):
        return b[row][col]
  return " "
"""

vertical_dir_code = """
#
def winner_vertical(b):
  for row in range(0, len(b) - 3):
    for col in range(0, len(b[row])):
      if b[row][col] == " ":
        continue
      if (b[row][col] == b[row + 1][col] and
          b[row][col] == b[row + 2][col] and
          b[row][col] == b[row + 3][col]):
        return b[row][col]
  return " "
"""

diag_1_code = """
#
def winner_diagonal1(b):
  for row in range(0, len(b) - 3):
    for col in range(0, len(b[row]) - 3):
      if b[row][col] == " ":
        continue
      if (b[row][col] == b[row + 1][col + 1] and
          b[row][col] == b[row + 2][col + 2] and
          b[row][col] == b[row + 3][col + 3]):
        return b[row][col]
  return " "
"""

diag_2_code = """
#
def winner_diagonal2(b):
  for row in range(0, len(b) - 3):
    for col in range(3, len(b[row])):
      if b[row][col] == " ":
        continue
      if (b[row][col] == b[row + 1][col - 1] and
          b[row][col] == b[row + 2][col - 2] and
          b[row][col] == b[row + 3][col - 3]):
        return b[row][col]
  return " "
"""

partial_game = [
  [' ', ' ', ' ', ' ', ' ', ' ', ' '],
  [' ', ' ', ' ', ' ', ' ', ' ', ' '],
  [' ', ' ', 'G', 'G', ' ', ' ', ' '],
  [' ', 'B', 'B*', 'B', 'B', ' ', ' '],
  [' ', 'B', 'G*', 'B', 'G', ' ', ' '],
  ['B', 'G', 'G*', 'G', 'B*', 'G', ' '],
]

class BoardScene(AnimatedCodeScene):
  def construct(self):
    super().construct()

    # For rapid prototyping only
    #self.next_section(skip_animations=True)

    code = CodeWindow(first_scene_code, tab_width=2)
    code.scale(0.8).align_to([-7.0, 3.9, 0], UL)
    self.set_code(code)
    self.pause()

    variables = VariableArea()
    variables.align_to([6.5, 3.9, 0], UR)

    self.set_variables(variables)
    self.play(FadeIn(variables))
    self.pause()

    self.play(self.move_pc(1, 0, 3))
    self.play(self.highlight_scope('def', lines=4))
    self.pause()
    make_board_fn = Function('make_board()', 'make_board',
                              num_inputs=2, user_fn=True)
    self.set_functions_anchor((code.get_corner(UR) + variables.get_corner(UL)) / 2)

    self.animate_user_fn(make_board_fn, code_group=code.lines(2, 5),
                         name_group=code['line_1'][4:14],
                         inputs_group=code['line_1'][15:-2],
                         outputs_groups=[code['line_5']])
    self.pause()

    o_top = occlude(code.lines(1, 5), width=code.line_width(), buff=0.2)
    o_mid = occlude(code.lines(6, 14), width=code.line_width(), buff=0.2)
    o_bot = occlude(code.lines(16, None), width=code.line_width(), buff=0.2)

    self.add(o_top, o_mid, o_bot, layer=1)

    # fade out first function from view
    self.play(o_top.animate.set_opacity(0.9),
              self.move_pc(7, 0, 3))
    self.wait(0.5)

    self.play(self.highlight_scope('def', lines=8))
    self.wait(0.2)

    add_token_fn = Function('add_token()', 'add_token',
                            num_inputs=3, num_outputs=0, user_fn=True)

    implicit_return = Rectangle(height=0.1, width=code['line_14'][:6].width)
    implicit_return.next_to(code['line_14'][:6], DOWN, buff=0.1)
    self.animate_user_fn(add_token_fn, code_group=code.lines(8, 14),
                         name_group=code['line_7'][4:13],
                         inputs_group=code['line_7'][14:-2],
                         outputs_groups=[
                            code['line_9'],
                            code['line_13'],
                            implicit_return,
                         ])
    self.wait(0.5)

    self.play(o_mid.animate.set_opacity(0.9),
              self.move_pc(16, 13, None))
    self.wait(0.5)

    # copy parameters into place
    input_7 = code_value('7').scale(1.3).next_to(make_board_fn['input_1'], LEFT, buff=0.1)
    input_6 = code_value('6').scale(1.3).next_to(make_board_fn['input_2'], LEFT, buff=0.1)
    # The inputs move over the mostly-opaque blockers, so they should be
    # on layer 2 during animation
    self.play(
      *self.cross_fade(code['line_16'][-5].copy(), input_7, layer=2),
      *self.cross_fade(code['line_16'][-2].copy(), input_6, layer=2),
    )
    self.wait(0.2)

    # create new PC box that will be used inside of next function
    make_board_pc = create_pc(VGroup(input_6, input_7, make_board_fn))
    self.play(Create(make_board_pc))

    push_anim = variables.push_variable_stack(initial_lines=2,
                                              vars_per_row=2)
    # Need to push the PC here so the new one is in the top layer
    pc_anim = self.push_pc(1, 15, -2, init_pc=make_board_pc)
    self.play(
        push_anim,
        o_top.animate.set_opacity(0),
        o_bot.animate.set_opacity(0.9),
    )
    self.pause()
    self.play(pc_anim)
    self.pause()

    # move variables in function box...
    self.play(
      input_7.animate.next_to(make_board_fn['input_1'], RIGHT, buff=0.1),
      input_6.animate.next_to(make_board_fn['input_2'], RIGHT, buff=0.1),
    )
    self.wait(0.1)
    # ...then into the shelf
    self.create_variable('width', 7, source=input_7)
    self.wait(0.1)
    self.create_variable('height', 6, source=input_6)
    self.pause()

    self.play(self.move_pc(2, 0, None))
    self.pause()

    board_list = List()
    b_box = self.create_variable('b', board_list, show_value=False)
    board_list.next_to(variables, DOWN, buff=0.4).align_to(variables.get_left() + [-0.5, 0, 0], LEFT)
    b_pointer = Pointer(b_box['contents'].get_bottom(),
                        board_list.get_top())

    self.play(b_box['contents'].animate.set_opacity(1),
              Create(b_pointer),
              FadeIn(board_list))

    self.play(self.move_pc(3, 0, 3))
    self.wait(0.2)
    self.play(self.highlight_scope('for', lines=1, indents=1))
    self.pause()

    self.play(self.move_pc(3, 4, 7))

    row_var = self.create_variable('row', 0, show_value=False,
                                   shift_down=[b_pointer, board_list])
    self.pause()

    range_fn = Function(name="range()", desc="count from\nstart to stop\nby step",
                        num_inputs=3)
    range_fn.next_to(add_token_fn, DOWN, buff=0.2).set_opacity(0)
    self.add(range_fn)

    make_board_range = ForRange(loop_var=row_var,
                                range_code=code['line_3'][11:])

    start_mobj = code['line_3'][17].copy()
    stop_mobj = self.get_variable('height')['contents'].copy()
    self.add(start_mobj, stop_mobj, layer=2)

    make_board_range.expand_range(self,
                                  range_fn=range_fn,
                                  range_fn_anim=range_fn.animate.set_opacity(1.0),
                                  start=0, start_mobj=start_mobj,
                                  stop=6, stop_mobj=stop_mobj)
    self.pause()

    # Allocate all the space for our lists
    prev_list = board_list.get_bottom() + [0, 0.1, 0]
    rows = []
    for i in range(0, 6):
      temp_list = List([PLAYER_ONE_TOKEN] * 7).next_to(prev_list, DOWN, buff=0.4)
      temp_list.scale(0.9).align_to([7, 0, 0], RIGHT)
      for j in range(0, 7):
        # Remove the placeholder R glyph (but not the quotes) so it
        # looks like a space
        temp_list[f'index_{j}'].remove(temp_list[f'index_{j}'][1])
        temp_list['background_rect'].set_opacity(0)
      rows.append(temp_list)
      prev_list = temp_list

    arrows = []
    for i in range(0, 6):
      make_board_range.go_next(self)
      self.wait(1.0 if i == 0 else 0.2)
      self.play(self.move_pc(4, 9, -1))
      self.wait(1.0 if i == 0 else 0.2)
      cover_rect = SurroundingRectangle(
        VGroup(rows[i]['div_0_1'], rows[i]['right_line']),
        stroke_width=0, fill_opacity=1.0, fill_color=WHITE, buff=0.1)
      cover_rect.shift(RIGHT * 0.105)
      rows[i].set_opacity(0)
      self.add(rows[i])
      self.add(cover_rect)
      left_bracket = code['line_4'][9].copy()
      left_quote = code['line_4'][10].copy()
      right_quote = code['line_4'][12].copy()
      right_bracket = code['line_4'][13].copy()
      times_txt = Text('*', color=BLACK, font_size=18, font=LM_MONO)
      times_txt.next_to(rows[i]['div_0_1'], RIGHT, buff=0.2)
      seven_txt = self.get_variable('width')['contents'].copy()
      # These will move over the opaque areas
      self.add(left_bracket, left_quote, right_quote, right_bracket, layer=2)
      self.play(
        left_bracket.animate.move_to(rows[i]['left_line']),
        right_bracket.animate.move_to(rows[i]['div_0_1']),
        Transform(left_quote, rows[i]['index_0'][0].copy().set_opacity(1)),
        Transform(right_quote, rows[i]['index_0'][1].copy().set_opacity(1)),
        FadeIn(times_txt),
        seven_txt.animate.scale(1.3).next_to(times_txt, RIGHT, buff=0.2),
      )
      self.wait(1.0 if i == 0 else 0.2)
      self.play(FadeOut(left_bracket), FadeOut(right_bracket),
                FadeOut(left_quote), FadeOut(right_quote),
                rows[i].animate.set_opacity(1.0))
      self.wait(0.2)
      self.play(VGroup(cover_rect, times_txt, seven_txt)
                       .animate.align_to([7.2, 0, 0], LEFT))
      self.remove(times_txt, seven_txt, cover_rect)
      self.wait(1.0 if i == 0 else 0.2)

      self.play(self.move_pc(4, 0, None))
      self.wait(0.2)

      resize_anims, copy_anims = board_list.animate_append(rows[i], new_scale=0.61)
      self.play(*resize_anims, b_pointer.point_to([
          board_list['index_0'].get_top()[0],  # center on the item
          board_list.get_top()[1],             # but pointing to the box
          0]
      ))
      start = board_list[f'index_{i}'].get_bottom()
      stop = np.array([
        rows[i]['index_0'].get_top()[0],
        rows[i].get_top()[1],
        0])
      new_pointer = Pointer(start, stop)
      self.bring_to_back(new_pointer)
      self.play(Create(new_pointer), *copy_anims)
      arrows.append(new_pointer)

      self.wait(1.0 if i == 0 else 0.2)
      self.pc_end_scope(4, scope_type='for', indents=1)
      self.wait(1.0 if i == 0 else 0.2)
      self.play(self.move_pc(3, 4, 7))
      self.wait(0.2)

    # FIXME code to add the stuff faster than animating it
    # fast_board_list = List([rows[0]] * 6).scale(0.61).align_to(board_list, UL)
    # self.remove(board_list)
    # self.add(fast_board_list)
    # board_list = fast_board_list
    # for i in range(1, 6):
    #   start = board_list[f'index_{i}'].get_bottom()
    #   stop = np.array([
    #     rows[i]['index_0'].get_bottom()[0],
    #     rows[i].get_top()[1],
    #     0])
    #   new_pointer = Pointer(start, stop)
    #   self.bring_to_back(new_pointer)
    # self.add(*rows[1:])
    # # end FIXME

    make_board_range.finish(self)
    self.wait(0.1)
    self.play(self.move_pc(5, 0, None))
    self.pause()

    rv = b_box['contents'].copy()
    rv_ptr = b_pointer.copy()

    rv_target = rv.copy().next_to(make_board_fn['output_1'], RIGHT, buff=0)

    self.play(rv.animate.become(rv_target),
              rv_ptr.point_from(rv_target.get_bottom()),
    )
    self.pause()
    self.play(
      Indicate(rv_ptr, color=IBM_CYAN_60, scale_factor=0.95),
      Indicate(b_pointer, color=IBM_MAGENTA_60, scale_factor=0.95),
    )
    self.pause()

    top_pc = self.pc
    pop_anims = [
      o_bot.animate.set_opacity(0),
      o_top.animate.set_opacity(0.9),
      top_pc.animate.set_opacity(0),
    ]
    # Give b_pointer to the top scope so it can be removed with the pop
    self.remove(b_pointer)
    variables.top_scope().add_mobj('pointer', b_pointer)
    variables.pop_variable_stack(self, pop_anims=pop_anims)
    self.pop_pc()
    self.wait(0.5)

    self.play(self.move_pc(16, 0, 12))
    self.wait(0.1)
    self.create_variable('game_board', board_list, source=rv,
                         move_pointer=rv_ptr)

    # Print some things to help reset the next scene
    print('function anchor', self.functions_anchor)
    print('board_list ul', board_list.get_corner(UL))
    print('first row ul', rows[0].get_corner(UL))

    self.wait(2)


class AddTokenScene(AnimatedCodeScene):
  def construct(self):
    super().construct()

    # Keep for setup
    self.next_section(skip_animations=True)

    code = CodeWindow(first_scene_code, tab_width=2)
    code.scale(0.8).align_to([-7.0, 3.9, 0], UL)
    self.set_code(code)

    variables = VariableArea()
    variables.align_to([6.5, 3.9, 0], UR)

    self.set_variables(variables)
    self.add(variables)

    self.play(self.highlight_scope('def', lines=4, loc=(1, 0, 3)),
              self.highlight_scope('def', lines=8, loc=(7, 0, 3)),
              self.highlight_scope('for', lines=1, loc=(3, 0, 3), indents=1))

    self.set_functions_anchor((code.get_corner(UR) + variables.get_corner(UL)) / 2)

    make_board_fn = Function('make_board()', 'make_board',
                             num_inputs=2, user_fn=True)
    add_token_fn = Function('add_token()', 'add_token',
                            num_inputs=3, num_outputs=0, user_fn=True)
    range_fn = Function(name="range()", desc="count from\nstart to stop\nby step",
                        num_inputs=3)
    make_board_fn.next_to(self.functions_anchor, DOWN, buff=0.2)
    self.functions.add(make_board_fn)
    add_token_fn.next_to(make_board_fn, DOWN, buff=0.2)
    self.functions.add(add_token_fn)
    range_fn.next_to(add_token_fn, DOWN, buff=0.2)
    self.functions.add(range_fn)

    o_top = occlude(code.lines(1, 5), width=code.line_width(), buff=0.2)
    o_mid = occlude(code.lines(6, 14), width=code.line_width(), buff=0.2)
    o_bot = occlude(code.lines(15, None), width=code.line_width(), buff=0.2)
    o_bot.shift(DOWN*0.3)

    self.add(o_top, o_mid, o_bot, layer=1)
    o_top.set_opacity(0.9)
    o_mid.set_opacity(0.9)

    # board_list ul [2.         1.70003906 0.        ]
    # first row ul [ 2.23817386e+00  9.35778823e-01 -5.44229253e-18]

    rows = []
    for i in range(0, 6):
      temp_list = List([PLAYER_ONE_TOKEN] * 7)
      if i == 0:
        temp_list.scale(0.9)
        temp_list.align_to([2.238173, 0.9357788, 0], UL)
      else:
        temp_list.next_to(prev_list, DOWN, buff=0.4)
        temp_list.scale(0.9).align_to([7, 0, 0], RIGHT)
      for j in range(0, 7):
        # Remove the placeholder R glyph (but not the quotes) so it
        # looks like a space
        temp_list[f'index_{j}'].remove(temp_list[f'index_{j}'][1])
      temp_list.contents = [' '] * 7
      rows.append(temp_list)
      prev_list = temp_list

    board_list = List([rows[0]] * 6).scale(0.61).align_to([2, 1.7, 0], UL)
    game_board_box = self.create_variable('game_board', board_list)
    b_pointer = Pointer(game_board_box['contents'].get_bottom(),
      [board_list['index_0'].get_top()[0],
       board_list.get_top()[1],
       0])
    self.add(board_list, b_pointer)

    arrows = []
    for i in range(0, 6):
      start = board_list[f'index_{i}'].get_bottom()
      stop = np.array([
        rows[i]['index_0'].get_bottom()[0],
        rows[i].get_top()[1],
        0])
      new_pointer = Pointer(start, stop)
      self.bring_to_back(new_pointer)
      arrows.append(new_pointer)
    self.add(*rows)
    self.play(self.move_pc(16, 0, 12))

    self.add_token_fn = add_token_fn
    self.arrows = arrows
    self.board_list = board_list
    self.code = code
    self.game_board_pointer = b_pointer
    self.range_fn = range_fn
    self.rows = rows
    self.variables = variables
    self.o_mid = o_mid
    self.o_bot = o_bot
    self.color_backs = {}

    # Setup from last scene complete, start animations
    self.next_section()
    self.pause()

    self.play(surround(self.pc,
                       VGroup(code['line_17'],
                              code['line_18'],
                              code['line_19'],
                              code['line_20'],
                              )
                       )
            )
    self.pause()

    piece = self.make_piece(PLAYER_ONE_TOKEN)
    piece.move_to(rows[0]['index_2']).align_to(rows[0].get_top() + [0, 0.1, 0], DOWN)
    pieces = [piece]
    self.play(FadeIn(piece), run_time=0.3)
    self.play(piece.animate.align_to(rows[5].get_bottom(), DOWN),
              rate_func=rate_functions.ease_out_bounce, run_time=1.1)
    self.wait(0.1)
    piece = self.make_piece(PLAYER_TWO_TOKEN)
    piece.move_to(rows[0]['index_4']).align_to(rows[0].get_top() + [0, 0.1, 0], DOWN)
    pieces.append(piece)
    self.play(FadeIn(piece), run_time=0.2)
    self.play(piece.animate.align_to(rows[5].get_bottom(), DOWN),
              rate_func=rate_functions.ease_out_bounce, run_time=1.1)
    self.wait(0.1)
    piece = self.make_piece(PLAYER_ONE_TOKEN)
    piece.move_to(rows[0]['index_2']).align_to(rows[0].get_top() + [0, 0.1, 0], DOWN)
    pieces.append(piece)
    self.play(FadeIn(piece), run_time=0.2)
    self.play(piece.animate.align_to(rows[4].get_bottom(), DOWN),
              rate_func=rate_functions.ease_out_bounce, run_time=1.0)
    self.wait(0.1)
    piece = self.make_piece(PLAYER_TWO_TOKEN)
    piece.move_to(rows[0]['index_2']).align_to(rows[0].get_top() + [0, 0.1, 0], DOWN)
    pieces.append(piece)
    self.play(FadeIn(piece), run_time=0.2)
    self.play(piece.animate.align_to(rows[3].get_bottom(), DOWN),
              rate_func=rate_functions.ease_out_bounce, run_time=0.9)
    self.pause()

    self.play(self.move_pc(17, 0, None),
              FadeOut(pieces[1]), FadeOut(pieces[2]), FadeOut(pieces[3]),
              )
    self.pause()

    # index reminder
    indexes = []
    for i in range(0, 7):
      idx_txt = Text(str(i), font_size=18, font=LM_MONO, color=BLACK)
      idx_txt.scale(1.6).next_to(rows[-1][f'index_{i}'], DOWN, buff=0.35)
      indexes.append(idx_txt)
    idx_txt = Text('Indexes', font_size=18, font=LM_MONO, color=BLACK)
    idx_txt.scale(1.2).next_to(indexes[0], LEFT, buff=0.3)
    indexes.insert(0, idx_txt)
    self.play(
      AnimationGroup(*[FadeIn(x) for x in indexes], lag_ratio=0.2),
      run_time=1.2
    )
    self.pause()

    self.play(FadeOut(pieces[0]),
              *[FadeOut(x) for x in indexes])
    self.pause()

    self.animate_add_token(2, PLAYER_ONE_TOKEN, first=True)
    self.pause()

    self.play(self.move_pc(18, 0, None))
    self.animate_add_token(4, PLAYER_TWO_TOKEN)
    self.wait(0.5)

    self.play(self.move_pc(19, 0, None))
    self.animate_add_token(2, PLAYER_ONE_TOKEN)
    self.wait(0.5)

    self.play(self.move_pc(20, 0, None))
    self.animate_add_token(2, PLAYER_TWO_TOKEN)
    self.wait(0.5)

    # For rapid prototyping
    # _, copy_anims = self.rows[5].animate_set(2, PLAYER_ONE_TOKEN)
    # self.rows[5].add_background_for_cell(2, PLAYER_ONE_COLOR)
    # self.play(*copy_anims)
    # _, copy_anims = self.rows[5].animate_set(4, PLAYER_TWO_TOKEN)
    # self.rows[5].add_background_for_cell(4, PLAYER_TWO_COLOR)
    # self.play(*copy_anims)
    # _, copy_anims = self.rows[4].animate_set(2, PLAYER_ONE_TOKEN)
    # self.rows[4].add_background_for_cell(2, PLAYER_ONE_COLOR)
    # self.play(*copy_anims)
    # _, copy_anims = self.rows[3].animate_set(2, PLAYER_TWO_TOKEN)
    # self.rows[3].add_background_for_cell(2, PLAYER_TWO_COLOR)
    # self.play(*copy_anims)
    # self.play(self.move_pc(20, 0, None))
    # self.len_fn = Function('len()', 'Count items',
    #                     num_inputs=1)
    # self.len_fn.next_to(self.range_fn, DOWN, buff=0.2)
    # self.functions.add(self.len_fn)
    # end rapid prototyping
    #self.next_section()

    # "Let's imagine the players play some more turns, adding several more
    # tokens each. <pause> Now, we can look at the code which detects if
    # a player has won, starting with identifying four tokens in a row horizontally.""
    anims = [FadeOut(self.pc), FadeOut(o_mid), FadeOut(o_top)]
    for r in range(0, len(partial_game)):
      for c in range(0, len(partial_game[0])):
        token = partial_game[r][c]
        if token == ' ' or '*' in token:
          continue
        _, copy_anims = self.rows[r].animate_set(c, token)
        color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
        back = self.rows[r].add_background_for_cell(c, color)
        back.set_opacity(0)
        anims += copy_anims
        anims.append(back.animate.set_opacity(1.0))

    new_code = CodeWindow(third_scene_code, tab_width=2, start_at_line=21)
    new_code.scale(0.8).align_to(code.get_corner(DL) + [0.0, -0.105, 0], UL)
    anims += [FadeIn(new_code)]

    self.play(*anims, run_time=1.5)
    self.wait(0.1)
    self.play(code.animate.align_to([-7.0, 0.59, 0], DL),
              new_code.animate.align_to([-7.0, 0.5, 0], UL),
              self.functions[:2].animate.shift(
                  [0, self.camera.frame.get_top()[1] - range_fn.get_top()[1], 0]),
              self.functions[2:].animate.shift(
                  [0, self.camera.frame.get_top()[1] - range_fn.get_top()[1] - 0.3, 0]),
              run_time=1.5)
    self.play(code.animate.set_opacity(0),
              new_code.highlight_scope('def', lines=9, indents=0,
                                       line=21, start=0, end=3)
      )
    print("Functions UL", self.functions[2:].get_corner(UL))
    self.wait(2)


  def make_piece(self, token: str):
    radius = (self.rows[0]['div_0_1'].get_left() -
              self.rows[0]['div_1_2'].get_left())[0] / 2
    color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
    circle = Circle(radius=radius, fill_color=color,
                    fill_opacity=1.0,
                    stroke_color=BLACK, stroke_width=2)
    txt = code_value(token).scale(1.5).move_to(circle)
    return VGroup(circle, txt)


  def animate_add_token(self, col, player, first=False):
    code = self.code
    call_line = self.pc[0]
    input_col = (code_value(str(col)).scale(1.3)
                 .next_to(self.add_token_fn['input_1'], LEFT, buff=0.2))
    input_player = (code_value(f'"{player}"').scale(1.3)
                    .next_to(self.add_token_fn['input_2'], LEFT, buff=0.1))
    game_board_var = self.get_variable('game_board')
    input_board = game_board_var['contents'].copy()
    input_arrow = self.game_board_pointer.copy()
    self.add(input_board, layer=2)
    self.play(
      *self.cross_fade(code[f'line_{call_line}'][10].copy(), input_col, layer=2),
      *self.cross_fade(code[f'line_{call_line}'][13:16].copy(), input_player, layer=2),
      input_board.animate.next_to(self.add_token_fn['input_3'], LEFT, buff=0.0),
      input_arrow.relocate(self.add_token_fn['input_3'].get_left(),
                           self.board_list.get_left()),
      run_time = 1.2
    )
    self.remove(input_player) # small layer fix
    self.add(input_player, layer=2)
    self.wait(1.0 if first else 0.2)

    add_token_pc = create_pc(VGroup(input_board, self.add_token_fn))
    self.add(add_token_pc, layer=2)
    self.play(Create(add_token_pc))
    if 'game_board_pointer' not in self.variables:
      # Add the game_board_pointer to the variables area, so it is above
      # the scope_0, but below scope_1
      self.remove(self.game_board_pointer)
      self.variables.add([('game_board_pointer', self.game_board_pointer)])
    push_anim = self.variables.push_variable_stack(initial_lines=2,
                                                   vars_per_row=2)

    # Need to push the PC here so the new one is in the top layer
    pc_anim = self.push_pc(7, 14, -2, init_pc=add_token_pc)
    self.play(
        push_anim,
        self.o_mid.animate.set_opacity(0),
        self.o_bot.animate.set_opacity(0.9),
        self.game_board_pointer.animate.set_color(BLACK_19),
    )
    self.wait(1.0 if first else 0.2)
    self.play(pc_anim)
    self.wait(1.0 if first else 0.2)

    # move variables into box
    shift_right = self.add_token_fn['input_3'].width + input_board.width
    self.play(
      input_col.animate.next_to(self.add_token_fn['input_1'], RIGHT, buff=0.2),
      input_player.animate.next_to(self.add_token_fn['input_2'], RIGHT, buff=0.1),
      input_board.animate.shift(RIGHT * shift_right),
      input_arrow.point_from(input_arrow.start + [shift_right, 0, 0]),
    )
    self.wait(0.1)
    col_var = self.create_variable('col', col, source=input_col)
    self.wait(0.1)
    self.create_variable('player', player, source=input_player)
    self.wait(0.1)
    # Have to put arrow on top of the scope again
    self.remove(input_arrow)
    self.add(input_arrow, layer=1)
    self.board_pointer = input_arrow
    new_target = [self.board_list['index_0'].get_top()[0],
                  self.board_list.get_top()[1],
                  0]
    board_var = self.create_variable('board', self.board_list, source=input_board,
                                     move_pointer=input_arrow,
                                     pointer_target=new_target)
    self.wait(1.0 if first else 0.2)

    self.play(self.move_pc(8, 0, 2))
    self.wait(0.5 if first else 0.2)

    if first:
      self.play(self.highlight_scope('if', lines=1, indents=1))
      self.pause()

    # Before Python evaluates this condition,
    self.play(self.move_pc(8, 3, -1))
    self.wait(0.5 if first else 0.2)

    if first:
      # it needs to evaluate the left side, with some complex looking syntax.
      board_code_rect = SurroundingRectangle(code['line_8'][3:16],
                                             color=IBM_PURPLE_60,
                                             buff=0.03, corner_radius=0.1)
      board_list_rect = SurroundingRectangle(board_var,
                                             color=IBM_PURPLE_60,
                                             stroke_width=5,
                                             buff=0.08, corner_radius=0.1)
      self.add(board_code_rect, layer=3)
      self.play(Create(board_code_rect))
      self.pause()

      # Python first finds the list in the board variable
      self.play(surround(board_code_rect, code['line_8'][3:8]))
      self.wait(0.2)
      self.add(board_list_rect, layer=2)
      self.play(Create(board_list_rect))
      self.wait(0.1)
      self.play(
          traverse(self.board_pointer),
          surround(board_list_rect, self.board_list))
      self.pause()

      # Then looks at index 0, due to the first set of square brackets.
      self.play(surround(board_code_rect, code['line_8'][3:11]))
      self.wait(0.1)
      self.play(surround(board_list_rect,
                         VGroup(self.board_list[f'left_line'],
                                self.board_list[f'div_0_1'])))
      self.wait(0.2)
      # Index 0 of board is another list corresponding to the top row in the game.
      self.play(
          traverse(self.arrows[0]),
          surround(board_list_rect, self.rows[0]))
      self.pause()

      # The next set of square brackets looks in the top row list for the item at
      # index 2, based on the col variable.
      self.play(surround(board_code_rect, code['line_8'][3:16]))
      self.wait(0.1)
      col_code = code['line_8'][12:15]
      col_reminder = col_var['contents'].copy()
      self.play(
          col_code.animate.set_opacity(0.1),
          col_reminder.animate.scale(1.3).move_to(col_code),
      )
      self.wait(0.2)
      # Remember index 2 refers to the third item in the list, that is the third
      # column, because Python lists start counting at 0.
      self.play(surround(board_list_rect,
                         VGroup(self.rows[0][f'div_{col-1}_{col}'],
                                self.rows[0][f'div_{col}_{col+1}'])))
      self.pause()

      item_mobj = self.rows[0][f'index_{col}'].copy()
      item = self.rows[0].contents[col]
      condition_code = code['line_8'][3:16]
      self.play(
          FadeOut(col_reminder),
          condition_code.animate.set_opacity(0.07),
          item_mobj.animate.scale(1.3).move_to(condition_code)
                                      .align_to(condition_code, UP),
      )
      self.wait(0.1)
      self.play(FadeOut(board_code_rect), FadeOut(board_list_rect))
      self.pause()
    else: # not first
      item_mobj, item = self.get_from_board(0, col,
                                            first_code=code['line_8'][3:8],
                                            second_code=code['line_8'][3:11],
                                            full_code=code['line_8'][3:16])
      condition_code = code['line_8'][3:16]

    condition = item != " "
    condition_txt = Condition(code['line_8'][3:-1],
                              state=condition).set_opacity(0)
    self.add(condition_txt, layer=1)
    self.play(condition_txt.animate.set_opacity(0.95))
    self.wait(1.0 if (first or condition) else 0.2)
    if condition:
      assert False # not impl yet

    self.pc_end_scope(9, scope_type='if', indents=1)
    self.wait(0.2)
    self.play(condition_code.animate.set_opacity(1.0),
              FadeOut(item_mobj), FadeOut(condition_txt),
              self.move_pc(10, 0, 3))
    self.wait(1.0 if first else 0.2)

    # For loop begins
    if first:
      self.play(self.highlight_scope('for', lines=3, indents=1))
      self.pause()

    self.play(self.move_pc(10, 4, 7))
    self.wait(0.1)
    row_var = self.create_variable('row', 1, show_value=False)

    if first:
      len_fn = Function('len()', 'Count items',
                        num_inputs=1)
      len_fn.next_to(self.range_fn, DOWN, buff=0.2)
      self.len_fn = len_fn
      self.functions.append(len_fn)

    len_code = code['line_10'][-12:-2]
    len_rect = SurroundingRectangle(len_code,
                                    color=SECONDARY_RECT_COLOR,
                                    buff=0.08, corner_radius=0.1)
    self.play(Create(len_rect))
    self.wait(1.0 if first else 0.2)
    if first:
      self.play(FadeIn(self.len_fn))
      self.wait(0.2)

    temp_list = self.board_list.copy()
    self.add(temp_list, layer=1)
    self.play(temp_list.animate.next_to(self.len_fn['input_1'], LEFT, buff=0.1),
              run_time=1.2)
    self.wait(0.2)
    six_len = code_value('6').set_opacity(0).move_to(self.len_fn['box'])
    self.play(temp_list.animate.scale_to_fit_width(self.len_fn['box'].width)
                       .move_to(self.len_fn['box'])
                       .set_opacity(0))
    self.remove(temp_list)
    self.add(six_len, layer=1)
    self.play(six_len.animate.scale(1.3).set_opacity(1.0)
                     .next_to(self.len_fn['output_1'], RIGHT, buff=0.1))
    self.wait(0.1)
    self.play(
        len_code.animate.set_opacity(0.1),
        six_len.animate.move_to(len_code),
    )
    self.wait(1.0 if first else 0.2)

    add_token_range = ForRange(loop_var=row_var,
                               range_code=code['line_10'][11:])
    add_token_range.expand_range(self, range_fn=self.range_fn,
                                 start=1, start_mobj=code['line_10'][17].copy(),
                                 stop=6, stop_mobj=six_len,
                                 starting_tracker=len_rect,
                                 wait = 1.0 if first else 0.2)
    self.wait(1.0 if first else 0.2)

    did_break = False
    for row in range(1, 6):
      add_token_range.go_next(self)
      self.play(self.move_pc(11, 0, 2))
      self.wait(0.2)
      if first and row == 1:
        self.play(self.highlight_scope('if', lines=2, indents=2))
        self.pause()
      self.play(self.move_pc(11, 3, -1))
      item_mobj, item = self.get_from_board(row, col, slow=(first and row == 1),
                                            first_code=code['line_11'][3:8],
                                            second_code=code['line_11'][3:13],
                                            full_code=code['line_11'][3:18])
      self.wait(0.5 if (first and row == 1) else 0.2)

      condition = item != " "
      condition_txt = Condition(code['line_11'][3:-1],
                                state=condition).set_opacity(0)
      self.add(condition_txt, layer=1)
      self.play(condition_txt.animate.set_opacity(0.95))
      self.wait(1.0 if (first or condition) else 0.3)

      if condition:
        self.play(self.move_pc(12, 0, None))
        self.play(FadeOut(condition_txt),
                  FadeOut(item_mobj),
                  code['line_11'][3:18].animate.set_opacity(1.0),
        )
        self.wait(0.2)
        self.set_into_board(player, row - 1, col,
                            first_code=code['line_12'][:5],
                            second_code=code['line_12'][:14],
                            full_code=code['line_12'][:19],
                            row_indicate=[code['line_12'][6:13]])
        self.pause()
        self.play(self.move_pc(13, 0, None))
        self.wait(0.5)
        did_break = True
        break

      self.pc_end_scope(13, scope_type='if', indents=2,
                        with_anims=[FadeOut(condition_txt),
                                    FadeOut(item_mobj),
                                    code['line_11'][3:18].animate.set_opacity(1.0)])
      self.wait(0.1)

      self.pc_end_scope(13, scope_type='for', indents=1)
      self.wait(0.1)
      self.play(self.move_pc(10, 4, 7))
      self.wait(0.1)

    if not did_break:
      add_token_range.finish(self)
      self.wait(0.1)
      self.play(self.move_pc(14, 0, None))

      self.wait(1.0 if first else 0.2)
      self.set_into_board(player, row, col,
                          first_code=code['line_14'][:5],
                          second_code=code['line_14'][:10],
                          full_code=code['line_14'][:15])
      self.wait(1.0 if first else 0.2)

      self.pc_end_scope(14, scope_type='for', indents=1)
      self.wait(1.0 if first else 0.2)
    pop_anims = []
    if first:
      implicit_return = code['line_9'].copy()
      implicit_return.next_to(code['line_14'][:6], DOWN, buff=0.05)
      self.add(implicit_return, layer=1)
      self.play(surround(self.pc, implicit_return),
                FadeIn(implicit_return))
      self.pause()
      pop_anims.append(FadeOut(implicit_return))

    mid_pc = self.pc
    pop_anims += [
        self.o_mid.animate.set_opacity(0.9),
        self.o_bot.animate.set_opacity(0),
        mid_pc.animate.set_opacity(0),
        self.game_board_pointer.animate.set_color(BLACK),
    ]
    if did_break:
      pop_anims += add_token_range.break_anims()
    # Give board_pointer to the top scope, so it can go away on pop.
    self.remove(self.board_pointer)
    self.variables.top_scope().add_mobj('pointer', self.board_pointer)
    self.variables.pop_variable_stack(self, pop_anims=pop_anims)
    self.board_pointer = None
    self.pop_pc()

  def get_from_board(self, row: int, col: int, first_code: Mobject = None,
                     second_code: Mobject = None, full_code: Mobject = None,
                     slow: bool = False) -> Mobject:
    row_indicate = []
    if row != 0:
      row_var = self.get_variable('row')
      row_indicate = [row_var['name'], row_var['contents']]
    code_rect, list_rect = self.get_to_board(row, col, first_code, second_code,
                                             full_code, row_indicate=row_indicate,
                                             slow=slow)
    self.wait(0.5 if slow else 0.2)
    list_item = self.rows[row][f'index_{col}'].copy()
    self.play(
        full_code.animate.set_opacity(0.07),
        list_item.animate.scale(1.3).move_to(full_code)
                                    .align_to(full_code, UP),
    )
    self.wait(0.1)
    self.play(FadeOut(code_rect), FadeOut(list_rect))
    return list_item, self.rows[row].contents[col]

  def set_into_board(self, player: str, row: int, col: int,
                     first_code: Mobject = None,
                     second_code: Mobject = None,
                     full_code: Mobject = None,
                     row_indicate: [Mobject] = None,
                     slow = False):
    assert player == PLAYER_ONE_TOKEN or player == PLAYER_TWO_TOKEN
    if row_indicate is None:
      row_var = self.get_variable('row')
      row_indicate = [row_var['name'], row_var['contents']]
    code_rect, list_rect = self.get_to_board(row, col, first_code, second_code,
                                             full_code, row_indicate = row_indicate,
                                             slow = slow)
    self.wait(1.0 if slow else 0.2)
    player_var = self.get_variable('player')
    # Move to upper layer during animation, so the new item is over the scope
    self.remove(self.rows[row])
    self.add(self.rows[row], layer=2)
    _, copy_anims = self.rows[row].animate_set(col, player_var.value,
                                               source=player_var['contents'],
                                               resize=False)
    self.play(*copy_anims)
    self.bring_to_front(self.rows[row])
    color = PLAYER_ONE_COLOR if player == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
    back = self.rows[row].add_background_for_cell(col, color)
    back.set_opacity(0.0)
    self.play(back.animate.set_opacity(1.0),
            FadeOut(code_rect), FadeOut(list_rect),
    )


  def get_to_board(self, row: int, col: int, first_code: Mobject = None,
                   second_code: Mobject = None, full_code: Mobject = None,
                   row_indicate: [Mobject] = [], slow: bool = False):
    board_list = self.board_list
    code_rect = SurroundingRectangle(first_code,
                                     color=IBM_PURPLE_60,
                                     buff=0.03, corner_radius=0.1)
    list_rect = SurroundingRectangle(board_list,
                                     color=IBM_PURPLE_60,
                                     stroke_width=5,
                                     buff=0.08, corner_radius=0.1)
    self.add(code_rect, list_rect, layer=3)
    self.play(Create(code_rect), Create(list_rect),
              traverse(self.board_pointer))
    self.wait(0.5 if slow else 0.2)

    row_anims = [surround(code_rect, second_code),
                 surround(list_rect, VGroup(board_list[f'div_{row-1}_{row}'],
                                            board_list[f'div_{row}_{row+1}']))]
    row_anims += [
      Indicate(mobj, color=IBM_PURPLE_60, scale_factor=1.3,
                rate_func=there_and_back_with_pause)
      for mobj in row_indicate
    ]
    self.play(*row_anims)
    self.wait(0.1)
    self.play(traverse(self.arrows[row]),
              surround(list_rect, self.rows[row])
    )
    self.wait(0.5 if slow else 0.2)
    col_var = self.get_variable('col')
    self.play(
        surround(code_rect, full_code),
        surround(list_rect,
                 VGroup(self.rows[row][f'div_{col-1}_{col}'],
                        self.rows[row][f'div_{col}_{col+1}'])),
        Indicate(col_var['name'], color=IBM_PURPLE_60, scale_factor=1.2,
                  rate_func=there_and_back_with_pause),
        Indicate(col_var['contents'], color=IBM_PURPLE_60, scale_factor=1.4,
                  rate_func=there_and_back_with_pause),
    )
    return code_rect, list_rect


class HorizontalWinnerScene(AnimatedCodeScene):
  def construct(self):
    super().construct()

    # Keep for setup
    self.next_section(skip_animations=True)

    code = CodeWindow(third_scene_code, tab_width=2, start_at_line=21)
    code.scale(0.8).align_to([-7.0, 0.5, 0], UL)
    self.set_code(code)

    variables = VariableArea()
    variables.align_to([6.5, 3.9, 0], UR)

    self.set_variables(variables)
    self.add(variables)

    # Functions UL [-0.53468749  3.7         0.        ]

    # self.len_fn.next_to(self.range_fn, DOWN, buff=0.2)
    # self.functions.add(self.len_fn)
    range_fn = Function(name="range()", desc="count from\nstart to stop\nby step",
                        num_inputs=3)
    len_fn = Function('len()', 'Count items',
                         num_inputs=1)
    len_fn.next_to(range_fn, DOWN, buff=0.2)
    self.functions.add(range_fn, len_fn)
    self.functions.align_to([-0.53468749, 3.7, 0], UL)

    self.play(code.highlight_scope('def', lines=9, indents=0,
                                   line=21, start=0, end=3))

    rows = []
    for i in range(0, 6):
      temp_list = List([PLAYER_ONE_TOKEN] * 7)
      if i == 0:
        temp_list.scale(0.9)
        temp_list.align_to([2.238173, 0.9357788, 0], UL)
      else:
        temp_list.next_to(prev_list, DOWN, buff=0.4)
        temp_list.scale(0.9).align_to([7, 0, 0], RIGHT)
      for j in range(0, 7):
        # Remove the placeholder R glyph (but not the quotes) so it
        # looks like a space
        temp_list[f'index_{j}'].remove(temp_list[f'index_{j}'][1])
      temp_list.contents = [' '] * 7
      rows.append(temp_list)
      prev_list = temp_list
    self.rows = rows

    board_list = List([rows[0]] * 6).scale(0.61).align_to([2, 1.7, 0], UL)
    game_board_box = self.create_variable('game_board', board_list)
    game_board_pointer = Pointer(game_board_box['contents'].get_bottom(),
      [board_list['index_0'].get_top()[0],
       board_list.get_top()[1],
       0])
    self.add(board_list)
    variables.add([('game_board_pointer', game_board_pointer)])

    arrows = []
    for i in range(0, 6):
      start = board_list[f'index_{i}'].get_bottom()
      stop = np.array([
        rows[i]['index_0'].get_bottom()[0],
        rows[i].get_top()[1],
        0])
      new_pointer = Pointer(start, stop)
      self.bring_to_back(new_pointer)
      arrows.append(new_pointer)
    self.add(*rows)

    backgrounds = {}
    anims = []
    for r in range(0, len(partial_game)):
      for c in range(0, len(partial_game[0])):
        token = partial_game[r][c]
        token = token.replace('*', '')
        if token == ' ':
          continue
        _, copy_anims = rows[r].animate_set(c, token)
        color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
        back = rows[r].add_background_for_cell(c, color)
        backgrounds[(r, c)] = back
        anims += copy_anims
    self.play(*anims)
    self.next_section()
    self.pause()

    # Conceptual showing
    slider = SurroundingRectangle(VGroup(rows[0]['left_line'], rows[0]['div_3_4']),
                                  stroke_width=6, color=TOL_ORANGE, buff=0.05)
    self.play(Create(slider))
    self.pause()

    def move_slider_to(r, c):
      left = rows[r][f'div_{c-1}_{c}']
      right = rows[r][f'div_{c+3}_{c+4}']
      assert type(left) == Line, type(left)
      assert type(right) == Line, type(right)
      return slider.animate.move_to((left.get_center()+right.get_center()) / 2)

    for r in range(0, 4):
      for c in range(0, 4):
        if r == 0 and c == 0:
          continue
        self.play(move_slider_to(r, c),
                  run_time=0.6)
        self.wait(0.3)
        if r == 3 and c == 1:
          break

    answer = slider.copy().set_color(IBM_BLUE_60)
    self.play(Create(answer))
    self.remove(slider)

    self.wait(0.2)
    back_copy = backgrounds[(r, c)].copy()
    answer_copy = rows[r][f'index_{c}'].copy()
    result = VGroup(back_copy, answer_copy)
    result_target = result.copy().next_to(code, DOWN)
    self.add(result)
    self.play(result.animate.next_to(code, DOWN),
              surround(answer, result_target))
    self.pause()
    self.play(FadeOut(result), FadeOut(answer))
    self.pause()

    # Let's imagine a function call
    self.play(self.move_pc(21, 4, -1))
    self.pause()

    self.play(self.variables.push_variable_stack(initial_lines=2,
                                                 vars_per_row=2),
              game_board_pointer.animate.set_color(BLACK_19))
    b_var = self.create_variable('b', board_list)
    b_pointer = Pointer(b_var['contents'].get_bottom(),
      [board_list['index_0'].get_top()[0],
       board_list.get_top()[1],
       0])
    self.play(FadeIn(b_pointer), run_time=0.5)
    self.pause()
    self.remove(b_pointer)
    variables.top_scope().add_mobj('pointer', b_pointer)

    self.play(self.move_pc(22, 0, 3))
    self.play(self.highlight_scope('for', lines=7, indents=1))
    self.wait(0.5)

    self.play(self.move_pc(22, 4, 7))
    self.wait(0.2)
    row_var = self.create_variable('row', 0, show_value=False)

    len_code = code['line_22'][-8:-2]
    len_rect = SurroundingRectangle(len_code,
                                    color=SECONDARY_RECT_COLOR,
                                    buff=0.08, corner_radius=0.1)
    self.play(Create(len_rect), run_time=0.6)
    self.wait(0.2)
    temp_list = board_list.copy()
    self.add(temp_list)
    self.play(temp_list.animate.next_to(len_fn['input_1'], LEFT, buff=0.1),
              run_time=1.0)
    self.wait(0.2)
    six_len = code_value('6').set_opacity(0).move_to(len_fn['box'])
    self.play(AnimationGroup(
        temp_list.animate.scale_to_fit_width(len_fn['box'].width)
                         .move_to(len_fn['box'])
                         .set_opacity(0),
        six_len.animate.scale(1.3).set_opacity(1.0)
                       .next_to(len_fn['output_1'], RIGHT, buff=0.1),
      lag_ratio=0.50), run_time=1.5)
    self.wait(0.2)
    self.remove(temp_list)
    self.play(
        len_code.animate.set_opacity(0.1),
        six_len.animate.move_to(len_code),
    )
    self.wait(0.2)
    row_range = ForRange(loop_var=row_var,
                         range_code=code['line_22'][11:])
    row_range.expand_range(self, range_fn=range_fn,
                           start=0, start_mobj=code['line_22'][17].copy(),
                           stop=6, stop_mobj=six_len,
                           starting_tracker=len_rect,
                           wait=0.2)
    self.wait(0.2)

    done = False
    # Main loop for looking in row
    for row in range(0, 4):
      if done: break
      row_range.go_next(self)
      if row == 0:
        self.play(self.move_pc(23, 0, 3))
        self.play(self.highlight_scope('for2', lines=6, indents=2))
        self.wait(0.5)
      self.play(self.move_pc(23, 4, 7))
      self.wait(0.2)

      if row == 0:
        col_var = self.create_variable('col', 0, show_value=False, where=(1, 1))
      if row <= 1:
        # Show the column range in full detail the first two times
        # to emphasize that it gets recalculated each loop.
        len_code2 = code['line_23'][20:31]
        len_rect2 = SurroundingRectangle(len_code2,
                                         color=SECONDARY_RECT_COLOR,
                                         buff=0.08, corner_radius=0.1)
        self.play(Create(len_rect2))
        self.wait(0.2)
        code_rect = SurroundingRectangle(code['line_23'][24],
                                         color=IBM_PURPLE_60,
                                         buff=0.03, corner_radius=0.1)
        list_rect = SurroundingRectangle(board_list,
                                         color=IBM_PURPLE_60,
                                         stroke_width=5,
                                         buff=0.08, corner_radius=0.1)
        self.play(Create(code_rect), Create(list_rect),
                  traverse(b_pointer))
        self.wait(0.8 if row == 0 else 0.2)
        self.play(
            surround(code_rect, code['line_23'][24:30]),
            surround(list_rect, VGroup(board_list[f'div_{row-1}_{row}'],
                                       board_list[f'div_{row}_{row+1}'])),
            Indicate(row_var['name'], color=IBM_PURPLE_60, scale_factor=1.2,
                     rate_func=there_and_back_with_pause),
            Indicate(row_var['contents'], color=IBM_PURPLE_60, scale_factor=1.3,
                     rate_func=there_and_back_with_pause),
        )
        self.wait(0.1)
        self.play(traverse(arrows[row]),
                  surround(list_rect, rows[row])
        )
        self.wait(0.5 if row == 0 else 0.2)
        list_copy = rows[row].copy()
        self.add(list_copy)
        self.play(
          list_copy.animate.next_to(len_fn['input_1'], LEFT, buff=0.1),
          list_rect.animate.set_opacity(0).move_to(len_fn['input_1'].get_left() + [-list_copy.width / 2, 0, 0]),
          FadeOut(code_rect)
        )
        self.remove(list_rect)
        self.wait(0.5 if row == 0 else 0.2)

        seven_len = code_value('7').set_opacity(0).move_to(len_fn['box'])
        self.play(AnimationGroup(
            list_copy.animate.scale_to_fit_width(len_fn['box'].width)
                             .move_to(len_fn['box'])
                             .set_opacity(0),
            seven_len.animate.scale(1.3).set_opacity(1.0)
                             .next_to(len_fn['output_1'], RIGHT, buff=0.1),
          lag_ratio=0.50), run_time=1.5)
        self.wait(0.2)
        self.remove(list_copy)
        self.play(
            len_code2.animate.set_opacity(0.1),
            seven_len.animate.move_to(len_code2),
        )
        self.wait(0.2)
        minus_three_code = code['line_23'][32:35]
        self.play(
            surround(len_rect2, VGroup(seven_len, minus_three_code)),
        )
        self.wait(0.5 if row == 0 else 0.2)
        self.play(
            Transform(seven_len, code_value('4').scale(1.3).move_to(VGroup(seven_len, minus_three_code))),
            minus_three_code.animate.set_opacity(0.1),
        )
        self.wait(0.5 if row == 0 else 0.2)
        col_range = ForRange(loop_var=col_var, range_code=code['line_23'][11:])
        col_range.expand_range(self, range_fn=range_fn,
                           start=0, start_mobj=code['line_23'][17].copy(),
                           stop=4, stop_mobj=seven_len,
                           starting_tracker=len_rect2,
                           wait=0.2)
        self.pause()
      else:
        col_range = ForRange(loop_var=col_var, range_code=code['line_23'][11:])
        col_range.show_range(self, 0, 4, 1)
        self.wait(0.4)

      # Start col loop
      for col in range(0, 4):
        col_range.go_next(self)
        self.play(self.move_pc(24, 0, 2))
        if row == 0 and col == 0:
          self.play(self.highlight_scope('if', lines=1, indents=3))
          self.wait(0.5)
        else:
          self.wait(0.2)
        self.play(self.move_pc(24, 3, -1))
        self.wait(0.2)
        line_24_list_code = code['line_24'][3:14]
        line_24_list_item = self.get_from_board(row, col,
                                                row_code=code['line_24'][3:9],
                                                col_code=line_24_list_code)
        condition = partial_game[row][col] == ' '
        self.wait(0.5 if ((row == 0 and col <= 1) or condition) else 0.2)
        condition_mobj = Condition(code['line_24'][3:-1], state=condition).set_opacity(0)
        self.add(condition_mobj)
        self.play(condition_mobj.animate.set_opacity(0.95))
        if condition:
          self.wait(0.5 if row == 0 and col <= 1 else 0.2)
          self.play(self.move_pc(25, 0, None),
                    condition_mobj.animate.set_opacity(0),
                    FadeOut(line_24_list_item),
                    line_24_list_code.animate.set_opacity(1.0),
                    )
          self.remove(condition_mobj)
          self.wait(1.0 if row == 0 and col == 0 else 0.5)
          if row == 0 and col == 0:
            # "Because the string at row 0, column 0 is a space, we know it is *not* the start
            # of a 4 in a row and can just go to the next item over to check there."
            # If this doesn't jive with the actual commntary, I should be able to cut it out.
            orange_rect = SurroundingRectangle(VGroup(rows[0]['left_line'], rows[0]['div_0_1']),
                                               stroke_width=6, color=TOL_ORANGE, buff=0.05)
            self.play(Create(orange_rect), run_time=0.8)
            self.wait(0.5)
            self.play(surround(orange_rect, VGroup(rows[0]['left_line'], rows[0]['div_3_4'])),
                      run_time=0.7)
            self.wait(0.3)
            self.play(orange_rect.animate.set_opacity(0))
            self.wait(0.2)
            self.play(self.move_pc(23, 4, 7))
          else:
            self.play(self.move_pc(23, 4, 7))
          self.wait(0.1)
          continue
        # not condition
        self.wait(0.5)
        first_time = 'scope_26' not in code
        self.pc_end_scope(25, scope_type='if', indents=3,
                          with_anims=[condition_mobj.animate.set_opacity(0.0),
                                      FadeOut(line_24_list_item),
                                      line_24_list_code.animate.set_opacity(1.0)])
        self.remove(condition_mobj)
        self.wait(0.5)
        self.play(self.move_pc(26, 0, 2))
        self.wait(0.2)
        entire_condition = VGroup(code['line_26'][3:],
                                  code['line_27'],
                                  code['line_28'])
        if first_time:
          # "This if statement has a three part condition, spread across
          #  three lines due to these parenthases.
          left_paren = code['line_26'][3]
          right_paren = code['line_28'][-2]
          three_lines = code.lines(26, 28).height
          self.play(left_paren.animate.scale_to_fit_height(three_lines)
                                      .align_to(code['line_26'].get_top(), UP)
                                      .shift(LEFT * 0.02)
                                      .set_color(IBM_RED_60),
                    right_paren.animate.scale_to_fit_height(three_lines)
                                       .align_to(code['line_26'].get_top(), UP)
                                       .align_to(code['line_26'].get_right(), LEFT)
                                       .shift(RIGHT * 0.02)
                                       .set_color(IBM_RED_60),
                    run_time=2.0, rate_func=there_and_back_with_pause)
          self.wait(0.2)

          # Line 29 is the only line of code inside the if statement and it
          # will run...
          self.play(code.highlight_scope('if', lines=1, indents=3,
                                         line=26, start=0, end=2,
                                         body_lines_offset=3))
          self.wait(0.5)

          # "when this entire condition is true.""
          self.play(surround(self.pc, entire_condition))
          self.wait(0.5)
        # end first_time

        conditions = [
          None,
          {
            'pc': (26, 4, -4),
            'row_1_code': code['line_26'][6:9],
            'col_1_code': code['line_26'][11:14],
            'left_code': code['line_26'][4:15],
            'row_2_code': code['line_26'][21:24],
            'col_2_code': code['line_26'][26:29],
            'col_2_plus_code': code['line_26'][26:33],
            'right_code': code['line_26'][19:34],
            'and_pc': (26, -3, None),
          },
          {
            'pc': (27, 0, -4),
            'row_1_code': code['line_27'][2:5],
            'col_1_code': code['line_27'][7:10],
            'left_code': code['line_27'][:11],
            'row_2_code': code['line_27'][17:20],
            'col_2_code': code['line_27'][22:25],
            'col_2_plus_code': code['line_27'][22:29],
            'right_code': code['line_27'][15:30],
            'and_pc': (27, -3, None),
          },
          {
            'pc': (28, 0, -2),
            'row_1_code': code['line_28'][2:5],
            'col_1_code': code['line_28'][7:10],
            'left_code': code['line_28'][:11],
            'row_2_code': code['line_28'][17:20],
            'col_2_code': code['line_28'][22:25],
            'col_2_plus_code': code['line_28'][22:29],
            'right_code': code['line_28'][15:30],
          }
        ]
        condition_mobjs = []
        was_true = True
        for offset in range(1, 4, 1):
          con = conditions[offset]
          pc = con['pc']
          self.play(self.move_pc(pc[0], pc[1], pc[2]))
          self.wait(0.2)

          # bring in col variable, add 1
          row_1 = row_var['contents'].copy()
          row_2 = row_var['contents'].copy()
          col_1 = col_var['contents'].copy()
          col_2 = col_var['contents'].copy()
          row_1_code = con['row_1_code']
          col_1_code = con['col_1_code']
          row_2_code = con['row_2_code']
          col_2_code = con['col_2_code']
          col_2_plus_code = con['col_2_plus_code']

          self.play(
            row_1.animate.scale(1.3).move_to(row_1_code).align_to(row_1_code, DOWN),
            row_1_code.animate.set_opacity(0.1),
            row_2.animate.scale(1.3).move_to(row_2_code).align_to(row_2_code, DOWN),
            row_2_code.animate.set_opacity(0.1),
            col_1.animate.scale(1.3).move_to(col_1_code).align_to(col_1_code, DOWN),
            col_1_code.animate.set_opacity(0.1),
            col_2.animate.scale(1.3).move_to(col_2_code).align_to(col_2_code, DOWN),
            col_2_code.animate.set_opacity(0.1),
          )
          self.wait(0.2)

          col_2_plus_off = code_value(str(col_var.value + offset)).scale(1.3)
          col_2_plus_off.move_to(col_2_plus_code).align_to(col_2_plus_code, DOWN)
          self.play(
            Transform(col_2, col_2_plus_off),
            col_2_plus_code.animate.set_opacity(0.1),
          )
          self.wait(0.3)
          # highlight both cells and copy values in for comparison
          rects = self.highlight_two(first=(row, col),
                                     first_code=con['left_code'],
                                     second=(row, col + offset),
                                     second_code=con['right_code'])
          self.wait(1.0 if row == 2 else 0.5)
          condition = (partial_game[row][col].replace('*', '') ==
                       partial_game[row][col + offset].replace('*', ''))
          condition_mobj = Condition(code[f'line_{pc[0]}'][pc[1]:pc[2]], state=condition).set_opacity(0)
          self.add(condition_mobj)
          self.play(
              *[FadeOut(mobj) for mobj in [rects[0], rects[2], row_1, row_2, col_1, col_2]],
              *[mobj.animate.set_opacity(1.0) for mobj in [row_1_code, row_2_code, col_1_code, col_2_code, col_2_plus_code]],
              condition_mobj.animate.set_opacity(0.95))
          self.wait(0.1)
          condition_mobjs.append(condition_mobj)
          self.play(FadeOut(rects[1]), FadeOut(rects[3]), run_time=0.6)
          self.wait(0.2)
          if not condition:
            was_true = False
            break
          # go to and
          and_pc = con.get('and_pc', None)
          if and_pc is None:
            break
          self.play(self.move_pc(and_pc[0], and_pc[1], and_pc[2]))
          self.wait(0.2)
        # end of conditions loop

        self.play(surround(self.pc, entire_condition))
        self.wait(0.2)
        # Highlight both ANDS
        and_color = IBM_BLUE_60 if was_true else IBM_RED_60
        self.play(Indicate(code['line_26'][-3:], color=and_color, scale_factor=1.4),
                  Indicate(code['line_27'][-3:], color=and_color, scale_factor=1.4),
        )
        self.wait(0.2)
        multi_and = Condition(entire_condition, state=was_true).set_opacity(0)
        self.add(multi_and)
        self.play(
            multi_and.animate.set_opacity(0.93),
            *[FadeOut(con) for con in condition_mobjs],
        )
        self.wait(0.5)
        if row == 2 and col == 2:
          # "Now because python sees there are multiple ANDs" in this condition
          # and one of them is False, it stops evaulating the other conditions
          # because it knows the whole condition will now be False. Skipping
          # the rest of the conditions is called "short-circuit evaluation"
          # <put on screen> and lets the computer do less work.
          sce_text = Text("short-\ncircuit\nevaluation", font=ROBOTO_MONO, font_size=18, color=BLACK)
          sce_text.scale_to_fit_width((rows[0].get_left()[0] - code.get_right()[0]) - 0.12)
          sce_text.next_to(self.pc, RIGHT, buff=0.1)
          self.play(FadeIn(sce_text))
          self.pause()
          self.play(FadeOut(sce_text))
          self.wait(0.1)

        if was_true:
          self.play(self.move_pc(29, 0, None), multi_and.animate.set_opacity(0))
          self.pause()
          return_mobj = self.get_from_board(row, col,
                                            row_code=code['line_29'][7:13],
                                            col_code=code['line_29'][7:18],
          )
          self.wait(0.5)
          done = True
          back_copy = backgrounds[(row, col)].copy()
          back_copy.move_to(return_mobj)
          self.remove(return_mobj)
          result = VGroup(back_copy, return_mobj)
          self.add(result)
          break

        self.pc_end_scope(29, 'if', indents=3,
                          with_anims=[multi_and.animate.set_opacity(0)])
        self.remove(multi_and)
        self.wait(0.2)
        self.play(self.move_pc(23, 4, 7))
      if done: break
      # end of col loop
      col_range.finish(self, skip_highlight=True)
      self.pc_end_scope(29, scope_type='for', indents=2)
      self.wait(0.5 if row == 0 else 0.2)
      self.play(self.move_pc(22, 4, 7))
    # end of for loop

    self.next_section()
    result_target = result.copy().next_to(code, DOWN)
    self.play(result.animate.next_to(code, DOWN),
              code['line_29'][7:18].animate.set_opacity(1.0),
              *col_range.break_anims(),
              *row_range.break_anims(),
              surround(self.pc, result_target),
    )
    self.wait(0.1)
    variables.pop_variable_stack(self, pop_anims=[
        FadeOut(self.pc),
        game_board_pointer.animate.set_color(BLACK),
    ])
    self.pause()
    self.play(FadeOut(result))
    self.pause()

    # I want to briefly come back to why this minus 3 is important.
    minus_three_code = code['line_23'][32:35]
    minus_three_box = SurroundingRectangle(minus_three_code, corner_radius=0.1,
                                           stroke_width=4, color=TOL_ORANGE, buff=0.08)
    self.play(Create(minus_three_box))
    self.wait(0.5)
    # Suppose it did not exist, what would break? Pause the video
    # and identify where the code might crash.
    self.play(minus_three_code.animate.set_opacity(0))
    self.pause()

    # Conceptually, the inner loop slides a window of 4 horizontal cells across
    # the board and asks if they are all the same. Without the minus three,
    # this sliding window would go off the board and Python could crash trying
    # to access items passed the end of the list.
    slider = SurroundingRectangle(VGroup(rows[0]['left_line'], rows[0]['div_3_4']),
                                  stroke_width=6, color=TOL_ORANGE, buff=0.05)
    self.play(Create(slider))
    self.pause()
    r = 0
    for c in range(1, 4):
        prev_slider_loc = slider.get_center()
        self.play(move_slider_to(r, c),
                  run_time=0.6)
        self.wait(0.3)

    underlines = [
      Underline(code['line_28'][21:30], color=IBM_RED_60, buff=0.01),
      Underline(code['line_27'][21:30], color=IBM_RED_60, buff=0.01),
      Underline(code['line_26'][25:34], color=IBM_RED_60, buff=0.01),
    ]
    delta = (slider.get_center() - prev_slider_loc)[0]
    for i in range(0, 3):
      self.play(slider.animate.shift(RIGHT * delta), run_time=0.6)
      self.play(Create(underlines[i]), run_time=0.6)
      self.wait(0.1)
    self.pause()
    # Because we are looking up to three columns ahead of the col loop variable,
    # we should stop the loop three columns early to avoid this, thus the
    # minus three in the range.
    plus_three_code = code['line_28'][26:29]
    plus_three_box = SurroundingRectangle(plus_three_code, corner_radius=0.1,
                                          stroke_width=4, color=TOL_ORANGE, buff=0.08)
    self.play(Create(plus_three_box))
    self.wait(0.5)
    self.play(Indicate(minus_three_box, color=TOL_ORANGE),
              minus_three_code.animate.set_opacity(1.0),
    )
    self.wait(0.1)
    self.play(
      slider.animate.shift(LEFT * 3 * delta),
      *[FadeOut(und) for und in underlines],
    )
    self.pause()
    self.play(FadeOut(minus_three_box), FadeOut(plus_three_box), FadeOut(slider))

    self.pause()
    self.play(*[scope.animate.set_opacity(0) for scope in code.scopes])

    self.wait(2.0)

  def get_from_board(self, row: int, col: int, row_code: Mobject = None,
                     col_code: Mobject = None):
    code_rect = SurroundingRectangle(row_code,
                                     color=IBM_PURPLE_60,
                                     buff=0.03, corner_radius=0.1)
    list_rect = SurroundingRectangle(self.rows[row],
                                     color=IBM_PURPLE_60,
                                     stroke_width=5,
                                     buff=0.08, corner_radius=0.1)
    row_var = self.get_variable('row')
    col_var = self.get_variable('col')
    self.play(
      Create(code_rect),
      Create(list_rect),
      Indicate(row_var['name'], color=IBM_PURPLE_60, scale_factor=1.2,
               rate_func=there_and_back_with_pause),
      Indicate(row_var['contents'], color=IBM_PURPLE_60, scale_factor=1.4,
               rate_func=there_and_back_with_pause),
      run_time=0.8,
    )
    self.wait(0.2)

    self.play(
        surround(code_rect, col_code),
        surround(list_rect,
                 VGroup(self.rows[row][f'div_{col-1}_{col}'],
                        self.rows[row][f'div_{col}_{col+1}'])),
        Indicate(col_var['name'], color=IBM_PURPLE_60, scale_factor=1.2,
                  rate_func=there_and_back_with_pause),
        Indicate(col_var['contents'], color=IBM_PURPLE_60, scale_factor=1.4,
                  rate_func=there_and_back_with_pause),
        run_time=0.8,
    )
    self.wait(0.2)

    list_item = self.rows[row][f'index_{col}'].copy()
    self.play(
        col_code.animate.set_opacity(0.07),
        list_item.animate.scale(1.3).move_to(col_code)
                                    .align_to(col_code, UP),
        list_rect.animate.set_opacity(0).move_to(col_code),
        FadeOut(code_rect, run_time=1.0),
        run_time=0.8,
    )
    self.remove(code_rect)
    return list_item

  def highlight_two(self, first, first_code, second, second_code):
    row, col = first
    rects = [
        SurroundingRectangle(first_code,
                             color=IBM_PURPLE_60,
                             buff=0.03, corner_radius=0.1),
        SurroundingRectangle(VGroup(self.rows[row][f'div_{col-1}_{col}'],
                                    self.rows[row][f'div_{col}_{col+1}']),
                             color=IBM_PURPLE_60,
                             stroke_width=5,
                             buff=0.04, corner_radius=0.1),
    ]
    row, col = second
    rects += [
        SurroundingRectangle(second_code,
                             color=IBM_PURPLE_60,
                             buff=0.03, corner_radius=0.1),
        SurroundingRectangle(VGroup(self.rows[row][f'div_{col-1}_{col}'],
                                    self.rows[row][f'div_{col}_{col+1}']),
                             color=IBM_PURPLE_60,
                             buff=0.04, corner_radius=0.1),
    ]
    self.play(Create(rects[0]), Create(rects[1]), run_time=0.8)
    self.wait(0.2)
    self.play(Create(rects[2]), Create(rects[3]), run_time=0.8)
    return rects


class OtherDirectionScene(AnimatedCodeScene):
  def construct(self):
    super().construct()

    self.next_section(skip_animations=True)

    h_code = CodeWindow(third_scene_code, tab_width=2, start_at_line=21)
    h_code.scale(0.8).align_to([-7.0, 0.5, 0], UL)
    self.add(h_code)

    variables = VariableArea()
    variables.align_to([6.5, 3.9, 0], UR)

    self.set_variables(variables)
    self.add(variables)

    # Functions UL [-0.53468749  3.7         0.        ]

    # self.len_fn.next_to(self.range_fn, DOWN, buff=0.2)
    # self.functions.add(self.len_fn)
    range_fn = Function(name="range()", desc="count from\nstart to stop\nby step",
                        num_inputs=3)
    len_fn = Function('len()', 'Count items',
                      num_inputs=1)
    len_fn.next_to(range_fn, DOWN, buff=0.2)
    self.functions.add(range_fn, len_fn)
    self.functions.align_to([-0.53468749, 3.7, 0], UL)

    rows = []
    for i in range(0, 6):
      temp_list = List([PLAYER_ONE_TOKEN] * 7)
      if i == 0:
        temp_list.scale(0.9)
        temp_list.align_to([2.238173, 0.9357788, 0], UL)
      else:
        temp_list.next_to(prev_list, DOWN, buff=0.4)
        temp_list.scale(0.9).align_to([7, 0, 0], RIGHT)
      for j in range(0, 7):
        # Remove the placeholder R glyph (but not the quotes) so it
        # looks like a space
        temp_list[f'index_{j}'].remove(temp_list[f'index_{j}'][1])
      temp_list.contents = [' '] * 7
      rows.append(temp_list)
      prev_list = temp_list
    self.rows = rows

    board_list = List([rows[0]] * 6).scale(0.61).align_to([2, 1.7, 0], UL)
    game_board_box = self.create_variable('game_board', board_list)
    game_board_pointer = Pointer(game_board_box['contents'].get_bottom(),
      [board_list['index_0'].get_top()[0],
       board_list.get_top()[1],
       0])
    self.add(board_list)
    variables.add([('game_board_pointer', game_board_pointer)])

    arrows = []
    for i in range(0, 6):
      start = board_list[f'index_{i}'].get_bottom()
      stop = np.array([
        rows[i]['index_0'].get_bottom()[0],
        rows[i].get_top()[1],
        0])
      new_pointer = Pointer(start, stop)
      self.bring_to_back(new_pointer)
      arrows.append(new_pointer)
    self.add(*rows)

    backgrounds = {}
    anims = []
    for r in range(0, len(partial_game)):
      for c in range(0, len(partial_game[0])):
        token = partial_game[r][c]
        token = token.replace('*', '')
        if token == ' ':
          continue
        _, copy_anims = rows[r].animate_set(c, token)
        color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
        back = rows[r].add_background_for_cell(c, color)
        backgrounds[(r, c)] = back
        anims += copy_anims
    self.play(*anims)
    self.next_section()
    self.pause()

    v_code = CodeWindow(vertical_dir_code, tab_width=2, start_at_line=31)
    v_code.scale(0.8).align_to(h_code.get_corner(DL) + [0.0, -0.105, 0], UL)
    v_code['line_31'].set_opacity(0)
    self.play(FadeIn(v_code))
    delta = 0.5 - v_code.get_top()[1]
    self.play(v_code.animate.align_to([-7.0, 0.5, 0], UL),
              h_code.animate.shift(UP * delta),
              self.functions.animate.shift(UP * delta)
    )
    self.pause()

    # Conceptual showing
    slider = SurroundingRectangle(VGroup(rows[0]['left_line'], rows[3]['div_0_1']),
                                  stroke_width=6, color=TOL_ORANGE, buff=0.05)
    self.play(Create(slider))
    self.pause()

    def move_v_slider_to(r, c):
      left = rows[r][f'div_{c-1}_{c}']
      right = rows[r+3][f'div_{c}_{c+1}']
      assert type(left) == Line, type(left)
      assert type(right) == Line, type(right)
      return slider.animate.move_to((left.get_center()+right.get_center()) / 2)

    for r in range(0, 3):
      for c in range(0, 7):
        if r == 0 and c == 0:
          continue
        self.play(move_v_slider_to(r, c),
                  run_time=0.6 if r != 1 else 0.5)
        self.wait(0.2)
        if r == 2 and c == 2:
          break

    # Highlight differences in code
    horiz_boxes = SurroundingRectangle(VGroup(h_code['line_26'][26:33],
                                              h_code['line_27'][22:29],
                                              h_code['line_28'][22:29]),
                                       color=IBM_PURPLE_60,
                                       buff=0.08, corner_radius=0.1)
    vert_boxes = SurroundingRectangle(VGroup(v_code['line_37'][21:28],
                                             v_code['line_38'][17:24],
                                             v_code['line_39'][17:24]),
                                      color=IBM_PURPLE_60,
                                      buff=0.08, corner_radius=0.1)
    self.play(Create(horiz_boxes))
    self.play(Create(vert_boxes))
    self.pause()
    h_minus_three_box = SurroundingRectangle(h_code['line_23'][-5:-2],
                                             color=TOL_ORANGE,
                                             buff=0.08, corner_radius=0.1)
    v_minus_three_box = SurroundingRectangle(v_code['line_33'][-5:-2],
                                             color=TOL_ORANGE,
                                             buff=0.08, corner_radius=0.1)
    self.play(Create(h_minus_three_box), run_time=0.7)
    self.play(Indicate(h_code['line_23'][4:7], scale_factor=1.4, color=TOL_ORANGE), rate_func=there_and_back_with_pause)
    self.play(Create(v_minus_three_box), run_time=0.7)
    self.play(Indicate(v_code['line_33'][4:7], scale_factor=1.4, color=TOL_ORANGE), rate_func=there_and_back_with_pause)
    self.pause()
    cleanup_anims = [FadeOut(horiz_boxes), FadeOut(vert_boxes),
                     FadeOut(h_minus_three_box), FadeOut(v_minus_three_box)]
    # Then go through the end
    for c in range(3, 7):
      self.play(move_v_slider_to(r, c),
                *cleanup_anims,
                run_time=0.6)
      cleanup_anims = []
      self.wait(0.2 if c < 6 else 0.5)

    self.play(surround(slider, v_code['line_41']), )
    self.wait(0.5)

    return_mobj = v_code['line_41'][-3:].copy()
    return_target = Text('"|"', font_size=18, font=ROBOTO_MONO)
    return_target.scale(1.6).next_to(v_code, DOWN)
    self.add(return_mobj)
    self.play(surround(slider, return_target),
              return_mobj.animate.scale(1.5).set_color(BLACK).next_to(v_code, DOWN))
    self.pause()
    self.play(FadeOut(slider), FadeOut(return_mobj))
    self.pause()

    # Now for diagonal code
    d1_code = CodeWindow(diag_1_code, tab_width=2, start_at_line=42)
    d1_code.scale(0.8).align_to(v_code.get_corner(DL) + [0.0, -0.105, 0], UL)
    d1_code['line_42'].set_opacity(0)
    self.play(FadeIn(d1_code))
    delta = 0.5 - d1_code.get_top()[1]

    self.play(d1_code.animate.align_to([-7.0, 0.5, 0], UL),
              v_code.animate.shift(UP * delta),
              h_code.animate.shift(UP * delta),
              self.functions.animate.shift(UP * delta),
              # Set up hits for diagonals too
              backgrounds[(2, 3)].animate.set_color(PLAYER_TWO_COLOR),
              become_in_place(rows[2]['index_3'], rows[3]['index_3']),
              backgrounds[(3, 3)].animate.set_color(PLAYER_ONE_COLOR),
              become_in_place(rows[3]['index_3'], rows[2]['index_3']),

    )
    self.remove(self.functions, h_code)
    self.pause()

    triangle = (rows[3]['index_3'].get_center() - rows[0]['index_0'].get_center())
    hypot = ((triangle[0] ** 2 + triangle[1] ** 2) ** 0.5) + 0.4
    angle = math.atan(triangle[1] / triangle[0])  # radians
    slider = Rectangle(height=rows[0].height + 0.1, width=hypot,
                       stroke_width=6, color=TOL_ORANGE)
    slider.rotate(angle, about_point=slider.get_corner(DL))
    slider.move_to((rows[0]['index_0'].get_center()+rows[3]['index_3'].get_center()) / 2)
    self.play(Create(slider), run_time=1.4)
    self.pause()

    def move_d1_slider_to(r, c):
      left = rows[r][f'index_{c}']
      right = rows[r+3][f'index_{c+3}']
      return slider.animate.move_to((left.get_center()+right.get_center()) / 2)

    for r in range(0, 3):
      for c in range(0, 4):
        if r == 0 and c == 0:
          continue
        self.play(move_d1_slider_to(r, c),
                  run_time=0.6)
        self.wait(0.3)
        if r == 2 and c == 2:
          break

    vert_boxes = SurroundingRectangle(VGroup(v_code['line_37'][21:28],
                                             v_code['line_38'][17:24],
                                             v_code['line_39'][17:24]),
                                      color=IBM_PURPLE_60,
                                      buff=0.08, corner_radius=0.1)
    d1_h_box = SurroundingRectangle(VGroup(d1_code['line_48'][21:28],
                                           d1_code['line_49'][17:24],
                                           d1_code['line_50'][17:24]),
                                      color=IBM_PURPLE_60,
                                      buff=0.08, corner_radius=0.1)
    d1_v_box = SurroundingRectangle(VGroup(d1_code['line_48'][30:37],
                                           d1_code['line_49'][26:33],
                                           d1_code['line_50'][26:33]),
                                    color=IBM_PURPLE_60,
                                    buff=0.08, corner_radius=0.1)
    self.play(Create(vert_boxes))
    self.play(Create(d1_h_box), Create(d1_v_box))
    self.pause()
    v_minus_three_box = SurroundingRectangle(v_code['line_33'][-5:-2],
                                             color=TOL_ORANGE,
                                             buff=0.08, corner_radius=0.1)
    d1_r_minus_three_box = SurroundingRectangle(d1_code['line_44'][-5:-2],
                                                color=TOL_ORANGE,
                                                buff=0.08, corner_radius=0.1)
    d1_c_minus_three_box = SurroundingRectangle(d1_code['line_45'][-5:-2],
                                                color=TOL_ORANGE,
                                                buff=0.08, corner_radius=0.1)
    self.play(Create(v_minus_three_box),
              Indicate(v_code['line_33'][4:7], scale_factor=1.4, color=TOL_ORANGE))
    self.wait(0.1)
    self.play(Create(d1_r_minus_three_box), Create(d1_c_minus_three_box),
              Indicate(d1_code['line_44'][4:7], scale_factor=1.4, color=TOL_ORANGE),
              Indicate(d1_code['line_45'][4:7], scale_factor=1.4, color=TOL_ORANGE))
    self.pause()

    self.play(FadeOut(slider), FadeOut(vert_boxes), FadeOut(d1_h_box), FadeOut(d1_v_box),
              FadeOut(v_minus_three_box), FadeOut(d1_r_minus_three_box), FadeOut(d1_c_minus_three_box))
    self.wait(0.2)

    # Second diagonal code
    d2_code = CodeWindow(diag_2_code, tab_width=2, start_at_line=53)
    d2_code.scale(0.8).align_to(d1_code.get_corner(DL) + [0.0, -0.105, 0], UL)
    d2_code['line_53'].set_opacity(0)
    self.play(FadeIn(d2_code))
    delta = 0.5 - d2_code.get_top()[1]

    self.play(d2_code.animate.align_to([-7.0, 0.5, 0], UL),
              d1_code.animate.shift(UP * delta),
              v_code.animate.shift(UP * delta),
    )
    self.remove(v_code)
    self.pause()
    # explain down and to the left
    triangle = (rows[0]['index_3'].get_center() - rows[3]['index_0'].get_center())
    hypot = ((triangle[0] ** 2 + triangle[1] ** 2) ** 0.5) + 0.4
    angle = math.atan(triangle[1] / triangle[0])  # radians
    slider = Rectangle(height=rows[0].height + 0.1, width=hypot,
                       stroke_width=6, color=TOL_ORANGE)
    slider.rotate(angle, about_point=slider.get_corner(DL))
    slider.move_to((rows[3]['index_0'].get_center()+rows[0]['index_3'].get_center()) / 2)
    self.play(Create(slider), run_time=1.4)
    self.pause()

    # The "down" part is the same, in that we look for increasing rows and
    # stop three rows before the bottom.
    d1_h_box = SurroundingRectangle(VGroup(d1_code['line_48'][21:28],
                                           d1_code['line_49'][17:24],
                                           d1_code['line_50'][17:24]),
                                    color=IBM_PURPLE_60,
                                    buff=0.08, corner_radius=0.1)

    d2_h_box = SurroundingRectangle(VGroup(d2_code['line_59'][21:28],
                                           d2_code['line_60'][17:24],
                                           d2_code['line_61'][17:24]),
                                    color=IBM_PURPLE_60,
                                    buff=0.08, corner_radius=0.1)
    d1_r_minus_three_box = SurroundingRectangle(d1_code['line_44'][-5:-2],
                                                color=TOL_ORANGE,
                                                buff=0.08, corner_radius=0.1)
    d2_r_minus_three_box = SurroundingRectangle(d2_code['line_55'][-5:-2],
                                                color=TOL_ORANGE,
                                                buff=0.08, corner_radius=0.1)

    self.play(Create(d1_h_box), Create(d2_h_box))
    self.wait(0.1)
    self.play(Create(d1_r_minus_three_box), Create(d2_r_minus_three_box),
              Indicate(d1_code['line_44'][4:7], scale_factor=1.4, color=TOL_ORANGE),
              Indicate(d2_code['line_55'][4:7], scale_factor=1.4, color=TOL_ORANGE))
    self.pause()

    # But to go left, we look at decreasing column values, using subtraction instead of
    # addition.
    d2_v_box = SurroundingRectangle(VGroup(d2_code['line_59'][30:37],
                                           d2_code['line_60'][26:33],
                                           d2_code['line_61'][26:33]),
                                    color=IBM_PURPLE_60,
                                    buff=0.08, corner_radius=0.1)
    self.play(Create(d2_v_box))
    self.play(Indicate(d2_code['line_59'][-8], scale_factor=2.5, color=IBM_RED_60),
              Indicate(d2_code['line_60'][-8], scale_factor=2.5, color=IBM_RED_60),
              Indicate(d2_code['line_61'][-6], scale_factor=2.5, color=IBM_RED_60),
              rate_func=there_and_back_with_pause,
    )
    self.wait(0.5)
    # Notice also how we start the inner loop at column index 3 and go all the way to
    # last column. Because we are moving down and to the left, we need to start our
    # search shifted right or we will try to access items using negative indices.
    d2_range_start_box = SurroundingRectangle(d2_code['line_56'][17],
                                              color=TOL_ORANGE,
                                              buff=0.08, corner_radius=0.1)
    self.play(Indicate(d2_code['line_56'][4:7], scale_factor=1.4, color=TOL_ORANGE),
              rate_func=there_and_back_with_pause)
    self.play(Create(d2_range_start_box))
    self.wait(0.5)

    def move_d2_slider_to(r, c):
      left = rows[r+3][f'index_{c-3}']
      right = rows[r][f'index_{c}']
      return slider.animate.move_to((left.get_center()+right.get_center()) / 2)

    for r in range(0, 3):
      for c in range(3, 7):
        if r == 0 and c == 3:
          continue
        self.play(move_d2_slider_to(r, c),
                  run_time=0.6)
        self.wait(0.5 if c == 6 else 0.3)
        if r == 2 and c == 3:
          break

    self.play(*[FadeOut(x) for x in [d1_h_box, d2_h_box, d2_v_box, d1_r_minus_three_box,
                                     d2_r_minus_three_box, d2_range_start_box, slider]])
    self.pause()

    delta = self.camera.frame.get_top()[1] + 0.1 - d2_code.get_bottom()[1]
    self.play(d1_code.animate.shift(UP * delta),
              d2_code.animate.shift(UP * delta),
              run_time=1.5)

    self.wait(2)


def traverse(arrow: Pointer) -> Animation:
  """Briefly change the color of the arrow to indicate following it."""
  return Indicate(arrow, color=IBM_PURPLE_60, scale_factor=1.0,
                  rate_func=there_and_back_with_pause)


from manim_ace.colors import IBM_MAGENTA_20

class ConnectFourIntro(AnimatedCodeScene):
  def construct(self):
    super().construct()
    self.camera.background_color = WHITE

    def TT(s, font=ROBOTO_MONO):
        return Text(s, color=BLACK, font_size=18, font=font).scale(1.7)

    title = TT('Python Connect Four', font=LM_MONO).scale(1.5).move_to([0, 3, 0])

    body = Rectangle(width=7, height=6)
    holes = []
    for r in range(0, 6):
      for c in range(0, 7):
        hole = Circle(radius=0.4).move_to(body.get_corner(UL) + [0.5, -0.5, 0] +
                                          [c, -r, 0])
        holes.append(hole)

    board_scale = 0.8
    board = Cutout(body, *holes,
                   stroke_width=4, fill_color=IBM_MAGENTA_20, fill_opacity=1.0,
                   stroke_color=BLACK)
    board.scale(board_scale).move_to([0, -0.25, 0])

    goal_txt = TT('Goal: Get 4 tokens in a row')
    goal_txt.next_to(board, DOWN, buff=0.5)

    self.add(title, goal_txt)
    self.add(board, layer=1)
    self.pause()
    to_fade_out = [goal_txt, board]

    def board_loc(row: int, col: int):
      offset = np.array([0.5, -0.5, 0]) * board_scale
      offset +=  np.array([col, -row, 0]) * board_scale
      return board.get_corner(UL) + offset

    def make_piece(token: str, column: int) -> VGroup:
      radius = 0.4 * board_scale
      color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
      circle = Circle(radius=radius, fill_color=color,
                      fill_opacity=1.0,
                      stroke_color=BLACK, stroke_width=2)
      txt = TT(token).move_to(circle)
      return VGroup(circle, txt).move_to(board_loc(-1, column))

    anims = [
      (PLAYER_ONE_TOKEN, 5, 5),
      (PLAYER_TWO_TOKEN, 3, 5),
      (PLAYER_ONE_TOKEN, 5, 4),
      (PLAYER_TWO_TOKEN, 2, 5),
      (PLAYER_ONE_TOKEN, 5, 3),
      (PLAYER_TWO_TOKEN, 5, 2),
      (PLAYER_ONE_TOKEN, 2, 4),
      (PLAYER_TWO_TOKEN, 1, 5),
      (PLAYER_ONE_TOKEN, 4, 5),
      (PLAYER_TWO_TOKEN, 0, 5),
    ]
    pieces = []
    for (player, col, row) in anims:
      piece = make_piece(player, col)
      anim = piece.animate.move_to(board_loc(row, col))
      self.play(anim, rate_func=rate_functions.ease_out_bounce,
                run_time=0.8 - 0.05 * (5-row))
      to_fade_out.append(piece)
      pieces.append(piece)

    self.wait(0.2)

    win_box = SurroundingRectangle(VGroup(pieces[-1], pieces[1]),
                                   color=IBM_BLUE_60,
                                   stroke_width=8,
                                   buff=0.1, corner_radius=0.1)
    self.add(win_box, layer=1)
    self.play(Create(win_box))
    self.pause()
    to_fade_out.append(win_box)


    code = CodeWindow(first_scene_code, tab_width=2)
    code.scale(0.8).align_to([-7.0, 3.9, 0], UL)

    b_1 = pieces[0][1].copy()
    b_2 = pieces[1][1].copy()
    b_3 = pieces[2][1].copy()
    b_4 = pieces[3][1].copy()
    self.remove(pieces[0][1], pieces[1][1], pieces[2][1], pieces[3][1])

    self.play(*[FadeOut(mobj) for mobj in to_fade_out],
      Transform(b_1, code['line_17'][14]),
      Transform(b_2, code['line_18'][14]),
      Transform(b_3, code['line_19'][14]),
      Transform(b_4, code['line_20'][14]),
    )
    self.wait(0.2)
    self.play(FadeIn(code), FadeOut(title),
              FadeOut(b_1), FadeOut(b_2), FadeOut(b_3), FadeOut(b_4))


    self.wait(2)


class ConnectFourOutro(AnimatedCodeScene):
  def construct(self):
    super().construct()

    self.next_section(skip_animations=True)

    variables = VariableArea()
    variables.align_to([6.5, 3.9, 0], UR)

    self.set_variables(variables)
    self.add(variables)

    rows = []
    for i in range(0, 6):
      temp_list = List([PLAYER_ONE_TOKEN] * 7)
      if i == 0:
        temp_list.scale(0.9)
        temp_list.align_to([2.238173, 0.9357788, 0], UL)
      else:
        temp_list.next_to(prev_list, DOWN, buff=0.4)
        temp_list.scale(0.9).align_to([7, 0, 0], RIGHT)
      for j in range(0, 7):
        # Remove the placeholder R glyph (but not the quotes) so it
        # looks like a space
        temp_list[f'index_{j}'].remove(temp_list[f'index_{j}'][1])
      temp_list.contents = [' '] * 7
      rows.append(temp_list)
      prev_list = temp_list
    self.rows = rows

    board_list = List([rows[0]] * 6).scale(0.61).align_to([2, 1.7, 0], UL)
    game_board_box = self.create_variable('game_board', board_list)
    game_board_pointer = Pointer(game_board_box['contents'].get_bottom(),
      [board_list['index_0'].get_top()[0],
       board_list.get_top()[1],
       0])
    self.add(board_list)
    variables.add([('game_board_pointer', game_board_pointer)])

    arrows = []
    for i in range(0, 6):
      start = board_list[f'index_{i}'].get_bottom()
      stop = np.array([
        rows[i]['index_0'].get_bottom()[0],
        rows[i].get_top()[1],
        0])
      new_pointer = Pointer(start, stop)
      self.bring_to_back(new_pointer)
      arrows.append(new_pointer)
    self.add(*rows)

    backgrounds = {}
    anims = []
    for r in range(0, len(partial_game)):
      for c in range(0, len(partial_game[0])):
        token = partial_game[r][c]
        token = token.replace('*', '')
        if token == ' ':
          continue
        _, copy_anims = rows[r].animate_set(c, token)
        color = PLAYER_ONE_COLOR if token == PLAYER_ONE_TOKEN else PLAYER_TWO_COLOR
        back = rows[r].add_background_for_cell(c, color)
        backgrounds[(r, c)] = back
        anims += copy_anims
    self.play(*anims)
    self.next_section()
    self.pause()

    six_functions = """
Implemented:
  - make_board()
  - add_token()
  - winner_horizontal()
  - winner_vertical()
  - winner_diagonal1()
  - winner_diagonal2()

To Finish:
  - get_user_input()
    - Check for invalid or full columns
  - Game Loop
    - switch between players
    - call get_user_input()
    - call add_token()
    - call winner_ functions
    """

    t = Paragraph(six_functions, color=BLACK, line_spacing=0.5,
                  font_size=18, font=ROBOTO_MONO).scale(1.4)
    t.align_to([-7, 0, 0], LEFT)
    self.play(FadeIn(t[:8]))
    self.pause()
    self.play(FadeIn(t[9:12]))
    self.pause()
    self.play(FadeIn(t[12:]))


    self.wait(2)