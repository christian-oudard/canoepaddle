import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    p.move_to((0, 0))
    p.turn_to(0)

    # Draw a square with one side a different color. It joins to the
    # beginning correctly.
    p.set_stroke_mode(2.0, color='black')
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.set_stroke_mode(2.0, color='red')
    p.line_forward(5)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg(1))
