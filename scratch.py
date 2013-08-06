import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

slant45 = 1 / math.sin(math.radians(45))
WIDTH = 1

def shape(p):

    p.turn_to(-135)
    p.move_forward(WIDTH * slant45 / 2)
    a = p.position

    p.move_forward(WIDTH * slant45)

    p.turn_to(0)
    p.arc_right(20, 10 * WIDTH)
    b = p.position
    p.undo()

    p.move_to(a)
    p.turn_to(0)
    p.arc_to(b)
    heading = p.heading
    p.undo()

    p.move_to(a)
    p.turn_to(-135)
    p.line_forward(WIDTH * slant45)

    p.turn_to(0)
    p.arc_to(b)
    p.turn_to(heading + 180)
    p.arc_to(a)


def draw():
    p = Pen()

    #p.set_mode(StrokeOutlineMode(WIDTH, 0.2, '#f51700', '#1d0603').outliner_mode())
    p.stroke_mode(0.2, '#1d0603')
    #.outline_mode(0.2, 0.06, '#1d0603')
    #p.fill_mode('#f51700')

    shape(p)

    return p.paper

if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg())
