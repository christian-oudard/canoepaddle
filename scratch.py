import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)


def draw():

    p = Pen()
    p.paper.override_bounds(-5, -5, 5, 5)
    p.stroke_mode(0.1)
    p.circle(0.2)
    p.paper.add_text('a', (0, 0), 1)

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(4, resolution=50))
