import math

import vec
from .point import Point, float_equal, points_equal
from .geometry import (
    intersect_lines,
    intersect_circle_line,
    intersect_circles,
)


MAX_TURN_ANGLE = 179


def closest_point_to(target, points):
    return min(
        points,
        key=lambda p: vec.mag2(vec.vfrom(target, p))
    )


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
    return slant


class Segment:
    def __init__(self, a, b, width=None):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.a_left = None
        self.a_right = None
        self.b_left = None
        self.b_right = None

    def __iter__(self):
        yield self.a
        yield self.b

    def __repr__(self):
        strings = []  # COVER
        for field in self.repr_fields:
            value = getattr(self, field)
            if value is None:
                continue
            strings.append('{}={}'.format(field, value))
        return '{}({})'.format(self.__class__.__name__, ', '.join(strings))

    def join_with(self, other):
        assert points_equal(self.b, other.a)
        if self.width is None or other.width is None:
            return

        if isinstance(other, LineSegment):
            self.join_with_line(other)
        elif isinstance(other, ArcSegment):
            self.join_with_arc(other)

    def check_degenerate_segment(self):
        if any(
            p is None for p in
            [self.a_left, self.a_right, self.b_left, self.b_right],
        ):
            return

        # Check whether the endcap lines intersect. If so, this will cause
        # graphical glitches when drawing the segment.
        intersection = intersect_lines(
            self.a_left, self.a_right,
            self.b_left, self.b_right,
            segment=True,
        )
        if intersection is not None:
            raise ValueError('Degenerate segment, endcaps cross each other.')


class LineSegment(Segment):

    repr_fields = ['a', 'b', 'width', 'start_angle', 'end_angle']

    def __init__(self, a, b, width, start_angle, end_angle):
        super().__init__(a, b, width)

        self.start_angle = None
        self.end_angle = None
        self.set_start_angle(start_angle)
        self.set_end_angle(end_angle)

    def join_with_line(self, other):
        # Check turn angle, and don't turn close to straight back.
        v_self = vec.vfrom(self.a, self.b)
        v_other = vec.vfrom(other.a, other.b)
        angle = math.degrees(vec.angle(v_self, v_other))
        if abs(angle) > MAX_TURN_ANGLE:
            raise ValueError('Turned too sharply.')

        # Special case equal widths.
        if float_equal(self.width, other.width):
            # When joints between segments of equal width are straight or
            # almost straight, the line-intersection method becomes very
            # numerically unstable, so we'll use another method instead.

            # For each segment, get a vector perpendicular to the
            # segment, then add them. This is an angle bisector for
            # the angle of the joint.
            w_self = self._width_vector()
            w_other = other._width_vector()
            v_bisect = vec.add(w_self, w_other)

            # Make the bisector have the correct length.
            half_angle = vec.angle(v_other, v_bisect)
            v_bisect = vec.norm(
                v_bisect,
                (self.width / 2) / math.sin(half_angle)
            )

            # Determine the left and right joint spots.
            self.b_left = vec.add(self.b, v_bisect)
            self.b_right = vec.sub(self.b, v_bisect)
            other.a_left = vec.add(other.a, v_bisect)
            other.a_right = vec.sub(other.a, v_bisect)
            return

        a, b = self.offset_line_left()
        c, d = other.offset_line_left()
        p_left = intersect_lines(a, b, c, d)

        a, b = self.offset_line_right()
        c, d = other.offset_line_right()
        p_right = intersect_lines(a, b, c, d)

        if p_left is None or p_right is None:
            raise ValueError('Joint not well defined.')

        self.b_left = other.a_left = p_left
        self.b_right = other.a_right = p_right

    def join_with_arc(self, other):
        a, b = self.offset_line_left()
        center, radius = other.offset_circle_left()
        points = intersect_circle_line(center, radius, a, b)
        self.b_left = other.a_left = closest_point_to(self.b, points)

        a, b = self.offset_line_right()
        center, radius = other.offset_circle_right()
        points = intersect_circle_line(center, radius, a, b)
        self.b_right = other.a_right = closest_point_to(self.b, points)

    # The offset_line_* functions create a copy of the centerline of a
    # segment, but offset to the right or left by half the segment width.

    def offset_line_left(self):
        w = self._width_vector()
        return (
            vec.add(self.a, w),
            vec.add(self.b, w),
        )

    def offset_line_right(self):
        w = vec.neg(self._width_vector())
        return (
            vec.add(self.a, w),
            vec.add(self.b, w),
        )

    def _width_vector(self):
        v = vec.vfrom(self.a, self.b)
        v = vec.perp(v)
        v = vec.norm(v, self.width / 2)
        return v

    def _heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))

    def draw_right(self, pen):
        pen.turn_to(self._heading())
        pen.line_to(self.b_right)

    def draw_left(self, pen):
        pen.turn_to(self._heading() + 180)
        pen.line_to(self.a_left)

    def set_start_angle(self, start_angle):
        self.start_angle = start_angle

        if self.width is None:
            return

        # Intersect the slant line with the left and right offset lines
        # to find the starting corners.
        if start_angle is None:
            v_slant = vec.perp(vec.vfrom(self.a, self.b))
        else:
            v_slant = vec.from_heading(math.radians(start_angle))
        a = self.a
        b = vec.add(self.a, v_slant)

        c, d = self.offset_line_left()
        self.a_left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        self.a_right = intersect_lines(a, b, c, d)

        if self.a_left is None or self.a_right is None:
            raise ValueError(
                'Could not set start angle of {}'.format(start_angle)
            )

        self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self.end_angle = end_angle

        if self.width is None:
            return

        # Intersect the slant line with the left and right offset lines
        # to find the ending corners.
        if end_angle is None:
            v_slant = vec.perp(vec.vfrom(self.a, self.b))
        else:
            v_slant = vec.from_heading(math.radians(end_angle))
        a = self.b
        b = vec.add(self.b, v_slant)

        c, d = self.offset_line_left()
        self.b_left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        self.b_right = intersect_lines(a, b, c, d)

        self.check_degenerate_segment()

    @staticmethod
    def calc_slant_width(stroke_width, slant):
        """
        The distance between the leading corners of the stroke can be longer if
        the stroke start is angled.
        """
        if slant == 0:
            raise ValueError('Slant angle is too steep')
        return stroke_width / math.sin(math.radians(slant))


class ArcSegment(Segment):

    repr_fields = [
        'a', 'b', 'width', 'start_angle', 'end_angle',
        'center', 'radius', 'start_heading', 'end_heading',
    ]

    def __init__(
        self, a, b, width, start_angle, end_angle,
        center, radius, arc_angle, start_heading, end_heading,
    ):
        super().__init__(a, b, width)

        self.arc_angle = arc_angle
        self.center = center
        self.radius = radius
        self._start_heading = start_heading
        self._end_heading = end_heading

        self.start_angle = None
        self.end_angle = None
        self.set_start_angle(start_angle)
        self.set_end_angle(end_angle)

    def join_with_line(self, other):
        a, b = other.offset_line_left()
        center, radius = self.offset_circle_left()
        points = intersect_circle_line(center, radius, a, b)
        self.b_left = other.a_left = closest_point_to(self.b, points)

        a, b = other.offset_line_right()
        center, radius = self.offset_circle_right()
        points = intersect_circle_line(center, radius, a, b)
        self.b_right = other.a_right = closest_point_to(self.b, points)

    def join_with_arc(self, other):
        c1, r1 = self.offset_circle_left()
        c2, r2 = other.offset_circle_left()
        points = intersect_circles(c1, r1, c2, r2)
        self.b_left = other.a_left = closest_point_to(self.b, points)

        c1, r1 = self.offset_circle_right()
        c2, r2 = other.offset_circle_right()
        points = intersect_circles(c1, r1, c2, r2)
        self.b_right = other.a_right = closest_point_to(self.b, points)

    # Since positive radius is defined as "left-arcing", and negative
    # radius is defined as "right-arcing", adding to or subtracting from
    # the radius will offset the curve to the right or left,
    # respectively.

    def offset_circle_left(self):
        return (
            self.center,
            self.radius - self.width / 2
        )

    def offset_circle_right(self):
        return (
            self.center,
            self.radius + self.width / 2,
        )

    @property
    def start_heading(self):
        return self._start_heading

    @property
    def end_heading(self):
        return self._end_heading

    def draw_right(self, pen):
        pen.turn_to(self.start_heading)
        pen.arc_to(self.b_right, self.center)

    def draw_left(self, pen):
        pen.turn_to(self.end_heading + 180)
        pen.arc_to(self.a_left, self.center)

    def set_start_angle(self, start_angle):
        self.start_angle = start_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.start_heading))
            v = vec.rotate(
                v,
                -math.radians(calc_slant(
                    self.start_heading,
                    start_angle,
                ))
            )

            center, radius = self.offset_circle_left()
            points = intersect_circle_line(
                center,
                radius,
                self.a,
                vec.add(self.a, v),
            )
            self.a_left = closest_point_to(self.a, points)

            center, radius = self.offset_circle_right()
            points = intersect_circle_line(
                center,
                radius,
                self.a,
                vec.add(self.a, v),
            )
            self.a_right = closest_point_to(self.a, points)

            self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self.end_angle = end_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.end_heading))
            v = vec.rotate(
                v,
                -math.radians(calc_slant(
                    self.end_heading,
                    end_angle,
                ))
            )

            center, radius = self.offset_circle_left()
            points = intersect_circle_line(
                center,
                radius,
                self.b,
                vec.add(self.b, v),
            )
            self.b_left = closest_point_to(self.b, points)

            center, radius = self.offset_circle_right()
            points = intersect_circle_line(
                center,
                radius,
                self.b,
                vec.add(self.b, v),
            )
            self.b_right = closest_point_to(self.b, points)

            self.check_degenerate_segment()
