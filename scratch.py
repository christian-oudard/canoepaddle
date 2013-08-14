import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():

    def shape():
        p = Pen()
        p.stroke_mode(1.0)
        p.turn_to(0)
        p.line_forward(3)
        p.fill_mode()
        p.square(2)
        return p.paper

    paper = Paper()

    paper_a = shape()
    paper_a.translate((-3, 0))
    paper.merge(paper_a)

    paper_b = shape()
    paper_b.translate((3, 0))
    paper_b.join_paths()
    paper.merge(paper_b)

    return paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4))
