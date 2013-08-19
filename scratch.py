import math

from canoepaddle import Pen, Paper
from canoepaddle.mode import *
from grapefruit import Color

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():
    p = Pen()
    p.stroke_mode(0.01)

    p.move_to((0.4192474135783115, 0.430155866908118))
    p.line_to((0.027797353665647728, 0.49398573855399375))
    p.break_stroke()
    p.text('1', 0.1)
    p.move_to((0.5879460634280621, 0.19217214115618309))
    p.line_to((0.29408558178545596, 0.7948715620494309))
    p.break_stroke()
    p.move_to((0.9369476736291589, 0.39225805628934773))
    p.line_to((0.4192474135783115, 0.430155866908118))
    p.break_stroke()
    p.move_to((0.5879460634280621, 0.19217214115618309))
    p.line_to((0.027797353665647728, 0.49398573855399375))
    p.break_stroke()
    p.move_to((0.9369476736291589, 0.39225805628934773))
    p.line_to((0.41710842266435744, 0.7527652903183519))
    p.break_stroke()

    p.paper.join_paths()

    return p.paper


if __name__ == '__main__':
    paper = draw()
    print(paper.format_svg(3, resolution=500))
