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

    def scythe_cap(pen, end):
        start_heading = pen.heading

        temp_pen = pen.copy()
        temp_pen.turn_right(75)
        temp_pen.move_forward(1.0)
        tip = temp_pen.position

        temp_pen.move_to(end)
        temp_pen.turn_to(start_heading)
        temp_pen.arc_to(tip)
        return_heading = temp_pen.heading + 180

        pen.turn_to(start_heading)
        pen.arc_to(tip)
        pen.turn_to(return_heading)
        pen.arc_to(end)


    p.last_segment().end_cap = scythe_cap
    p.move_forward(5)
    p.fill_mode()
    p.circle(.5)

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
