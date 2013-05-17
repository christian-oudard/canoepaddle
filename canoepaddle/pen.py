import math

import vec
from paper import Paper
from segment import LineSegment, ArcSegment
from point import Point


def flip_angle_x(angle):
    if angle is not None:
        return 180 - angle


class Pen:

    def __init__(self, offset=(0, 0)):
        self.paper = Paper(offset)
        self._heading = 0
        self._position = (0.0, 0.0)
        self._width = 1.0
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

    def stroke_to(self, point, start_angle=None, end_angle=None):
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

    def stroke_forward(self, distance, start_angle=None, end_angle=None):
        self.stroke_to(
            self._calc_forward_position(distance),
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def stroke_to_y(self, y_target, start_angle=None, end_angle=None):
        """
        Stroke forward in the current orientation, until the y coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_y(y_target)
        self.stroke_to(new_position, start_angle=start_angle, end_angle=end_angle)

    def stroke_to_x(self, x_target, start_angle=None, end_angle=None):
        """
        Stroke forward in the current orientation, until the x coordinate
        equals the given value.
        """
        new_position = self._calc_forward_to_x(x_target)
        self.stroke_to(new_position, start_angle=start_angle, end_angle=end_angle)

    def arc_left(self, arc_angle, radius):
        # Create a radius vector, which is a vector from the arc center to the
        # current position. Subtract to find the center, then rotate the radius
        # vector to find the arc end point.
        r = vec.rotate((radius, 0), math.radians(self._heading - 90))
        center = vec.sub(self._position, r)
        endpoint = vec.add(center, vec.rotate(r, math.radians(arc_angle)))

        old_position = self._position
        old_heading = self._heading
        self.move_to(endpoint)
        self.turn_left(arc_angle)

        self.paper.add_segment(ArcSegment(
            a=old_position,
            b=endpoint,
            width=self.width,
            arc_angle=arc_angle,
            radius=radius,
            start_heading=old_heading,
            end_heading=self._heading,
        ))

    def arc_right(self, arc_angle, radius):
        self.arc_left(-arc_angle, -radius)

    def last_slant_width(self):
        #XXX Uncovered.
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

    def _calc_forward_position(self, distance):
        return vec.add(
            self.position,
            vec.rotate((distance, 0), math.radians(self._heading)),
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
