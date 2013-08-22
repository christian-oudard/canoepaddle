import math

from canoepaddle import *

from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)

#p.outline_mode(1.0, 0.1)

def draw():

    p = Pen()

    p.stroke_mode(2.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

    def copy_cap(pen, end):
        pen.copy()
        pen.line_to(end)

    p.last_segment().end_cap = copy_cap

    return p.paper


if __name__ == '__main__':
    paper = draw()
    bounds = paper.bounds()
    bounds.left -= 1
    bounds.right += 1
    bounds.bottom -= 1
    bounds.top += 1
    paper.override_bounds(bounds)
    #print(paper.format_svg(6, resolution=100))
    print(paper.format_svg(2, resolution=100))
    #print(paper.format_svg(1, resolution=100))
