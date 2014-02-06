import math

from canoepaddle import Pen

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


# Parametric sine wave.

def sine_func_factory(amplitude, frequency, phase=0):
    def f(t):
        return (
            t,
            amplitude * math.sin(frequency * t + phase),
        )
    return f


def draw():

    p = Pen()

    # Draw sine waves in various widths.
    for width in [0.01, 0.1, 0.3, 0.5, 0.8, 1.0]:
        p.stroke_mode(width)

        func = sine_func_factory(
            amplitude=1.0,
            frequency=4 / math.pi,
            phase=0,
        )
        p.parametric(
            func,
            start=0,
            end=10,
            step=0.1,
        )
        # Next line.
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
