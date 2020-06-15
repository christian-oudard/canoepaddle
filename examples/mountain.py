import math

from canoepaddle import Pen

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def draw():

    p = Pen()

    center_radius = 3.0
    start_radius = radius = 100
    start_width = width = 3.0
    ratio = (1 / 2) ** (1/5)

    series = []
    while radius > center_radius / sqrt2:
        series.append((radius, width))
        radius *= ratio
        width *= ratio

    p.move_to((0, 0))
    for radius, width in series:
        p.stroke_mode(width, 'black')
        p.circle(radius)

    # Parametric conic spirals.
    p.move_to((0, 0))

    def spiral(theta):
        b = (1 / 2) ** (-2 / math.pi)
        r = start_radius * (b ** (-theta))
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = start_radius - r
        return (x, y, z)

    def spiral_top1(t):
        x, y, z = spiral(t)
        return x, y

    def spiral_top2(t):
        x, y, z = spiral(t)
        x = -x
        y = -y
        return x, y

    # Top spirals.
    p.stroke_mode(start_width, 'black')
    p.parametric(spiral_top1, 0, 4*math.pi, .1)
    p.parametric(spiral_top2, 0, 4*math.pi, .1)

    # Blank out the bottom triangle.
    p.fill_mode('white')
    p.move_to((0, 0))
    s = start_radius + start_width
    p.line_to((-s, -s))
    p.line_to((+s, -s))
    p.line_to((0, 0))

    # Horizontal lines for the bottom triangle.
    for radius, width in series:
        p.stroke_mode(width, 'black')
        p.move_to((-radius, -radius))
        p.line_to(
            (+radius, -radius),
            start_slant=45,
            end_slant=-45,
        )

    # Front spirals.
    def spiral_front1(t):
        x, y, z = spiral(t)
        return (x, z - start_radius)

    def spiral_front2(t):
        x, y, z = spiral(t)
        x = -x
        y = -y
        return (x, z - start_radius)

    p.move_to((0, 0))
    p.stroke_mode(start_width, 'black')
    p.parametric(spiral_front1, 0, math.pi, .1)
    p.parametric(spiral_front2, math.pi, 2*math.pi, .1)
    p.parametric(spiral_front1, 2*math.pi, 3*math.pi, .1)

    # Fill in the center.
    p.move_to((0, 0))
    p.fill_mode('black')
    p.circle(center_radius)

    return p.paper


if __name__ == '__main__':
    paper = draw()
    bounds = paper.bounds()
    bounds.left -= 10
    bounds.right += 10
    bounds.bottom -= 10
    bounds.top += 10
    paper.override_bounds(bounds)
    print(paper.format_svg(6, resolution=10))
