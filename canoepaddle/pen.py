import math

import vec
from .paper import Paper
from .path import Path
from .segment import LineSegment, ArcSegment
from .shape import Circle, Rectangle
from .point import Point, points_equal
from .geometry import intersect_lines


class Pen:

    def __init__(self):
        self.paper = Paper()
        self._heading = 0
        self._position = Point(0.0, 0.0)
        self._width = None
        self._color = (0.0, 0.0, 0.0)
        self.flipped_x = False
        self.flipped_y = False

        self._current_path = None

        # Debug switches.
        self.show_joints = False
        self.show_nodes = False
        self.show_bones = False

    # Properties.

    @property
    def position(self):
        return Point(*self._position)

    @property
    def heading(self):
        if self.flipped_x:
            return flip_angle_x(self._heading)
        if self.flipped_y:
            return flip_angle_y(self._heading)
        return self._heading

    @property
    def width(self):
        return self._width

    def set_width(self, width):
        self._width = width

    @property
    def color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    def last_slant_width(self):
        for element in reversed(self.paper.elements):
            if isinstance(element, Path):
                last_path = element
                break
        else:
            return None

        seg = last_path.segments[-1]
        return vec.mag(vec.vfrom(seg.b_left, seg.b_right))

    # Movement.

    def move_to(self, point):
        self._position = Point(*point)

    def move_forward(self, distance):
        self.move_to(self._calc_forward_position(distance))

    def move_to_y(self, y_target):
        """
        Move forward in the current orientation, until the y coordinate
        equals the given value.
        """
        self.move_to(self._calc_forward_to_y(y_target))

    def move_to_x(self, x_target):
        """
        Move forward in the current orientation, until the x coordinate
        equals the given value.
        """
        self.move_to(self._calc_forward_to_x(x_target))

    def end(self):
        self._current_path = None

    # Turning.

    def turn_to(self, heading):
        if self.flipped_x:
            heading = flip_angle_x(heading)
        if self.flipped_y:
            heading = flip_angle_y(heading)
        self._heading = heading % 360

    def turn_toward(self, point):
        v = vec.vfrom(self._position, point)
        heading = math.degrees(vec.heading(v))
        self.turn_to(heading)

    def turn_left(self, angle):
        self.turn_to(self.heading + angle)

    def turn_right(self, angle):
        self.turn_left(-angle)

    def flip_x(self):
        """
        Make turns behave in the x-opposite manner.
        """
        self.flipped_x = not self.flipped_x

    def flip_y(self):
        """
        Make turns behave in the y-opposite manner.
        """
        self.flipped_y = not self.flipped_y

    # Lines.

    def line_to(self, point, start_angle=None, end_angle=None):
        old_position = self._position
        self.move_to(point)

        if self.flipped_x:
            start_angle = flip_angle_x(start_angle)
            end_angle = flip_angle_x(end_angle)
        if self.flipped_y:
            start_angle = flip_angle_y(start_angle)
            end_angle = flip_angle_y(end_angle)

        self._add_segment(LineSegment(
            a=old_position,
            b=self.position,
            width=self.width,
            color=self.color,
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

    # Arcs.

    def arc_left(
        self, arc_angle, radius=None, center=None, start_angle=None, end_angle=None,
    ):
        # Create a radius vector, which is a vector from the arc center to the
        # current position. Subtract to find the center, then rotate the radius
        # vector to find the arc end point.
        if center is None:
            if arc_angle < 0:
                radius = -abs(radius)
            v_radius = vec.neg(vec.perp(self._vector(radius)))
            center = vec.sub(self._position, v_radius)
        elif radius is None:
            v_radius = vec.vfrom(center, self._position)
            radius = vec.mag(v_radius)
            if arc_angle < 0:
                radius = -radius

        endpoint = vec.add(center, vec.rotate(v_radius, math.radians(arc_angle)))

        self._arc(
            center,
            radius,
            endpoint,
            arc_angle,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def arc_right(
        self, arc_angle, radius=None, center=None, start_angle=None, end_angle=None,
    ):
        # We define a positive radius to be arcing to the left, and a
        # negative radius to be arcing to the right.
        self.arc_left(-arc_angle, radius, center, start_angle, end_angle)

    def arc_to(self, endpoint, center=None, start_angle=None, end_angle=None):
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
        v_chord = vec.vfrom(self._position, endpoint)
        if center is None:
            midpoint = vec.div(vec.add(self._position, endpoint), 2)
            v_bisector = vec.perp(v_chord)
            center = intersect_lines(
                self._position,
                vec.add(self._position, v_perp),
                midpoint,
                vec.add(midpoint, v_bisector),
            )

        # Determine true start heading. This may not be the same as the
        # original pen heading in some circumstances.
        v_radius_start = vec.vfrom(center, self._position)
        v_radius_perp = vec.perp(v_radius_start)
        if vec.dot(v_radius_perp, v_pen) < 0:
            v_radius_perp = vec.neg(v_radius_perp)
        start_heading = math.degrees(vec.heading(v_radius_perp))
        self.turn_to(start_heading)
        # Refresh v_pen and v_perp based on the new start heading.
        v_pen = self._vector()
        v_perp = vec.perp(self._vector())

        # Calculate the arc angle.
        # The arc angle is double the angle between the pen vector and the
        # chord vector. Arcing to the left is a positive angle, and arcing to
        # the right is a negative angle.
        arc_angle = 2 * math.degrees(vec.angle(v_pen, v_chord))
        radius = vec.mag(v_radius_start)
        # Check which side of v_pen the goes toward.
        if vec.dot(v_chord, v_perp) < 0:
            arc_angle = -arc_angle
            radius = -radius

        self._arc(
            center,
            radius,
            endpoint,
            arc_angle,
            start_angle,
            end_angle,
        )

    def _arc(self, center, radius, endpoint, arc_angle, start_angle, end_angle):
        old_position = self._position
        old_heading = self._heading
        self.move_to(endpoint)
        self.turn_left(arc_angle)

        self._add_segment(ArcSegment(
            a=old_position,
            b=endpoint,
            width=self.width,
            color=self.color,
            start_angle=start_angle,
            end_angle=end_angle,
            center=center,
            radius=radius,
            arc_angle=arc_angle,
            start_heading=old_heading,
            end_heading=self._heading,
        ))

    # Shapes.

    def circle(self, radius):
        self.paper.add_element(Circle(
            center=self._position,
            radius=radius,
            color=self.color,
        ))

    def square(self, size):
        self.paper.add_element(Rectangle(
            left=self._position.x - size / 2,
            bottom=self._position.y - size / 2,
            width=size,
            height=size,
            color=self.color,
        ))

    # Internal.

    def _add_segment(self, new_segment):
        # Don't bother adding segments with zero length.
        if points_equal(new_segment.a, new_segment.b):
            return

        def new_path():
            path = Path(self.color)
            path.show_joints = self.show_joints
            path.show_nodes = self.show_nodes
            path.show_bones = self.show_bones
            self.paper.add_element(path)
            path.add_segment(new_segment)
            self._current_path = path

        # Start a new path if this is the first segment added.
        if self._current_path is None:
            new_path()
            return

        # Check whether we are continuing the current stroke or starting a
        # new one.
        assert len(self._current_path.segments) > 0
        last_segment = self._current_path.segments[-1]
        points_same = points_equal(last_segment.b, new_segment.a)
        color_same = (last_segment.color == new_segment.color)

        if points_same and color_same:
            self._current_path.add_segment(new_segment)
        elif points_same and not color_same:
            # We are continuing the old path visually, but with a new
            # color. We implement this by starting a new path, and doing an
            # extra "join_with" to set the start and end of the segment
            # correctly.
            new_path()
            last_segment.join_with(new_segment)
        else:  # There is a break in the path.
            new_path()

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


def flip_angle_x(angle):
    if angle is not None:
        return 180 - angle


def flip_angle_y(angle):
    if angle is not None:
        return -angle
