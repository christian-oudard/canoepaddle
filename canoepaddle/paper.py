import math

import vec
from point import Point, points_equal
from util import epsilon


class Paper:
    def __init__(self, offset=(0, 0)):
        self.offset = offset
        self.strokes = []
        self.show_joints = False

    def add_segment(self, new_segment):
        if points_equal(new_segment.a, new_segment.b):
            return  # Don't bother adding segments with zero length.

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
        from pen import Pen
        pen = Pen(self.offset)
        for segments in self.strokes:
            self.draw_stroke_thick(pen, segments)
        return pen.paper.to_svg_path(precision=precision)

    def draw_stroke_thick(self, pen, segments):
        if self.show_joints:
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
