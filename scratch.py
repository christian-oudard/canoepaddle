import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():
    paper = Paper()

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.line_to((-3, 0))
    paper.merge(p.paper)

    p = Pen()
    p.stroke_mode(1.0)
    p.line_to((-3, 0))
    p.move_to((-6, 0))
    paper.merge(p.paper)

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(1.0, end_slant=45)
    p.turn_to(-135)
    p.move_forward(1.4142135623730951)
    p.turn_to(-90)
    p.line_forward(2)
    paper.merge(p.paper)

    #paper.join_paths()
    #XXX For some reason right now one of the segments is in the svg output twice??

    return paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(1))
