import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():
    paper = Paper()

    p = Pen()
    p.stroke_mode(sqrt2)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(5 * sqrt2, end_angle=45)
    p.paper.mirror_x(0)
    paper.merge(p.paper)

    p = Pen()
    p.stroke_mode(sqrt2)
    p.move_to((0, 0))
    p.turn_to(45)
    p.line_forward(5 * sqrt2)
    paper.merge(p.paper)

    paper.join_paths()
    #paper.fuse_paths()

    return paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
