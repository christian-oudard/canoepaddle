import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():
    #p = Pen()
    #p.set_mode(OutlineMode(1.0, 0.2, '#1d0603'))

    #p.move_to((-4.000000000000001, 3.6))
    #p.turn_to(270)

    #p.line_to_y(0.5, end_angle=45)

    #p.turn_to(45)
    #p.move_forward(1.2071067811865475)
    #p.turn_to(-45)
    #p.line_to_y(0, end_angle=0)

    ###

    p = Pen()
    p.set_mode(StrokeMode(0.2))

    def square():
        p.turn_to(180)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)

    p.move_to((0, 0))
    square()
    p.move_to((2, 0))
    square()

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
