import math
from collections import namedtuple

import vec

sqrt2 = 2.0**0.5

Point = namedtuple('Point', 'x, y')

stroke_width = 1

class Paper:
    def __init__(self):
        self.segments = []
        self.precision = 12

    def add_segment(self, a, b):
        self.segments.append((
            Point(*a),
            Point(*b),
        ))

    def to_svg_path(self):
        output = []
        last_a = last_b = None
        first = self.segments[0][0]
        for a, b in self.segments:
            # Start a new line segment if necessary.
            if a != last_b:
                output.append('M{:.{p}f},{:.{p}f}'.format(a.x, -a.y, p=self.precision))
            # Close the path, or continue the current segment.
            if b == first:
                output.append('z')
            else:
                output.append('L{:.{p}f},{:.{p}f}'.format(b.x, -b.y, p=self.precision))
            last_a, last_b = a, b
        return ' '.join(output)

    def to_svg_path_thick(self, width):
        p = Pen()
        p.paper.precision = self.precision
        halfwidth = width / 2
        for a, b in self.segments:
            segment_length = vec.dist(a, b)
            p.move_to(a)
            p.turn_towards(b)
            p.turn_right(90)
            p.move_forward(-halfwidth)
            p.stroke_forward(width)
            p.turn_left(90)
            p.stroke_forward(segment_length)
            p.turn_left(90)
            p.stroke_forward(width)
            p.stroke_close()
        return p.paper.to_svg_path()


class Pen:
    def __init__(self):
        self.paper = Paper()
        self._heading = 0
        self._position = (0.0, 0.0)
        self._width = 1.0
        self._slant = None # Perpendicular to heading.

    def move_to(self, point):
        self._position = point

    def turn_to(self, heading):
        self._heading = heading % 360

    def turn_towards(self, point):
        self.turn_to(
            math.degrees(
                vec.heading(
                    vec.vfrom(self._position, point))))

    def turn_left(self, angle):
        self.turn_to(self._heading + angle)

    def turn_right(self, angle):
        self.turn_left(-angle)

    def move_forward(self, distance):
        self._position = vec.add(
            self._position,
            vec.rotate((distance, 0), math.radians(self._heading)),
        )

    def stroke_forward(self, distance):
        old_position = self._position
        self.move_forward(distance)
        self.paper.add_segment(old_position, self._position)

    def stroke_close(self):
        first_point = self.paper.segments[0][0]
        self.paper.add_segment(self._position, first_point)
        self.move_to(first_point)

    @property
    def position(self):
        return self._position

    @property
    def heading(self):
        return self._heading

if __name__ == '__main__':
    p = Pen()

    p.move_to((-5, 0))
    p.turn_to(-45)
    p.stroke_forward(5)
    p.turn_left(90)
    p.stroke_forward(10)

    path_data = p.paper.to_svg_path_thick(width=1.0)

    from string import Template
    with open('template.svg') as f:
        t = Template(f.read())
    print(t.substitute(path_data=path_data))
