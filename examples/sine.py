import math
import itertools

from canoepaddle import Pen

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def sine(pen, start, end, step, amplitude, frequency, phase=0):
    start_x, start_y = pen.position
    start_heading = pen.heading

    # Parametric sine wave.
    def f(t):
        return (
            t,
            amplitude * math.sin(frequency * t + phase),
        )

    for i in itertools.count():
        t = start + step * i
        if t > end:
            break
        x, y = f(t)

        x += start_x
        y += start_y

        if i == 0:
            pen.move_to((x, y))
        else:
            pen.line_to((x, y))

    pen.move_to((start_x, start_y))
    pen.turn_to(start_heading)


def draw():

    p = Pen()

    for width in [0.01, 0.1, 0.3, 0.5, 0.8, 1.0]:
        p.stroke_mode(width)
        sine(
            p,
            start=0,
            end=10,
            step=0.1,
            amplitude=1.0,
            frequency=4 / math.pi,
            phase=0,
        )
        p.turn_to(-90)
        p.move_forward(1.0 + 2 * width)

    return p.paper


if __name__ == '__main__':
    paper = draw()
    bounds = paper.bounds()
    bounds.left -= 1
    bounds.right += 1
    bounds.bottom -= 1
    bounds.top += 1
    paper.override_bounds(bounds)
    print(paper.format_svg(6, resolution=100))
    #print(paper.format_svg(2, resolution=100))
    #print(paper.format_svg(1, resolution=100))
