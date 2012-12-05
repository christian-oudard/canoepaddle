import math
from collections import namedtuple

import vec

SMOOTH_JOINTS = True

Point = namedtuple('Point', 'x, y')

class Segment:
    def __init__(self, a, b, width, start_angle=None, end_angle=None):
        self.a = a
        self.b = b
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.width = width

    def __iter__(self):
        yield self.a
        yield self.b

    def length(self):
        return vec.dist(self.a, self.b)

    def heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))

    #TODO: make these into properties, and add caching.

    def start_slant(self):
        return self.calc_slant(self.heading(), self.start_angle)

    def end_slant(self):
        return self.calc_slant(self.heading(), self.end_angle)

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

    def extra_length(self):
        """
        The extra length along the right side of the segment due to the angled
        start and end. Note that the same value for the left side is the
        negative of this.
        """
        extra_length = (self.width / 2) * (
            math.tan(math.radians(self.start_slant() - 90)) -
            math.tan(math.radians(self.end_slant() - 90))
        )
        if abs(extra_length) > self.length():
            raise ValueError('Slant is too extreme for the length and width of the segment.')
        return extra_length


class Paper:
    def __init__(self, offset):
        self.offset = offset
        self.strokes = []

    def add_segment(self, a, b, width, start_angle=None, end_angle=None):
        new_segment = Segment(
            Point(*a),
            Point(*b),
            width,
            start_angle,
            end_angle,
        )

        # Check whether we are continuing the current stroke or starting a
        # new one.
        continuing = False
        if len(self.strokes) > 0:
            segments = self.strokes[-1]
            last_segment = segments[-1]
            if last_segment.b == new_segment.a:
                continuing = True

        if continuing:
            self.strokes[-1].append(new_segment)
            # Add a joint between successive segments.
            joint_angle = self.calc_joint_angle(last_segment, new_segment)
            last_segment.end_angle = joint_angle
            new_segment.start_angle = joint_angle
        else:
            # Start a new stroke.
            self.strokes.append([new_segment])

    @staticmethod
    def calc_joint_angle(last_segment, new_segment):
        # Solve the parallelogram created by the previous stroke intersecting
        # with the next stroke. The diagonal of this parallelogram is at the
        # correct joint angle.
        w1 = last_segment.width
        w2 = new_segment.width
        theta = (new_segment.heading() - last_segment.heading()) % 180
        sin_theta = math.sin(math.radians(theta))
        v1 = vec.vfrom(last_segment.a, last_segment.b)
        v2 = vec.vfrom(new_segment.a, new_segment.b)
        v1 = vec.norm(v1, w2 * sin_theta)
        v2 = vec.norm(v2, w1 * sin_theta)
        return math.degrees(vec.heading(vec.vfrom(v1, v2)))

    def to_svg_path(self, precision=12):
        output = []
        for segments in self.strokes:
            # Start a new stroke.
            start_point = segments[0].a
            point = Point(*vec.add(start_point, self.offset))
            output.append('M{:.{p}f},{:.{p}f}'.format(
                point.x, -point.y, p=precision))
            # Draw the rest of the stroke.
            for seg in segments:
                # Close the path, or continue the current segment.
                if seg.b == start_point:
                    output.append('z')
                else:
                    point = Point(*vec.add(seg.b, self.offset))
                    output.append('L{:.{p}f},{:.{p}f}'.format(
                        point.x, -point.y, p=precision))
        return ' '.join(output)

    def to_svg_path_thick(self, precision=12):
        pen = Pen(self.offset)
        for segments in self.strokes:
            self.draw_stroke_thick(pen, segments)
        return pen.paper.to_svg_path(precision=precision)

    def draw_stroke_thick(self, pen, segments):
        if len(segments) == 1:
            seg = segments[0]
            self.draw_segment_right(pen, seg, first=True, last=True)
            self.draw_segment_left(pen, seg, first=True, last=True)
        else:
            # Draw all the segments, going out along the right side, then back
            # along the left, treating the first and last segments specially.
            first_seg = segments[0]
            last_seg = segments[-1]
            middle_segments = segments[1:-1]

            self.draw_segment_right(pen, first_seg, first=True)
            for seg in middle_segments:
                self.draw_segment_right(pen, seg)
            self.draw_segment_right(pen, last_seg, last=True)

            self.draw_segment_left(pen, last_seg, last=True)
            for seg in reversed(middle_segments):
                self.draw_segment_left(pen, seg)
            self.draw_segment_left(pen, first_seg, first=True)

    @staticmethod
    def draw_segment_right(pen, seg, first=False, last=False):
        if first:
            # Draw the beginning edge.
            pen.move_to(seg.a)
            pen.turn_to(seg.heading())
            pen.turn_right(seg.start_slant())

            sw = seg.start_slant_width()
            pen.move_forward(-sw / 2)
            pen.stroke_forward(sw)

        # Draw along the length of the segment.
        pen.turn_to(seg.heading())
        pen.stroke_forward(seg.length() + seg.extra_length())

        if last:
            # Draw the ending thickness edge.
            pen.turn_left(180 - seg.end_slant())
            pen.stroke_forward(seg.end_slant_width())

    @staticmethod
    def draw_segment_left(pen, seg, first=False, last=False):
        if first:
            # Close the path to finish.
            pen.stroke_close()
        else:
            # Continue path back towards the beginning.
            pen.turn_to(seg.heading() + 180)
            pen.stroke_forward(seg.length() - seg.extra_length())


class Pen:
    def __init__(self, offset=(0, 0)):
        self.paper = Paper(offset)
        self._heading = 0
        self._position = (0.0, 0.0)
        self._width = 1.0
        self.offset = offset

    def turn_to(self, heading):
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
        self._position = vec.add(
            self._position,
            vec.rotate((distance, 0), math.radians(self.heading)),
        )

    def set_width(self, width):
        self._width = width

    def stroke_to(self, point, start_angle=None, end_angle=None):
        old_position = self._position
        self.move_to(point)
        self.paper.add_segment(
            old_position,
            self.position,
            self.width,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def stroke_forward(self, distance, start_angle=None, end_angle=None):
        old_position = self._position
        self.move_forward(distance)
        self.paper.add_segment(
            old_position,
            self.position,
            self.width,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def stroke_close(self):
        first_point = self.paper.strokes[-1][0].a
        self.stroke_to(first_point)

    def stroke_to_y(self, y_target, start_angle=None, end_angle=None):
        """
        Stroke forward in the current orientation, until the y coordinate
        equals the given value.
        """
        x, y = self.position
        y_diff = y_target - y
        x_diff = y_diff / math.tan(math.radians(self.heading))
        new_position = vec.add(self.position, (x_diff, y_diff))
        self.stroke_to(new_position, start_angle=start_angle, end_angle=end_angle)

    def stroke_to_x(self, x_target, start_angle=None, end_angle=None):
        """
        Stroke forward in the current orientation, until the x coordinate
        equals the given value.
        """
        x, y = self.position
        x_diff = x_target - x
        y_diff = x_diff * math.tan(math.radians(self.heading))
        new_position = vec.add(self.position, (x_diff, y_diff))
        self.stroke_to(new_position, start_angle=start_angle, end_angle=end_angle)

    @property
    def position(self):
        return self._position

    @property
    def heading(self):
        return self._heading

    @property
    def width(self):
        return self._width


def cosine_rule(a, b, gamma):
    """
    Find C where {A, B, C} are the sides of a triangle, and gamma is
    the angle opposite C.
    """
    return a**2 + b**2 - 2 * a * b * math.cos(gamma)


if __name__ == '__main__':
    sqrt2 = math.sqrt(2)

    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.stroke_forward(3, end_angle=-45)
    p.turn_right(45)
    p.move_forward(0.5 * sqrt2 + 0.5)
    p.turn_right(90)
    p.stroke_forward(3, start_angle=-45)

    path_data = p.paper.to_svg_path_thick()
    #path_data += p.paper.to_svg_path()

    from string import Template
    with open('template.svg') as f:
        t = Template(f.read())
    print(t.substitute(path_data=path_data))
