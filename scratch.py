import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_stroke_mode(1.0, color=(1.0, 0.0, 0.0))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.set_fill_mode(color=(0.0, 1.0, 0.0))
    p.move_to((2, 2))
    p.circle(2)

    p.set_stroke_mode(1.0, color=(0.0, 0.0, 1.0))
    p.move_to((0, 4))
    p.turn_to(0)
    p.line_forward(4)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(3))
