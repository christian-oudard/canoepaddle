import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.move_to((0, 0))
    p.turn_to(0)
    p.set_outline_mode(1.0, 0.2)
    p.line_forward(3)
    p.set_outline_mode(1.0, 0.4)
    p.line_forward(3)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(1))
