import math
from textwrap import dedent
from string import Template

import vec
from .point import Point, points_equal, epsilon
from .svg import path_move, path_close, path_line, path_arc


class Paper:
    def __init__(self, offset=(0, 0), precision=12):
        self.offset = offset
        self.precision = precision
        self.strokes = []
        self.shapes = []
        self.show_joints = False
        self.style = ''

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

    def add_shape(self, new_shape):
        self.shapes.append(new_shape)

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
        width1 = last_segment.width
        width2 = new_segment.width
        v1 = vec.norm(v1, width2 * sin_theta)
        v2 = vec.norm(v2, width1 * sin_theta)
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

    def set_style(self, style):
        self.style = style

    def set_precision(self, precision):
        self.precision = precision

    def format_svg(self, thick=False):
        shapes = self.svg_shapes()
        if thick:
            path_data = self.svg_path_thick()
        else:
            path_data = self.svg_path()

        svg_template = dedent('''\
            <?xml version="1.0" standalone="no"?>
            <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
            <svg
                xmlns="http://www.w3.org/2000/svg" version="1.1"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                viewBox="-10 -10 20 20"
                width="400px" height="400px"
            >
                <style type="text/css">
                    * {
                        $style
                    }
                </style>
                $shapes
                <path d="
                    $path_data
                    " />
            </svg>
        ''')
        t = Template(svg_template)
        return t.substitute(
            shapes=shapes,
            path_data=path_data,
            style=self.style,
        )

    def svg_shapes(self):
        output = []
        for shape in self.shapes:
            output.append(shape.format(self.precision))
        return '\n'.join(output)

    def svg_path(self):
        output = []
        for segments in self.strokes:
            # Start a new stroke.
            start_point = segments[0].a
            point = Point(*vec.add(start_point, self.offset))
            output.append(path_move(point.x, point.y, self.precision))

            # Draw the rest of the stroke.
            for seg in segments:
                point = Point(*vec.add(seg.b, self.offset))
                if seg.radius is None:
                    output.append(path_line(
                        point.x,
                        point.y,
                        self.precision,
                    ))
                else:
                    output.append(path_arc(
                        point.x,
                        point.y,
                        seg.arc_angle,
                        seg.radius,
                        self.precision,
                    ))
            # Close the path if necessary.
            if points_equal(seg.b, start_point):
                output.append(path_close())

        return ' '.join(output)

    def svg_path_thick(self):
        from .pen import Pen
        pen = Pen(self.offset)
        pen.paper.precision = self.precision
        for segments in self.strokes:
            self.draw_stroke_thick(pen, segments)
        return pen.paper.svg_path()

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
