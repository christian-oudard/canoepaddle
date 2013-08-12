import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():
    paper = Paper()

    def stroke(p):
        #p.fill_mode()
        #p.stroke_mode(1)
        #p.outline_mode(1, 0.2)

        #p.move_to((0, 0))
        #p.turn_to(0)
        #p.arc_left(90, 3)
        #p.turn_left(90)
        #p.line_forward(2)
        #p.turn_right(90)
        #p.arc_right(90, 3)

        p.stroke_mode(2)
        p.move_to((0, 0))
        p.turn_to(0)
        p.arc_left(90, 5)

    p = Pen()
    stroke(p)
    paper.merge(p.paper)

    p = Pen()
    stroke(p)
    p.paper.mirror_x(0)
    paper.merge(p.paper)

    p = Pen()
    stroke(p)
    p.paper.mirror_y(0)
    paper.merge(p.paper)

    return paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
