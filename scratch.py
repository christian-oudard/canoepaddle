import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.set_color('red')

    p.set_width(1.0)

    p.move_to((0, 0))
    p.turn_to(-120)
    p.move_forward(3)
    p2 = p.position

    p.move_to((0, 0))
    p.turn_to(30)
    p.move_forward(3)
    p1 = p.position

    p.turn_left(90)
    h1 = p.heading
    p.arc_to(p2)

    p.end()
    p.set_color('green')
    p.move_to(p1)
    p.turn_to(h1)
    p.arc_left(210, 3)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(3))
