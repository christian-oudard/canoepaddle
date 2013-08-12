import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():
    p = Pen()
    p.outline_mode(1, .1)

    p.move_to((2, 0))
    p.line_to((1, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((3, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((0, 0))

    p.paper.join_paths()

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
