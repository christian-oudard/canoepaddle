import math
from collections import namedtuple
from textwrap import dedent
from string import Template

import vec

DEBUG_SHOW_JOINTS = False

epsilon = 10e-15

Point = namedtuple('Point', 'x, y')


def points_equal(a, b):
    return all(
        abs(da - db) <= epsilon
        for (da, db) in zip(a, b)
    )


class LineSegment:
    def __init__(self, a, b, width, start_angle=None, end_angle=None):
        self.a = a
        self.b = b
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.width = width
        self.radius = None

    def __iter__(self):
        yield self.a
        yield self.b

    def __repr__(self):
        return '{}(a={a}, b={b}, width={width}, start_angle={start_angle}, end_angle={end_angle})'.format(self.__class__.__name__, **self.__dict__)

    def length(self):
        return vec.dist(self.a, self.b)

    def heading(self):
        return math.degrees(vec.heading(vec.vfrom(self.a, self.b)))

    @property
    def start_heading(self):
        return self.heading()

    @property
    def end_heading(self):
        return self.heading()

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
            raise ValueError(
                'Slant is too extreme for the length and width of the segment: {}'.format(self)
            )
        return extra_length


class ArcSegment:
    def __init__(self, a, b, width, arc_angle, radius, start_heading, end_heading):
        self.a = a
        self.b = b
        self.width = width
        self.arc_angle = arc_angle
        self.radius = radius
        self.start_heading = start_heading
        self.end_heading = end_heading

    def start_slant(self):
        return 90  # Not yet implemented.

    def end_slant(self):
        return 90  # Not yet implemented.

    def start_slant_width(self):
        return self.width

    def end_slant_width(self):
        return self.width

    def heading(self):
        return self.start_heading


class Paper:
    def __init__(self, offset=(0, 0)):
        self.offset = offset
        self.strokes = []

    def add_segment(self, new_segment):
        if points_equal(new_segment.a, new_segment.b):
            return # Don't bother adding segments with zero length.

        new_segment.a = Point(*new_segment.a)
        new_segment.b = Point(*new_segment.b)

        # Check whether we are continuing the current stroke or starting a
        # new one.
        continuing = False
        if len(self.strokes) > 0:
            segments = self.strokes[-1]
            last_segment = segments[-1]
            if points_equal(last_segment.b, new_segment.a):
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
        v1_heading = last_segment.end_heading
        v2_heading = new_segment.start_heading

        # Special case for equal widths, more numerically stable around
        # straight joints.
        if abs(last_segment.width - new_segment.width) < epsilon:
            return ((v1_heading + v2_heading) / 2 + 90) % 180

        # Solve the parallelogram created by the previous stroke intersecting
        # with the next stroke. The diagonal of this parallelogram is at the
        # correct joint angle.
        v1 = vec.vfrom(last_segment.a, last_segment.b)
        v2 = vec.vfrom(new_segment.a, new_segment.b)
        theta = (v2_heading - v1_heading) % 180
        sin_theta = math.sin(math.radians(theta))
        w1 = last_segment.width
        w2 = new_segment.width
        v1 = vec.norm(v1, w2 * sin_theta)
        v2 = vec.norm(v2, w1 * sin_theta)
        return math.degrees(vec.heading(vec.vfrom(v1, v2))) % 180

    def center_on_x(self, x_center):
        x_values = []
        for segments in self.strokes:
            for seg in segments:
                x_values.append(seg.a.x)
                x_values.append(seg.b.x)
        current_center = (max(x_values) + min(x_values)) / 2
        offset = current_center - x_center
        for segments in self.strokes:
            for seg in segments:
                seg.a = (seg.a.x - offset, seg.a.y)
                seg.b = (seg.b.x - offset, seg.b.y)

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
                point = Point(*vec.add(seg.b, self.offset))
                if seg.radius is None:
                    output.append(
                        self.format_line(
                            point.x,
                            -point.y,
                            precision,
                        )
                    )
                else:
                    output.append(
                        self.format_arc(
                            point.x,
                            -point.y,
                            seg.arc_angle,
                            seg.radius,
                            precision,
                        )
                    )
            # Close the path if necessary.
            if points_equal(seg.b, start_point):
                output.append('z')

        return ' '.join(output)

    @staticmethod
    def format_number(n, precision):
        # Handle numbers near zero formatting inconsistently as
        # either "0.0" or "-0.0".
        if abs(n) < 0.5 * 10**(-precision):
            n = 0
        return '{n:.{p}f}'.format(n=n, p=precision)

    @staticmethod
    def format_line(x, y, precision):
        return 'L{x},{y}'.format(
            x=Paper.format_number(x, precision),
            y=Paper.format_number(y, precision),
        )

    @staticmethod
    def format_arc(x, y, arc_angle, radius, precision):
        direction_flag = int(arc_angle < 0)
        sweep_flag = int(abs(arc_angle) % 360 > 180)
        return (
            'A {r},{r} 0 {sweep_flag} {direction_flag} {x},{y}'
        ).format(
            x=Paper.format_number(x, precision),
            y=Paper.format_number(y, precision),
            r=Paper.format_number(abs(radius), precision),
            direction_flag=direction_flag,
            sweep_flag=sweep_flag,
        )

    def to_svg_path_thick(self, precision=12):
        pen = Pen(self.offset)
        for segments in self.strokes:
            self.draw_stroke_thick(pen, segments)
        return pen.paper.to_svg_path(precision=precision)

    def draw_stroke_thick(self, pen, segments):
        if DEBUG_SHOW_JOINTS:
            for seg in segments:
                self.draw_segment_right(pen, seg, first=True, last=True)
                self.draw_segment_left(pen, seg, first=True, last=True)
            return

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
        pen.turn_to(seg.start_heading)
        if seg.radius is None:
            pen.stroke_forward(seg.length() + seg.extra_length())
        else:
            pen.arc_left(seg.arc_angle, seg.radius + seg.width / 2)

        if last:
            # Draw the ending thickness edge.
            pen.turn_left(180 - seg.end_slant())
            pen.stroke_forward(seg.end_slant_width())

    @staticmethod
    def draw_segment_left(pen, seg, first=False, last=False):
        # Continue path back towards the beginning.
        pen.turn_to(seg.end_heading + 180)
        if seg.radius is None:
            pen.stroke_forward(seg.length() - seg.extra_length())
        else:
            pen.arc_right(seg.arc_angle, seg.radius - seg.width / 2)


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


def cosine_rule(a, b, gamma):
    """
    Find C where {A, B, C} are the sides of a triangle, and gamma is
    the angle opposite C.
    """
    return a**2 + b**2 - 2 * a * b * math.cos(gamma)


def format_svg(path_data, path_style):
    svg_template = dedent('''\
        <?xml version="1.0" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        <svg
            xmlns="http://www.w3.org/2000/svg" version="1.1"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            viewBox="-10 -10 20 20"
            width="400px" height="400px"
        >
            <style type="text/css">
                path {
                    $path_style
                }
            </style>
            <path d="
                $path_data
                " />
        </svg>
    ''')
    t = Template(svg_template)
    return t.substitute(
        path_data=path_data,
        path_style=path_style,
    )


if __name__ == '__main__':
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5)
    p.stroke_forward(p.width / 2)
    p.turn_to(0)
    p.stroke_forward(p.width / 2)
    p.arc_left(90, radius=5)

    path_data = p.paper.to_svg_path_thick(precision=2)

    path_style = '''
        stroke: black;
        stroke-width: 0.1;
        stroke-linecap: butt;
        fill: #a00;
    '''
    print(format_svg(path_data, path_style))
