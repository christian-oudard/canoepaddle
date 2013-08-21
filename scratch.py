import math

from canoepaddle import Pen, Paper, Bounds
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():

    pen = Pen()

    pen.fill_mode('gray')
    Bounds(0, 0, 3 * sqrt2, 3 - 1.5 * sqrt2).draw(pen)

    pen.fill_mode('black')
    pen.move_to((0, 0))
    pen.turn_to(45)
    pen.arc_right(90, 3)


    return pen.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(6, resolution=100))
