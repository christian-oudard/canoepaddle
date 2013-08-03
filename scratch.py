import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_width(2.0)
    p.move_to((0, 0))
    p.turn_to(0)

    # Draw a square.
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(0))
