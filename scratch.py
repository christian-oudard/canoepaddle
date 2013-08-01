import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    c = (0, 0)
    p.set_width(1.0)
    p.move_to(c)
    p.turn_to(0)
    p.arc_left(180, 1)
    p.end()
    p.arc_left(90, 2)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(1))
