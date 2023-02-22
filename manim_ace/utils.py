from manim import *

def surround(origRect, targetMobj, offset=ORIGIN):
    """Reshapes one SurroundingRectangle around another mobject."""
    new_box = SurroundingRectangle(targetMobj, color=origRect.color,
                                   buff=origRect.buff,
                                   stroke_width=origRect.stroke_width,
                                   corner_radius=origRect.corner_radius)
    new_box.shift(offset)
    # Intentionally not ReplacementTransform so this can be used in a
    # self.play and keep using the existing variable
    return Transform(origRect, new_box)


def occlude(mobj, width=None, buff=0):
    """Return a white, transparent rectangle around a mobject."""
    if not width:
        width = mobj.width
    rect = Rectangle(color=WHITE, stroke_width=0,
                     width=width + buff * 2,
                     height=mobj.height + buff * 2,
                     fill_opacity=1.0)
    rect.set_opacity(0.0)
    rect.align_to(mobj.get_corner(UL) + [-buff / 2, buff / 2, 0], UL)
    return rect


def become_in_place(mobj: Mobject, target: Mobject):
    """Turn mobj into target, but still located at mobj"""
    return Transform(mobj, target.copy().move_to(mobj))