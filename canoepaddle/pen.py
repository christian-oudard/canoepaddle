import math

import vec
from .paper import Paper
from .segment import LineSegment, ArcSegment
from .shape import Circle
from .point import Point
from .geometry import intersect_lines


def flip_angle_x(angle):
    if angle is not None:
        return 180 - angle


class Pen:

    def __init__(self, offset=(0, 0)):
        self.paper = Paper(offset)
        self._heading = 0
        self._position = (0.0, 0.0)
        self._width = None
        self.flipped_x = False

    def flip_x(self):
        """
        Make turns behave in the x-opposite manner.
        """
        self.flipped_x = not self.flipped_x

    def set_width(self, width):
        self._width = width

    def turn_to(self, heading):
        if self.flipped_x:
            heading = flip_angle_x(heading)
        self._heading = heading % 360

    def turn_toward(self, point):
        v = vec.vfrom(self._position, point)
        heading = math.degrees(vec.heading(v))
        self.turn_to(heading)

    def turn_left(self, angle):
        self.turn_to(self.heading + angle)

    def turn_right(self, angle):
        self.turn_left(-angle)

    def move_to(self, point):
        self._position = point

    def move_forward(self, distance):
        self._position = self._calc_forward_position(distance)

    def move_to_y(self, y_target):
        """
        Move forward in the current orientation, until the y coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_y(y_target)
        self.move_to(new_position)

    def move_to_x(self, x_target):
        """
        Move forward in the current orientation, until the x coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_x(x_target)
        self.move_to(new_position)

    def line_to(self, point, start_angle=None, end_angle=None):
        old_position = self._position
        self.move_to(point)

        if self.flipped_x:
            start_angle = flip_angle_x(start_angle)
            end_angle = flip_angle_x(end_angle)

        self.paper.add_segment(LineSegment(
            old_position,
            self.position,
            self.width,
            start_angle=start_angle,
            end_angle=end_angle,
        ))

    def line_forward(self, distance, start_angle=None, end_angle=None):
        self.line_to(
            self._calc_forward_position(distance),
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def line_to_y(self, y_target, start_angle=None, end_angle=None):
        """
        Draw a line, forward in the current orientation, until the y coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_y(y_target)
        self.line_to(
            new_position,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def line_to_x(self, x_target, start_angle=None, end_angle=None):
        """
        Draw a line, forward in the current orientation, until the x coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_x(x_target)
        self.line_to(
            new_position,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def _arc(self, center, radius, endpoint, arc_angle):
        old_position = self._position
        old_heading = self._heading
        self.move_to(endpoint)
        self.turn_left(arc_angle)

        self.paper.add_segment(ArcSegment(
            a=old_position,
            b=endpoint,
            width=self.width,
            center=center,
            radius=radius,
            arc_angle=arc_angle,
            start_heading=old_heading,
            end_heading=self._heading,
        ))

    def arc_left(self, arc_angle, radius):
        # Create a radius vector, which is a vector from the arc center to the
        # current position. Subtract to find the center, then rotate the radius
        # vector to find the arc end point.
        v_radius = vec.neg(vec.perp(self._vector(radius)))
        center = vec.sub(self._position, v_radius)
        endpoint = vec.add(center, vec.rotate(v_radius, math.radians(arc_angle)))

        self._arc(center, radius, endpoint, arc_angle)

    def arc_right(self, arc_angle, radius):
        self.arc_left(-arc_angle, -radius)

    def arc_to(self, endpoint, center=None):
        """
        Draw an arc ending at the specified point, starting tangent to the
        current position and heading.
        """
        # Handle unspecified center.
        # We need to find the center of the arc, so we can find its radius. The
        # center of this arc is uniquely defined by the intersection of two
        # lines:
        # 1. The first line is perpendicular to the pen heading, passing
        #    through the pen position.
        # 2. The second line is the perpendicular bisector of the pen position
        #    and the target arc end point.
        v_pen = self._vector()
        v_perp = vec.perp(self._vector())
        if center is None:
            midpoint = vec.div(vec.add(self._position, endpoint), 2)
            v_bisector = vec.perp(vec.vfrom(self._position, endpoint))
            center = intersect_lines(
                self._position,
                vec.add(self._position, v_perp),
                midpoint,
                vec.add(midpoint, v_bisector),
            )

        # Calculate the arc angle.
        # Construct two radii, one for the start and end of the arc, and find
        # the angle between them. Check some dot products to determine which
        # quadrant the arc angle is in.
        v_radius_start = vec.vfrom(center, self._position)
        v_radius_end = vec.vfrom(center, endpoint)
        arc_angle = math.degrees(vec.angle(v_radius_start, v_radius_end))
        if vec.dot(v_radius_end, v_pen) < 0:
            arc_angle += 180
        if vec.dot(v_radius_start, v_perp) > 0:
            arc_angle = -arc_angle

        # Determine start heading. This may not be the same as the original pen
        # heading if the "center" argument is specified.
        start_heading = vec.heading(vec.perp(v_radius_start))
        if arc_angle < 0:
            start_heading = (start_heading + 180) % 360

        self._arc(center, vec.mag(v_radius_start), endpoint, arc_angle)

    def circle(self, radius):
        self.paper.add_shape(Circle(
            center=self._position,
            radius=radius,
        ))

    def last_slant_width(self):
        return self.paper.strokes[-1][-1].end_slant_width()

    @property
    def position(self):
        return Point(*self._position)

    @property
    def heading(self):
        if self.flipped_x:
            return flip_angle_x(self._heading)
        return self._heading

    @property
    def width(self):
        return self._width

    def _vector(self, length=1):
        """
        Create a vector pointing in the same direction as the pen, with the
        specified length.
        """
        return vec.from_heading(math.radians(self._heading), length)

    def _calc_forward_position(self, distance):
        return vec.add(
            self.position,
            self._vector(distance),
        )

    def _calc_forward_to_y(self, y_target):
        x, y = self.position
        y_diff = y_target - y
        x_diff = y_diff / math.tan(math.radians(self._heading))
        return vec.add(self.position, (x_diff, y_diff))

    def _calc_forward_to_x(self, x_target):
        x, y = self.position
        x_diff = x_target - x
        y_diff = x_diff * math.tan(math.radians(self._heading))
        return vec.add(self.position, (x_diff, y_diff))
