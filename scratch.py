import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_width(1.0)

    p.set_color('red')
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)

    p.set_color('green')
    p.turn_right(60)
    p.line_forward(6)


if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
