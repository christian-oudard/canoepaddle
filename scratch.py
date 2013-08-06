import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color


def draw():
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_left(90, 5)
    p.arc_left(90, 5)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_right(90, 5)
    p.arc_right(90, 5)

    return p.paper

if __name__ == '__main__':
    p = Pen()
    paper = draw()
    print(paper.format_svg(3))
