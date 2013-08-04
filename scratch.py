import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_stroke_mode(1.0)
    p.arc_left(90, 0.5)


if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(3))
