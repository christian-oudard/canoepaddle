import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():
    # We can set up a pattern in one mode,
    p = Pen()
    p.set_mode(StrokeOutlineMode(sqrt3, 0.2 * sqrt3, 'blue', 'black'))

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5, end_slant=60)

    # Then continue it in another mode without caring what the first mode was.
    old_mode = p.mode
    p.set_mode(p.mode.outliner_mode())

    p.turn_to(60)
    p.move_forward(1.0)

    p.turn_left(60)
    p.line_forward(2.0)
    p.turn_right(120)
    p.line_forward(2.0)
    p.turn_right(120)
    p.line_forward(2.0)

    p.turn_to(60)
    p.move_forward(3.0)
    p.turn_to(120)

    p.set_mode(old_mode)

    p.line_forward(5, start_slant=60)

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(3))
