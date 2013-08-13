import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():
    p = Pen()
    p.outline_mode(1, 0.2)

    p.move_to((-1, 1))
    p.line_to((0, 0))
    p.break_stroke()
    p.turn_to(-45)
    p.line_forward(3, end_angle=0)


    #p.paper.mirror_x(3)
    p.paper.join_paths()
    p.paper.fuse_paths()

    print(p._log)
    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
