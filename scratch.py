import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_width(1.0)

    p.line_forward(3)
    p.arc_left(90, 3)
    p.turn_left(90)
    p.move_forward(3)
    p.circle(0.5)
    p.move_forward(3)
    p.square(1)

    p.paper.translate((1, 1))




if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
