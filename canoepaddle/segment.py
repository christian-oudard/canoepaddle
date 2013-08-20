import math
from copy import copy

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
    closest_point_to,
)
from .heading import Heading
from .error import SegmentError


MAX_TURN_ANGLE = 175


class Segment:
    def __init__(self, a, b, width, color, start_slant, end_slant):
        self.a = Point(*a)
        self.b = Point(*b)
        self.width = width
        self.color = color

        self.a_left = None
        self.a_right = None
        self.b_left = None
        self.b_right = None

        self.start_slant = None
        self.end_slant = None
        self.set_start_slant(start_slant)
        self.set_end_slant(end_slant)

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

    def copy(self):
        return copy(self)

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
                new_x = x_center - p.x
                return Point(x_center + new_x, p.y)

        def f_heading(heading):
            if heading is not None:
                return heading.flipped_x()

        self._mirror(f, f_heading)

    def mirror_y(self, y_center):

        def f(p):
            if p is not None:
                new_y = y_center - p.y
                return Point(p.x, y_center + new_y)

        def f_heading(heading):
            if heading is not None:
                return heading.flipped_y()

        self._mirror(f, f_heading)

    def _mirror(self, f, f_heading):
        self.a = f(self.a)
        self.b = f(self.b)
        # The corners need to be swapped left for right as they are
        # mirrored, to maintain counterclockwise thick segment drawing
        # order.
        self.a_left, self.a_right = f(self.a_right), f(self.a_left)
        self.b_left, self.b_right = f(self.b_right), f(self.b_left)

        self.start_slant = f_heading(self.start_slant)
        self.end_slant = f_heading(self.end_slant)

    def reverse(self):
        self.a, self.b = self.b, self.a
        self.a_left, self.b_right = self.b_right, self.a_left
        self.a_right, self.b_left = self.b_left, self.a_right

    def join_with(self, other):
        assert points_equal(self.b, other.a)

        if not self.width:
            return

        try:
            if isinstance(other, LineSegment):
                self.join_with_line(other)
            elif isinstance(other, ArcSegment):
                self.join_with_arc(other)
        except SegmentError:
            #TODO: Make it work somehow if the joint is too sharp.
            raise

    def fused_with(self, other):
        """
        Create a segment that is equivalent to self and other fused together.
        """
        seg = LineSegment(
            a=self.a,
            b=other.b,
            width=self.width,
            color=self.color,
            start_slant=self.start_slant,
            end_slant=other.end_slant,
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
        if intersection is not None:
            if not any(points_equal(p, intersection) for p in [
                self.a_left,
                self.a_right,
                self.b_left,
                self.b_right,
            ]):
                raise SegmentError('Degenerate segment, endcaps cross each other.')

    def can_set_angle(self):
        return (
            self.width is not None and
            not points_equal(self.a, self.b)
        )


class LineSegment(Segment):

    repr_fields = ['a', 'b', 'start_slant', 'end_slant']

    def bounds(self):
        if self.width is None:
            endpoints = [self.a, self.b]
        else:
            endpoints = [self.a_left, self.a_right, self.b_left, self.b_right]
        return Bounds.union_all([Bounds.from_point(p) for p in endpoints])

    def reverse(self):
        self.start_slant, self.end_slant = self.end_slant, self.start_slant
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

    def set_start_slant(self, start_slant):
        if start_slant is not None:
            start_slant = Heading(start_slant)
        self.start_slant = start_slant

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset lines
        # to find the starting corners.
        if start_slant is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(start_slant.rad)
        a = self.a
        b = vec.add(self.a, v_slant)

        c, d = self.offset_line_left()
        left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        right = intersect_lines(a, b, c, d)

        if left is None or right is None:
            raise SegmentError(
                'Could not set start slant to {}'.format(start_slant)
            )

        self.a_left = Point(*left)
        self.a_right = Point(*right)

        self.check_degenerate_segment()

    def set_end_slant(self, end_slant):
        if end_slant is not None:
            end_slant = Heading(end_slant)
        self.end_slant = end_slant

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset lines
        # to find the ending corners.
        if end_slant is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(end_slant.rad)
        a = self.b
        b = vec.add(self.b, v_slant)

        c, d = self.offset_line_left()
        left = intersect_lines(a, b, c, d)

        c, d = self.offset_line_right()
        right = intersect_lines(a, b, c, d)

        if left is None or right is None:
            raise SegmentError(
                'Could not set end slant to {}'.format(end_slant)
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
        pen.line_to(self.b_right)

    def draw_left(self, pen):
        pen.line_to(self.a_left)


class ArcSegment(Segment):

    repr_fields = [
        'a', 'b', 'start_slant', 'end_slant',
        'center', 'radius', 'start_heading', 'end_heading',
    ]

    def __init__(
        self, a, b, width, color, start_slant, end_slant,
        center, radius, arc_angle, start_heading, end_heading,
    ):
        self.arc_angle = arc_angle
        self.center = Point(*center)
        self.radius = radius
        self.start_heading = start_heading
        self.end_heading = end_heading
        super().__init__(a, b, width, color, start_slant, end_slant)

    def bounds(self):
        # We use the outside radius, because the inside of the arc cannot be
        # tangent to the boundary. This is not a perfect approximation, as
        # setting end slants could fail to shrink the bounding box as
        # they should.
        r = abs(self.radius)
        if self.width is not None:
            r += self.width / 2

        # Find the four "compass points" around the center.
        compass_points = [
            vec.add(self.center, direction)
            for direction in [
                (r, 0),  # East, heading = 0.
                (0, r),  # North, heading = 90.
                (-r, 0),  # West, heading = 180.
                (0, -r),  # South, heading = 270.
            ]
        ]

        # Check which compass points are in the body of the circle.
        start = self.start_heading - 90
        end = self.end_heading - 90
        occupied_points = []
        for i, h in enumerate([0, 90, 180, 270]):
            h = Heading(h)
            if h == start or h == end or h.between(start, end):
                occupied_points.append(compass_points[i])

        # The bounding box of the arc is the combined bounding box of the start
        # point, the end point, and the compass points occupied by the body of
        # the arc. If the arc is a thick arc, then the edge points also can
        # push the boundary.
        if self.width is None:
            endpoints = [self.a, self.b]
        else:
            endpoints = [self.a_left, self.a_right, self.b_left, self.b_right]

        return Bounds.union_all([
            Bounds.from_point(p) for p in
            endpoints + occupied_points
        ])

    def _translate(self, f):
        super()._translate(f)
        self.center = f(self.center)

    def _mirror(self, f, f_heading):
        super()._mirror(f, f_heading)
        self.center = f(self.center)
        self.arc_angle = -self.arc_angle
        self.radius = -self.radius
        self.start_heading = f_heading(self.start_heading)
        self.end_heading = f_heading(self.end_heading)

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

    def set_start_slant(self, start_slant):
        if start_slant is not None:
            start_slant = Heading(start_slant)
        self.start_slant = start_slant

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset circles
        # to find the starting corners.
        if start_slant is None:
            v_slant = vec.vfrom(self.center, self.a)
        else:
            v_slant = vec.from_heading(start_slant.rad)
        a = self.a
        b = vec.add(self.a, v_slant)

        center, radius = self.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)

        center, radius = self.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            raise SegmentError(
                'Could not set start slant to {}'.format(start_slant)
            )

        self.a_left = Point(*closest_point_to(self.a, points_left))
        self.a_right = Point(*closest_point_to(self.a, points_right))

        self.check_degenerate_segment()

    def set_end_slant(self, end_slant):
        if end_slant is not None:
            end_slant = Heading(end_slant)
        self.end_slant = end_slant

        if not self.can_set_angle():
            return

        # Intersect the slant line with the left and right offset circles
        # to find the ending corners.
        if end_slant is None:
            v_slant = vec.vfrom(self.center, self.b)
        else:
            v_slant = vec.from_heading(end_slant.rad)
        a = self.b
        b = vec.add(self.b, v_slant)

        center, radius = self.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)

        center, radius = self.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            raise SegmentError(
                'Could not set end slant to {}'.format(end_slant)
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
