#TODO Maybe we can make set_end_angle just set the b_left and b_right
# directly. Do we even need to keep around the end angle?

import math

import vec
from .point import Point, points_equal
from .geometry import intersect_lines, intersect_circle_line


MAX_TURN_ANGLE = 179


def closest_point_to(target, points):
    return min(
        points,
        key=lambda p: vec.mag2(vec.vfrom(target, p))
    )


class Segment:
    def join_with(self, other):
        if self.width is None or other.width is None:
            return

        if other.is_line():
            self.join_with_line(other)
        elif other.is_arc():
            self.join_with_arc(other)

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
        return slant

    def check_degenerate_segment(self):
        #TODO: make this check go off of a_left, a_right, etc. directly instead.
        if (
            not hasattr(self, '_start_angle') or
            not hasattr(self, '_end_angle')
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

    def __init__(self, a, b, width, start_angle, end_angle):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width

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

    def is_line(self):
        return True

    def is_arc(self):
        return False

    def join_with_line(self, other):
        v_self = vec.vfrom(self.a, self.b)
        v_other = vec.vfrom(other.a, other.b)
        angle = math.degrees(vec.angle(v_self, v_other))
        if abs(angle) > MAX_TURN_ANGLE:
            raise ValueError('Turned too sharply.')

        # Left side.
        a, b = self.offset_line_left()
        c, d = other.offset_line_left()
        if points_equal(b, c):
            p = b
        else:
            p = intersect_lines(a, b, c, d)
        self.b_left = other.a_left = p

        # Right side.
        a, b = self.offset_line_right()
        c, d = other.offset_line_right()
        if points_equal(b, c):
            p = b
        else:
            p = intersect_lines(a, b, c, d)
        assert p is not None
        self.b_right = other.a_right = p

    def join_with_arc(self, other):
        raise NotImplementedError

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

    def draw_right(self, pen):
        pen.turn_to(self.start_heading)
        pen.line_to(self.b_right)

    def draw_left(self, pen):
        pen.turn_to(self.end_heading + 180)
        pen.line_to(self.a_left)

    def set_start_angle(self, start_angle):
        self._start_angle = start_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.start_heading))
            v = vec.rotate(
                v,
                -math.radians(self.calc_slant(
                    self.start_heading,
                    start_angle,
                ))
            )
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
        if slant == 0:
            raise ValueError('Slant angle is too steep')
        return stroke_width / math.sin(math.radians(slant))


class ArcSegment(Segment):
    def __init__(
        self, a, b, width, start_angle, end_angle,
        center, radius, arc_angle, start_heading, end_heading,
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

    def is_line(self):
        return False

    def is_arc(self):
        return True

    def join_with_line(self, other):
        raise NotImplementedError

    def join_with_arc(self, other):
        raise NotImplementedError

    @property
    def start_heading(self):
        return self._start_heading

    @property
    def end_heading(self):
        return self._end_heading

    def start_slant_width(self):
        # Do these need to exist?
        return self.width

    def end_slant_width(self):
        return self.width

    def draw_right(self, pen):
        pen.turn_to(self.start_heading)
        pen.arc_to(self.b_right, self.center)

    def draw_left(self, pen):
        pen.turn_to(self.end_heading + 180)
        pen.arc_to(self.a_left, self.center)

    def set_start_angle(self, start_angle):
        self._start_angle = start_angle
        if self.width is not None:
            v = vec.from_heading(math.radians(self.start_heading))
            v = vec.rotate(
                v,
                -math.radians(self.calc_slant(
                    self.start_heading,
                    start_angle,
                ))
            )
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
