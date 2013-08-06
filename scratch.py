import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color


def draw():
    p = Pen()
    p.set_mode(OutlinedStrokeMode(1.0, 0.2, 'red', 'black'))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    return p.paper

if __name__ == '__main__':
    p = Pen()
    paper = draw()
    print(paper.format_svg())
