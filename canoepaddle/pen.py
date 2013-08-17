import math
from copy import copy
from functools import wraps

import vec
from .paper import Paper
from .path import Path
from .segment import LineSegment, ArcSegment
from .mode import FillMode, StrokeMode, OutlineMode, modes_compatible
from .point import Point, points_equal
from .geometry import intersect_lines
from .heading import Heading, Angle


def logged(method):
    """
    Decorator to keep track of each time this method is called.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._log.append((method.__name__, copy(args), copy(kwargs)))
        # Don't keep extra log entries added through this call.
        len_before = len(self._log)
        method(self, *args, **kwargs)
        del self._log[len_before:]
    return wrapper


class Pen:

    def __init__(self):
        self.paper = Paper()
        self._mode = None
        self._heading = Heading(0)
        self._position = Point(0.0, 0.0)

        self._path = None

        self._log = []

    # Properties.

    @property
    def position(self):
        return self._position

    @property
    def heading(self):
        return self._heading

    @property
    def mode(self):
        if self._mode is None:
            raise AttributeError('Mode not set.')
        return self._mode.copy()

    @logged
    def fill_mode(self, color=None):
        """
        Start drawing filled paths.
        """
        self.set_mode(FillMode(color))

    @logged
    def stroke_mode(self, width, color=None):
        """
        Start drawing strokes with a width.
        """
        self.set_mode(StrokeMode(width, color))

    @logged
    def outline_mode(self, width, outline_width, outline_color=None):
        """
        Start drawing strokes with a width drawn by thin outlines.
        """
        self.set_mode(OutlineMode(width, outline_width, outline_color))

    @logged
    def set_mode(self, mode):
        if self._mode is not None:
            mode.copy_colors(self._mode)
        self._mode = mode

    def last_path(self):
        return self.paper.elements[-1]

    def last_segment(self):
        return self.last_path().segments[-1]

    def last_slant_width(self):
        seg = self.last_segment()
        return vec.mag(vec.vfrom(seg.b_left, seg.b_right))

    # Movement.

    @logged
    def move_to(self, point):
        self._position = Point(*point)

    @logged
    def move_relative(self, offset):
        self.move_to(vec.add(self.position, offset))

    @logged
    def move_forward(self, distance):
        self.move_to(self._calc_forward_position(distance))

    @logged
    def move_to_y(self, y_target):
        """
        Move forward in the current orientation, until the y coordinate
        equals the given value.
        """
        self.move_to(self._calc_forward_to_y(y_target))

    @logged
    def move_to_x(self, x_target):
        """
        Move forward in the current orientation, until the x coordinate
        equals the given value.
        """
        self.move_to(self._calc_forward_to_x(x_target))

    # Miscellaneous.

    @logged
    def break_stroke(self):
        """
        Break the current path and start a new one.
        """
        self._path = None

    @logged
    def undo(self):
        if self.paper.elements:
            path = self.paper.elements[-1]
            if path.segments:
                path.segments.pop()
                if not path.segments:
                    self.paper.elements.pop()
                    self._path = None
                return

        raise IndexError('Nothing to undo.')

    # Turning.

    @logged
    def turn_to(self, heading):
        self._heading = Heading(heading)

    @logged
    def turn_toward(self, point):
        v = vec.vfrom(self._position, point)
        heading = math.degrees(vec.heading(v))
        self.turn_to(heading)

    @logged
    def turn_left(self, angle):
        self.turn_to(self.heading + angle)

    @logged
    def turn_right(self, angle):
        self.turn_to(self.heading - angle)

    # Lines.

    @logged
    def line_to(self, point, start_slant=None, end_slant=None):
        old_position = self._position
        self.move_to(point)
        self._add_segment(LineSegment(
            a=old_position,
            b=self.position,
            width=self.mode.width,
            color=self.mode.color,
            start_slant=start_slant,
            end_slant=end_slant,
        ))

    @logged
    def line_forward(self, distance, start_slant=None, end_slant=None):
        self.line_to(
            self._calc_forward_position(distance),
            start_slant=start_slant,
            end_slant=end_slant,
        )

    @logged
    def line_to_y(self, y_target, start_slant=None, end_slant=None):
        """
        Draw a line, forward in the current orientation, until the y coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_y(y_target)
        self.line_to(
            new_position,
            start_slant=start_slant,
            end_slant=end_slant,
        )

    @logged
    def line_to_x(self, x_target, start_slant=None, end_slant=None):
        """
        Draw a line, forward in the current orientation, until the x coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_x(x_target)
        self.line_to(
            new_position,
            start_slant=start_slant,
            end_slant=end_slant,
        )

    # Arcs.

    @logged
    def arc_left(
        self, arc_angle, radius=None, center=None, start_slant=None, end_slant=None,
    ):
        arc_angle = Angle(arc_angle)
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

        endpoint = vec.add(center, vec.rotate(v_radius, arc_angle.rad))

        self._arc(
            center,
            radius,
            endpoint,
            arc_angle,
            start_slant=start_slant,
            end_slant=end_slant,
        )

    @logged
    def arc_right(
        self, arc_angle, radius=None, center=None, start_slant=None, end_slant=None,
    ):
        # Reverse the arc angle so we go to the right.
        self.arc_left(-arc_angle, radius, center, start_slant, end_slant)

    @logged
    def arc_to(self, endpoint, center=None, start_slant=None, end_slant=None):
        """
        Draw an arc ending at the specified point, starting tangent to the
        current position and heading.
        """
        if points_equal(self._position, endpoint):
            return
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
        assert not points_equal(center, self._position)
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
            start_slant,
            end_slant,
        )

    def _arc(self, center, radius, endpoint, arc_angle, start_slant, end_slant):
        """
        Internal implementation of arcs.

        Arcs that go to the left have a positive radius and arc angle.
        Arcs that go to the right have a negative radius and arc angle.
        """
        old_position = self._position
        old_heading = self._heading
        self.move_to(endpoint)
        self.turn_left(arc_angle)

        self._add_segment(ArcSegment(
            a=old_position,
            b=endpoint,
            width=self.mode.width,
            color=self.mode.color,
            start_slant=start_slant,
            end_slant=end_slant,
            center=center,
            radius=radius,
            arc_angle=arc_angle,
            start_heading=old_heading,
            end_heading=self._heading,
        ))

    # Shapes.

    @logged
    def circle(self, radius):
        old_position = self._position
        old_heading = self._heading
        self.break_stroke()
        self.turn_to(0)
        self.move_forward(radius)
        self.turn_left(90)
        self.arc_left(180, radius)
        self.arc_left(180, radius)
        self.move_to(old_position)
        self.turn_to(old_heading)

    @logged
    def square(self, size):
        old_position = self._position
        old_heading = self._heading
        self.break_stroke()
        self.move_relative((-size / 2, -size / 2))
        self.turn_to(0)
        self.line_forward(size)
        self.turn_left(90)
        self.line_forward(size)
        self.turn_left(90)
        self.line_forward(size)
        self.turn_left(90)
        self.line_forward(size)
        self.move_to(old_position)
        self.turn_to(old_heading)

    # Internal.

    def _add_segment(self, new_segment):
        # Don't bother adding segments with zero length.
        if points_equal(new_segment.a, new_segment.b):
            return

        # Continue the current path if possible.
        if (
            self._path is not None and
            modes_compatible(self._path.mode, self.mode)
        ):
            self._path.add_segment(new_segment)
        else:
            # Start a new path if this is the first segment or there has been a
            # mode change.
            self._path = path = Path(self.mode)
            self.paper.add_element(path)
            path.add_segment(new_segment)

    def _vector(self, length=1):
        """
        Create a vector pointing in the same direction as the pen, with the
        specified length.
        """
        return vec.from_heading(self._heading.rad, length)

    def _calc_forward_position(self, distance):
        return vec.add(
            self.position,
            self._vector(distance),
        )

    def _calc_forward_to_y(self, y_target):
        x, y = self.position
        y_diff = y_target - y
        x_diff = y_diff / math.tan(self._heading.rad)
        return vec.add(self.position, (x_diff, y_diff))

    def _calc_forward_to_x(self, x_target):
        x, y = self.position
        x_diff = x_target - x
        y_diff = x_diff * math.tan(self._heading.rad)
        return vec.add(self.position, (x_diff, y_diff))

    def log(self):
        result = []
        for name, args, kwargs in self._log:
            arg_strings = []
            for arg in args:
                if isinstance(arg, Point):
                    arg = tuple(arg)
                arg_strings.append(repr(arg))
            for key, value in kwargs.items():
                arg_strings.append('{}={}'.format(key, repr(value)))
            result.append(
                '{}({})'.format(
                    name,
                    ', '.join(arg_strings),
                )
            )
        return result
