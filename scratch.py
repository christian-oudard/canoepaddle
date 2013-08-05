import math

from canoepaddle import Pen, Paper
from grapefruit import Color


def draw():
    paper = Paper()

    from canoepaddle.mode import OutlinedFillMode
    mode = OutlinedFillMode(0.2, 'red', 'black')

    p = Pen()
    p.set_mode(mode)
    p.turn_to(0)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    p = Pen()
    p.set_mode(mode)
    p.turn_to(180)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    return paper

if __name__ == '__main__':
    p = Pen()
    paper = draw()
    print(paper.format_svg())
