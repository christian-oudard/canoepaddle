from canoepaddle import Pen
from canoepaddle.point import float_equal
from scipy.special import fresnel
import numpy


def euler_spiral_parametric(t):
    s, c = fresnel(t)
    return numpy.column_stack((t, c, s))


def draw_parametric_func(pen, f, t_range):
    txy_values = f(t_range)
    t, x, y = txy_values[0]
    pen.move_to((x, y))
    for t, x, y in txy_values[1:]:
        pen.line_to((x, y))
        mod = t % 1.0
        if float_equal(mod, 0) or float_equal(mod, 1.0):
            pen.circle(0.01)


step = 0.01
t_range = numpy.arange(-4 + step, 4, step)

pen = Pen()
pen.stroke_mode(0.01, 'green')
draw_parametric_func(pen, euler_spiral_parametric, t_range)

pen.fill_mode('green')
pen.move_to((0.5, 0.5))
pen.circle(0.01)
pen.move_to((-0.5, -0.5))
pen.circle(0.01)

print(pen.paper.format_svg(5, resolution=500))

# TODO: euler spiral solver to end at a particular point. newton-raphson method for root finding convergence?
