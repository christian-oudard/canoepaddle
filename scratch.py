import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.break_stroke()
    p.turn_left(90)
    p.line_forward(5)
    p.paper.join_paths()

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(3))
