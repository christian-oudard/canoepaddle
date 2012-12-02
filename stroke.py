import math
from collections import namedtuple

import vec

sqrt2 = math.sqrt(2)

Point = namedtuple('Point', 'x, y')

class Segment:
    def __init__(self, a, b, start_angle=None, end_angle=None):
        self.a = a
        self.b = b
        self.start_angle = start_angle
        self.end_angle = end_angle

    def __iter__(self):
        yield self.a
        yield self.b

    def length(self):
        return vec.dist(self.a, self.b)

    def heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))


class Paper:
    precision = 12

    def __init__(self):
        self.segments = []

    def add_segment(self, a, b, start_angle=None, end_angle=None):
        self.segments.append(Segment(
            Point(*a),
            Point(*b),
            start_angle,
            end_angle,
        ))

    def to_svg_path(self):
        output = []
        last_a = last_b = None
        first = self.segments[0].a
        for seg in self.segments:
            # Start a new line segment if necessary.
            if seg.a != last_b:
                output.append('M{:.{p}f},{:.{p}f}'.format(
                    seg.a.x, -seg.a.y, p=self.precision))
            # Close the path, or continue the current segment.
            if seg.b == first:
                output.append('z')
            else:
                output.append('L{:.{p}f},{:.{p}f}'.format(
                    seg.b.x, -seg.b.y, p=self.precision))
            last_a, last_b = seg.a, seg.b
        return ' '.join(output)

    def to_svg_path_thick(self, width):
        p = Pen()

        # Handle joints by setting the in-between angles for each segment.
        segments = []
        #for previous, next in pairwise(self.segments):
            #STUB

        for seg in self.segments:
            start_slant = self.calc_slant(seg.heading(), seg.start_angle)
            slant_width = self.calc_slant_width(width, start_slant)

            end_slant = self.calc_slant(seg.heading(), seg.end_angle)
            end_slant_width = self.calc_slant_width(width, end_slant)

            extra_length = self.calc_extra_length(width, start_slant, end_slant)
            if abs(extra_length) > seg.length():
                raise ValueError('Slant is too extreme for the length and width of the segment.')

            # Draw the starting thickness edge.
            p.move_to(seg.a)
            p.turn_to(seg.heading())
            p.turn_right(start_slant)

            p.move_forward(-slant_width / 2)
            p.stroke_forward(slant_width)

            # Draw along the length of the segment.
            p.turn_left(start_slant)
            p.stroke_forward(extra_length + seg.length())

            # Draw the ending thickness edge.
            p.turn_left(180 - end_slant)
            p.stroke_forward(end_slant_width)

            # Close the path to finish.
            p.stroke_close()

        return p.paper.to_svg_path()

    @staticmethod
    def calc_slant(heading, angle):
        r"""
        The slant of a stroke is defined as the angle between the
        direction of the stroke and the start angle of the pen.

        90 degree slant:
         ___
        |___|

        60 degree slant:
        ____
        \___\

        120 degree slant:
         ____
        /___/

        """
        if angle is None:
            return 90
        slant = (heading - angle) % 180
        if slant > 179 or slant < 1:
            raise ValueError('Slant angle is too steep')
        return slant

    @staticmethod
    def calc_slant_width(width, slant):
        return width / math.sin(math.radians(slant))

    @staticmethod
    def calc_extra_length(width, slant1, slant2):
        return (width / 2) * (
            math.tan(math.radians(slant1 - 90)) -
            math.tan(math.radians(slant2 - 90))
        )


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

    def stroke_forward(self, distance, start_angle=None, end_angle=None):
        old_position = self._position
        self.move_forward(distance)
        self.paper.add_segment(
            old_position,
            self._position,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def stroke_close(self):
        first_point = self.paper.segments[0].a
        self.paper.add_segment(self._position, first_point)
        self.move_to(first_point)

    @property
    def position(self):
        return self._position

    @property
    def heading(self):
        return self._heading

if __name__ == '__main__':
    path_data = ''

    p = Pen()
    p.move_to((-3, 3))
    p.turn_to(0)
    p.stroke_forward(6, start_angle=45, end_angle=30)
    path_data += p.paper.to_svg_path_thick(width=1.0)
    path_data += p.paper.to_svg_path()

    p = Pen()
    p.move_to((-3, 0))
    p.turn_to(190)
    p.stroke_forward(6, start_angle=90, end_angle=45)
    path_data += p.paper.to_svg_path_thick(width=1.0)
    path_data += p.paper.to_svg_path()

    p = Pen()
    p.move_to((-3, -3))
    p.turn_to(0)
    p.stroke_forward(6)
    p.turn_right(60)
    p.stroke_forward(6)
    path_data += p.paper.to_svg_path_thick(width=1.0)
    path_data += p.paper.to_svg_path()

    from string import Template
    with open('template.svg') as f:
        t = Template(f.read())
    print(t.substitute(path_data=path_data))
