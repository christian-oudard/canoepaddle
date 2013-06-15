import math

import vec
from .point import Point
from .geometry import intersect_circle_line


def closest_point_to(target, points):
    return min(
        points,
        key=lambda p: vec.mag2(vec.vfrom(target, p))
    )


class LineSegment:

    def __init__(self, a, b, width=None, start_angle=None, end_angle=None):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.radius = None

        self.set_start_angle(start_angle)
        self.set_end_angle(end_angle)

    def __iter__(self):
        yield self.a
        yield self.b

    def __repr__(self):
        return (
            '{}(a={a}, b={b}, width={width}, '
            'start_angle={_start_angle}, end_angle={_end_angle})'
            .format(self.__class__.__name__, **self.__dict__)
        )

    def length(self):
        return vec.dist(self.a, self.b)

    def _heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))

    @property
    def start_heading(self):
        return self._heading()

    @property
    def end_heading(self):
        return self._heading()

    def start_slant(self):
        return self.calc_slant(self.start_heading, self._start_angle)

    def end_slant(self):
        return self.calc_slant(self.end_heading, self._end_angle)

    def set_start_angle(self, start_angle):
        self._start_angle = start_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.start_heading))
            v = vec.rotate(v, -math.radians(self.calc_slant(self.start_heading, start_angle)))
            v = vec.norm(v, self.start_slant_width() / 2)
            self.a_left = vec.sub(self.a, v)
            self.a_right = vec.add(self.a, v)
            self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self._end_angle = end_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.end_heading))
            v = vec.rotate(v, -math.radians(self.calc_slant(self.end_heading, end_angle)))
            v = vec.norm(v, self.end_slant_width() / 2)
            self.b_left = vec.sub(self.b, v)
            self.b_right = vec.add(self.b, v)
            self.check_degenerate_segment()

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

    def check_degenerate_segment(self):
        # Check the extra length along the right side of the segment due to the
        # angled start and end. Note that the same value for the left side is
        # the negative of this. If the extra length goes negative on one side,
        # this will draw an incorrect segment, so raise an exception.
        if (
            not hasattr(self, '_start_angle') or
            not hasattr(self, '_end_angle')
        ):
            return

        extra_length = (self.width / 2) * (
            math.tan(math.radians(self.start_slant() - 90)) -
            math.tan(math.radians(self.end_slant() - 90))
        )
        if abs(extra_length) > self.length():
            raise ValueError(
                'Slant is too extreme for the length and width of the '
                'segment: {}'.format(self)
            )


class ArcSegment(LineSegment):
    def __init__(
        self, a, b, width, center, radius, arc_angle,
        start_heading, end_heading, start_angle, end_angle,
    ):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.arc_angle = arc_angle
        self.center = center
        self.radius = radius
        self._start_heading = start_heading
        self._end_heading = end_heading

        self.set_start_angle(start_angle)
        self.set_end_angle(end_angle)

    @property
    def start_heading(self):
        return self._start_heading

    @property
    def end_heading(self):
        return self._end_heading

    def start_slant_width(self):
        return self.width

    def end_slant_width(self):
        return self.width

    def set_start_angle(self, start_angle):
        self._start_angle = start_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.start_heading))
            v = vec.rotate(v, -math.radians(self.calc_slant(self.start_heading, start_angle)))
            points = intersect_circle_line(
                self.center,
                self.radius - self.width / 2,
                self.a,
                vec.add(self.a, v),
            )
            self.a_left = closest_point_to(self.a, points)
            points = intersect_circle_line(
                self.center,
                self.radius + self.width / 2,
                self.a,
                vec.add(self.a, v),
            )
            self.a_right = closest_point_to(self.a, points)
            self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self._end_angle = end_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.end_heading))
            v = vec.rotate(v, -math.radians(self.calc_slant(self.end_heading, end_angle)))
            points = intersect_circle_line(
                self.center,
                self.radius - self.width / 2,
                self.b,
                vec.add(self.b, v),
            )
            self.b_left = closest_point_to(self.b, points)
            points = intersect_circle_line(
                self.center,
                self.radius + self.width / 2,
                self.b,
                vec.add(self.b, v),
            )
            self.b_right = closest_point_to(self.b, points)
            self.check_degenerate_segment()

    def check_degenerate_segment(self):
        return #STUB
