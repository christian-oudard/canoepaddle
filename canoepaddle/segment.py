import math

import vec
from point import Point


class LineSegment:

    def __init__(self, a, b, width, start_angle=None, end_angle=None):
        self.a = Point(*a)
        self.b = Point(*b)
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.width = width
        self.radius = None

    def __iter__(self):
        yield self.a
        yield self.b

    def __repr__(self):
        return (
            '{}(a={a}, b={b}, width={width}, '
            'start_angle={start_angle}, end_angle={end_angle})'
            .format(self.__class__.__name__, **self.__dict__)
        )

    def length(self):
        return vec.dist(self.a, self.b)

    def heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))

    @property
    def start_heading(self):
        return self.heading()

    @property
    def end_heading(self):
        return self.heading()

    #TODO: make these into properties, and add caching.

    def start_slant(self):
        return self.calc_slant(self.heading(), self.start_angle)

    def end_slant(self):
        return self.calc_slant(self.heading(), self.end_angle)

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

    def start_slant_width(self):
        return self.calc_slant_width(self.width, self.start_slant())

    def end_slant_width(self):
        return self.calc_slant_width(self.width, self.end_slant())

    @staticmethod
    def calc_slant_width(stroke_width, slant):
        """
        The distance between the leading corners of the stroke can be longer if
        the stroke start is angled.
        """
        return stroke_width / math.sin(math.radians(slant))

    def extra_length(self):
        """
        The extra length along the right side of the segment due to the angled
        start and end. Note that the same value for the left side is the
        negative of this.
        """
        extra_length = (self.width / 2) * (
            math.tan(math.radians(self.start_slant() - 90)) -
            math.tan(math.radians(self.end_slant() - 90))
        )
        if abs(extra_length) > self.length():
            raise ValueError(
                'Slant is too extreme for the length and width of the '
                'segment: {}'.format(self)
            )
        return extra_length


class ArcSegment:
    def __init__(
        self, a, b, width, arc_angle, radius, start_heading, end_heading,
    ):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.arc_angle = arc_angle
        self.radius = radius
        self.start_heading = start_heading
        self.end_heading = end_heading

    def start_slant(self):
        return 90  # Not yet implemented.

    def end_slant(self):
        return 90  # Not yet implemented.

    def start_slant_width(self):
        return self.width

    def end_slant_width(self):
        return self.width

    def heading(self):
        return self.start_heading
