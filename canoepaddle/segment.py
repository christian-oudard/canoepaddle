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
from .heading import Heading, Angle

MAX_TURN_ANGLE = 170


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

        self.start_joint_illegal = False
        self.end_joint_illegal = False

        self.start_slant = None
        self.end_slant = None
        if self.can_set_slant():
            self.set_slants(start_slant, end_slant)

        self.start_cap = flat_cap
        self.end_cap = flat_cap

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
                return p.flipped_x(x_center)

        def f_heading(heading):
            if heading is not None:
                return heading.flipped_x()

        self._mirror(f, f_heading)

    def mirror_y(self, y_center):

        def f(p):
            if p is not None:
                return p.flipped_y(y_center)

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
            [self.a_left, self.a_right, self.b_left, self.b_right]
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
                self.start_joint_illegal = True
                self.end_joint_illegal = True

    def can_set_slant(self):
        return (
            self.width is not None
            and not points_equal(self.a, self.b)
        )


class LineSegment(Segment):

    repr_fields = ['a', 'b', 'start_slant', 'end_slant']

    @property
    def heading(self):
        return Heading.from_rad(vec.heading(vec.vfrom(self.a, self.b)))
    start_heading = heading
    end_heading = heading

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
        v_self = self._vector()
        v_other = other._vector()

        # Check turn angle.
        self_heading = Heading.from_rad(vec.heading(v_self))
        other_heading = Heading.from_rad(vec.heading(v_other))
        turn_angle = self_heading.angle_to(other_heading)

        # Special case equal widths.
        if(
            abs(turn_angle) <= MAX_TURN_ANGLE
            and float_equal(self.width, other.width)
        ):
            # When joints between segments of equal width are straight or
            # almost straight, the line-intersection method becomes very
            # numerically unstable, so use another method instead.

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
            p_left = vec.add(self.b, v_bisect)
            p_right = vec.sub(self.b, v_bisect)
        else:
            a, b = self.offset_line_left()
            c, d = other.offset_line_left()
            p_left = intersect_lines(a, b, c, d)

            a, b = self.offset_line_right()
            c, d = other.offset_line_right()
            p_right = intersect_lines(a, b, c, d)

        # Make sure the joint points are "forward" from the perspective
        # of each segment.
        if p_left is not None:
            if vec.dot(vec.vfrom(self.a_left, p_left), v_self) < 0:
                p_left = None
        if p_right is not None:
            if vec.dot(vec.vfrom(self.a_right, p_right), v_self) < 0:
                p_right = None

        # Don't join the outer sides if the turn angle is too steep.
        if abs(turn_angle) > MAX_TURN_ANGLE:
            if turn_angle > 0:
                p_right = None
            else:
                p_left = None

        if p_left is not None:
            self.b_left = other.a_left = Point(*p_left)
        if p_right is not None:
            self.b_right = other.a_right = Point(*p_right)

        if p_left is None or p_right is None:
            self.end_joint_illegal = True
            other.start_joint_illegal = True

    def join_with_arc(self, other):
        a, b = self.offset_line_left()
        center, radius = other.offset_circle_left()
        points_left = intersect_circle_line(center, radius, a, b)
        if len(points_left) > 0:
            p = Point(*closest_point_to(self.b, points_left))
            self.b_left = other.a_left = p

        a, b = self.offset_line_right()
        center, radius = other.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)
        if len(points_right) > 0:
            p = Point(*closest_point_to(self.b, points_right))
            self.b_right = other.a_right = p

        if len(points_left) == 0 or len(points_right) == 0:
            self.end_joint_illegal = True
            other.start_joint_illegal = True

    def set_slants(self, start_slant, end_slant):
        if start_slant is not None:
            start_slant = Heading(start_slant)
        if end_slant is not None:
            end_slant = Heading(end_slant)

        self.start_slant = start_slant
        self.end_slant = end_slant

        # Intersect the slant lines with the left and right offset lines
        # to find the corners.
        line_left = self.offset_line_left()
        line_right = self.offset_line_right()

        # Start corners.
        if start_slant is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(start_slant.rad)
        a = self.a
        b = vec.add(self.a, v_slant)

        left = intersect_lines(a, b, line_left[0], line_left[1])
        right = intersect_lines(a, b, line_right[0], line_right[1])

        if left is None or right is None:
            self.start_joint_illegal = True
        else:
            self.a_left = Point(*left)
            self.a_right = Point(*right)

        # End corners.
        if end_slant is None:
            v_slant = vec.perp(self._vector())
        else:
            v_slant = vec.from_heading(end_slant.rad)
        a = self.b
        b = vec.add(self.b, v_slant)

        left = intersect_lines(a, b, line_left[0], line_left[1])

        right = intersect_lines(a, b, line_right[0], line_right[1])

        if left is None or right is None:
            self.end_joint_illegal = True
        else:
            self.b_left = Point(*left)
            self.b_right = Point(*right)

        # Done, make sure we didn't cross
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
        self.arc_angle = Angle(arc_angle)
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
        if self.arc_angle < 0:
            start = self.end_heading + 90
            end = self.start_heading + 90
        else:
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

    def copy(self):
        other = super().copy()
        other.arc_angle = self.arc_angle.copy()
        other.center = Point(*self.center)
        other.radius = self.radius
        other.start_heading = self.start_heading.copy()
        other.end_heading = self.end_heading.copy()
        return other

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
        points_left = intersect_circle_line(center, radius, a, b)
        if len(points_left) > 0:
            p = Point(*closest_point_to(self.b, points_left))
            self.b_left = other.a_left = p

        a, b = other.offset_line_right()
        center, radius = self.offset_circle_right()
        points_right = intersect_circle_line(center, radius, a, b)
        if len(points_right) > 0:
            p = Point(*closest_point_to(self.b, points_right))
            self.b_right = other.a_right = p

        if len(points_left) == 0 or len(points_right) == 0:
            self.end_joint_illegal = True
            other.start_joint_illegal = True

    def join_with_arc(self, other):
        # Special case coincident arcs.
        if points_equal(self.center, other.center):
            if not (
                float_equal(self.radius, other.radius)
                and float_equal(self.width, other.width)
            ):
                self.end_joint_illegal = True
                other.start_joint_illegal = True
                return

            r = vec.vfrom(self.center, self.b)
            if self.radius < 0:
                r = vec.neg(r)
            v_left = vec.norm(r, self.radius - self.width / 2)
            self.b_left = other.a_left = Point(*vec.add(self.center, v_left))
            v_right = vec.norm(r, self.radius + self.width / 2)
            self.b_right = other.a_right = Point(*vec.add(self.center, v_right))
            return

        c1, r1 = self.offset_circle_left()
        c2, r2 = other.offset_circle_left()
        points_left = intersect_circles(c1, r1, c2, r2)
        if len(points_left) > 0:
            p = Point(*closest_point_to(self.b, points_left))
            self.b_left = other.a_left = p

        c1, r1 = self.offset_circle_right()
        c2, r2 = other.offset_circle_right()
        points_right = intersect_circles(c1, r1, c2, r2)
        if len(points_right) > 0:
            p = Point(*closest_point_to(self.b, points_right))
            self.b_right = other.a_right = p

        if len(points_left) == 0 or len(points_right) == 0:
            self.end_joint_illegal = True
            other.start_joint_illegal = True

    def set_slants(self, start_slant, end_slant):
        if start_slant is not None:
            start_slant = Heading(start_slant)
        if end_slant is not None:
            end_slant = Heading(end_slant)

        self.start_slant = start_slant
        self.end_slant = end_slant

        # Intersect the slant lines with the left and right offset circles
        # to find the corners.
        center_left, radius_left = self.offset_circle_left()
        center_right, radius_right = self.offset_circle_right()

        # Start corners.
        if start_slant is None:
            v_slant = vec.vfrom(self.center, self.a)
        else:
            v_slant = vec.from_heading(start_slant.rad)
        a = self.a
        b = vec.add(self.a, v_slant)

        points_left = intersect_circle_line(center_left, radius_left, a, b)
        points_right = intersect_circle_line(center_right, radius_right, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            self.start_joint_illegal = True
            return

        self.a_left = Point(*closest_point_to(self.a, points_left))
        self.a_right = Point(*closest_point_to(self.a, points_right))

        # End corners.
        if end_slant is None:
            v_slant = vec.vfrom(self.center, self.b)
        else:
            v_slant = vec.from_heading(end_slant.rad)
        a = self.b
        b = vec.add(self.b, v_slant)

        points_left = intersect_circle_line(center_left, radius_left, a, b)
        points_right = intersect_circle_line(center_right, radius_right, a, b)

        if len(points_left) == 0 or len(points_right) == 0:
            self.end_joint_illegal = True
            return

        self.b_left = Point(*closest_point_to(self.b, points_left))
        self.b_right = Point(*closest_point_to(self.b, points_right))

        self.check_degenerate_segment()

    def offset_circle_left(self):
        # Since positive radius is defined as "left-arcing", and negative
        # radius is defined as "right-arcing", subtracting from the radius
        # offsets the curve to the left, and adding to the radius offsets it to
        # the right.
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


def flat_cap(pen, end):
    pen.line_to(end)
