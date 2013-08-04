import math

from canoepaddle import Pen, Paper
from grapefruit import Color


def draw():
    paper = Paper()

    p = Pen()
    p.fill_mode()
    p.turn_to(0)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    p = Pen()
    p.fill_mode()
    p.turn_to(180)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    return paper

if __name__ == '__main__':
    p = Pen()
    paper = draw()
    print(paper.format_svg())
