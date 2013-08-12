import math

import vec
from .point import (
    Point,
    float_equal,
    points_equal,
)
from .bounds import Bounds
from .geometry import (
    intersect_lines,
    intersect_circle_line,
    intersect_circles,
)
from .error import SegmentError


MAX_TURN_ANGLE = 179


def closest_point_to(target, points):
    return min(
        points,
        key=lambda p: vec.mag2(vec.vfrom(target, p))
    )


class Segment:
    def __init__(self, a, b, width, color, start_angle, end_angle):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.color = color

        self.a_left = None
        self.a_right = None
        self.b_left = None
        self.b_right = None

        self.start_angle = None
        self.end_angle = None
        self.set_start_angle(start_angle)
        self.set_end_angle(end_angle)

    def __iter__(self):
        yield self.a
        yield self.b

    def __repr__(self):
        strings = []
        for field in self.repr_fields:
            value = getattr(self, field)
            if value is None:
                continue
            strings.append('{}={}'.format(field, value))
        return '{}({})'.format(self.__class__.__name__, ', '.join(strings))

    def translate(self, offset):

        def f(p):
            if p is not None:
                return Point(*vec.add(p, offset))

        self._translate(f)

    def _translate(self, f):
        self.a = f(self.a)
        self.b = f(self.b)
        self.a_left = f(self.a_left)
        self.a_right = f(self.a_right)
        self.b_left = f(self.b_left)
        self.b_right = f(self.b_right)

    def mirror_x(self, x_center):

        def f(p):
            if p is not None:
                return Point(x_center - p.x, p.y)

        def f_angle(angle):
            if angle is not None:
                return 180 - angle

        self._mirror(f, f_angle)

    def mirror_y(self, y_center):

        def f(p):
            if p is not None:
                return Point(p.x, y_center - p.y)

        def f_angle(angle):
            if angle is not None:
                return -angle

        self._mirror(f, f_angle)

    def _mirror(self, f, f_angle):
        self.a = f(self.a)
        self.b = f(self.b)
        # The corners need to be swapped left for right as they are
        # mirrored, to maintain counterclockwise thick segment drawing
        # order.
        self.a_left, self.a_right = f(self.a_right), f(self.a_left)
        self.b_left, self.b_right = f(self.b_right), f(self.b_left)

    def reverse(self):
        self.a, self.b = self.b, self.a
        self.a_left, self.b_right = self.b_right, self.a_left
        self.a_right, self.b_left = self.b_left, self.a_right

    def join_with(self, other):
        assert points_equal(self.b, other.a)

        if not self.width:
            return

        if isinstance(other, LineSegment):
            self.join_with_line(other)
        elif isinstance(other, ArcSegment):
            self.join_with_arc(other)

    def fused_with(self, other):
        """
        Create a segment that is equivalent to self and other fused together.
        """
        seg = LineSegment(
            a=self.a,
            b=other.b,
            width=self.width,
            color=self.color,
            start_angle=self.start_angle,
            end_angle=other.end_angle,
        )
        seg.a_left = self.a_left
        seg.a_right = self.a_right
        seg.b_left = other.b_left
        seg.b_right = other.b_right
        return seg

    def check_degenerate_segment(self):
        if any(
            p is None for p in
            [self.a_left, self.a_right, self.b_left, self.b_right],
        ):
            return

        # Check whether the endcap lines intersect. If so, this will cause
        # graphical glitches when drawing the segment, unless the intersection
        # is one of the endpoints.
        intersection = intersect_lines(
            self.a_left, self.a_right,
            self.b_left, self.b_right,
            segment=True,
        )
        if intersection not in [
            None,
            self.a_left,
            self.a_right,
            self.b_left,
            self.b_right,
        ]:
            raise SegmentError('Degenerate segment, endcaps cross each other.')

    def can_set_angle(self):
        return (
            self.width is not None and
            not points_equal(self.a, self.b)
        )


class LineSegment(Segment):

    repr_fields = ['a', 'b', 'start_angle', 'end_angle']

    def bounds(self):
        return Bounds.union_all([
            Bounds.from_point(self.a),
            Bounds.from_point(self.b),
        ])

    def reverse(self):
        self.start_angle, self.end_angle = self.end_angle, self.start_angle
        super().reverse()

    def join_with_line(self, other):
        # Check turn angle, and don't turn close to straight back.
        v_self = self._vector()
        v_other = other._vector()
        angle = math.degrees(vec.angle(v_self, v_other))
        if abs(angle) > MAX_TURN_ANGLE:
            raise SegmentError('Turned too sharply.')

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
            self.b_left = Point(*vec.add(self.b, v_bisect))
            self.b_right = Point(*vec.sub(self.b, v_bisect))
            other.a_left = Point(*vec.add(other.a, v_bisect))
            other.a_right = Point(*vec.sub(other.a, v_bisect))
            return

        a, b = self.offset_line_left()
        c, d = other.offset_line_left()
        p_left = intersect_lines(a, b, c, d)

        a, b = self.offset_line_right()
        c, d = other.offset_line_right()
        p_right = intersect_lines(a, b, c, d)

        if p_left is None or p_right is None:
            raise SegmentError('Joint not allowed.')

        self.b_left = other.a_left = Point(*p_left)
        self.b_right = other.a_right = Point(*p_right)

    def join_with_arc(self, other):
        a, b = self.offset_line_left()
        center, radius = other.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)

        a, b = self.offset_line_right()
        center, radius = other.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)

        self.b_left = other.a_left = Point(*closest_point_to(self.b, points_left))
        self.b_right = other.a_right = Point(*closest_point_to(self.b, points_right))

    def set_start_angle(self, start_angle):
        self.start_angle = start_angle

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset lines
        # to find the starting corners.
        if start_angle is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(math.radians(start_angle))
        a = self.a
        b = vec.add(self.a, v_slant)

        c, d = self.offset_line_left()
        left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        right = intersect_lines(a, b, c, d)

        if left is None or right is None:
            raise SegmentError(
                'Could not set start angle to {}'.format(start_angle)
            )

        self.a_left = Point(*left)
        self.a_right = Point(*right)

        self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self.end_angle = end_angle

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset lines
        # to find the ending corners.
        if end_angle is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(math.radians(end_angle))
        a = self.b
        b = vec.add(self.b, v_slant)

        c, d = self.offset_line_left()
        left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        right = intersect_lines(a, b, c, d)

        if left is None or right is None:
            raise SegmentError(
                'Could not set end angle to {}'.format(end_angle)
            )

        self.b_left = Point(*left)
        self.b_right = Point(*right)

        self.check_degenerate_segment()

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

    def _vector(self):
        return vec.vfrom(self.a, self.b)

    def _width_vector(self):
        v = self._vector()
        v = vec.perp(v)
        v = vec.norm(v, self.width / 2)
        return v

    def draw_right(self, pen):
        #pen.turn_to(self._heading())
        pen.line_to(self.b_right)

    def draw_left(self, pen):
        #pen.turn_to(self._heading() + 180)
        pen.line_to(self.a_left)

    def _heading(self):
        return math.degrees(vec.heading(self._vector()))


class ArcSegment(Segment):

    repr_fields = [
        'a', 'b', 'start_angle', 'end_angle',
        'center', 'radius', 'start_heading', 'end_heading',
    ]

    def __init__(
        self, a, b, width, color, start_angle, end_angle,
        center, radius, arc_angle, start_heading, end_heading,
    ):
        self.arc_angle = arc_angle
        self.center = Point(*center)
        self.radius = radius
        self.start_heading = start_heading
        self.end_heading = end_heading
        super().__init__(a, b, width, color, start_angle, end_angle)

    def bounds(self):
        # Find the four "compass points" around the center.
        r = abs(self.radius)
        compass_points = [
            vec.add(self.center, direction)
            for direction in [
                (r, 0),  # East, heading = 0.
                (0, r),  # North, heading = 90.
                (-r, 0),  # West, heading = 180.
                (0, -r),  # South, heading = 270.
            ]
        ]

        # Check which compass points are in the body of the circle. We need to
        # know what "clock hand angle" the start and end of the arc are, in the
        # range (0 <= angle < 360). Keep the end angle larger than the start
        # angle.
        start = self.start_heading - 90
        end = self.end_heading - 90
        start = start % 360
        end = end % 360
        if end < start:
            end += 360
        assert 0 <= start < 360
        assert start <= end < start + 360

        # Find the compass points in the angular range from the start to the
        # end of the arc. We have to check two full rotations worth, because
        # the end of the range could reach up to 720 degrees.
        occupied_points = []
        for i, angle in enumerate(range(0, 720, 90)):
            if start <= angle <= end:
                occupied_points.append(compass_points[i % 4])

        # The bounding box of the arc is the combined bounding box of the start
        # point, the end point, and the compass points occupied by the body of
        # the arc.
        return Bounds.union_all([
            Bounds.from_point(p) for p in
            [self.a, self.b] + occupied_points
        ])

    def _translate(self, f):
        super()._translate(f)
        self.center = f(self.center)

    def _mirror(self, f, f_angle):
        super()._mirror(f, f_angle)
        self.center = f(self.center)
        self.arc_angle = -self.arc_angle
        self.radius = -self.radius
        self.start_heading = f_angle(self.start_heading)
        self.end_heading = f_angle(self.end_heading)

    def join_with_line(self, other):
        a, b = other.offset_line_left()
        center, radius = self.offset_circle_left()
        points = intersect_circle_line(center, radius, a, b)
        self.b_left = other.a_left = Point(*closest_point_to(self.b, points))

        a, b = other.offset_line_right()
        center, radius = self.offset_circle_right()
        points = intersect_circle_line(center, radius, a, b)
        self.b_right = other.a_right = Point(*closest_point_to(self.b, points))

    def join_with_arc(self, other):
        # Special case coincident arcs.
        if points_equal(self.center, other.center):
            if (
                float_equal(self.radius, other.radius) and
                float_equal(self.width, other.width)
            ):
                r = vec.vfrom(self.center, self.b)
                if self.radius < 0:
                    r = vec.neg(r)
                v_left = vec.norm(r, self.radius - self.width / 2)
                self.b_left = other.a_left = Point(*vec.add(self.center, v_left))
                v_right = vec.norm(r, self.radius + self.width / 2)
                self.b_right = other.a_right = Point(*vec.add(self.center, v_right))
                return
            else:
                raise SegmentError(
                    'Joint not allowed, coincident arcs without equal '
                    'widths or radii.'
                )

        c1, r1 = self.offset_circle_left()
        c2, r2 = other.offset_circle_left()
        points_left = intersect_circles(c1, r1, c2, r2)

        c1, r1 = self.offset_circle_right()
        c2, r2 = other.offset_circle_right()
        points_right = intersect_circles(c1, r1, c2, r2)

        if len(points_left) == 0 or len(points_right) == 0:
            raise SegmentError('Joint not allowed.')

        self.b_left = other.a_left = Point(*closest_point_to(self.b, points_left))
        self.b_right = other.a_right = Point(*closest_point_to(self.b, points_right))

    def set_start_angle(self, start_angle):
        self.start_angle = start_angle

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset circles
        # to find the starting corners.
        if start_angle is None:
            v_slant = vec.vfrom(self.center, self.a)
        else:
            v_slant = vec.from_heading(math.radians(start_angle))
        a = self.a
        b = vec.add(self.a, v_slant)

        center, radius = self.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)

        center, radius = self.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            raise SegmentError(
                'Could not set start angle to {}'.format(start_angle)
            )

        self.a_left = Point(*closest_point_to(self.a, points_left))
        self.a_right = Point(*closest_point_to(self.a, points_right))

        self.check_degenerate_segment()

    def set_end_angle(self, end_angle):
        self.end_angle = end_angle

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset circles
        # to find the ending corners.
        if end_angle is None:
            v_slant = vec.vfrom(self.center, self.b)
        else:
            v_slant = vec.from_heading(math.radians(end_angle))
        a = self.b
        b = vec.add(self.b, v_slant)

        center, radius = self.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)

        center, radius = self.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            raise SegmentError(
                'Could not set end angle to {}'.format(end_angle)
            )

        self.b_left = Point(*closest_point_to(self.b, points_left))
        self.b_right = Point(*closest_point_to(self.b, points_right))

        self.check_degenerate_segment()

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

    def draw_right(self, pen):
        pen.turn_to(self.start_heading)
        pen.arc_to(self.b_right, self.center)

    def draw_left(self, pen):
        pen.turn_to(self.end_heading + 180)
        pen.arc_to(self.a_left, self.center)
