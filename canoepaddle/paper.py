from textwrap import dedent
from string import Template

from .point import Point, points_equal
from .svg import path_move, path_close, path_line, path_arc
from .segment import LineSegment, ArcSegment
from .shape import Circle
from .error import SegmentError


class Paper:
    def __init__(self, precision=12):
        self.precision = precision
        self.strokes = []
        self.shapes = []
        self.style = ''

        # Debug switches.
        self.show_joints = False
        self.show_bones = False
        self.show_nodes = False

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
            # Add a joint between successive segments.
            self.strokes[-1].append(new_segment)
            last_segment.join_with(new_segment)
        else:
            # Start a new stroke.
            self.strokes.append([new_segment])

    def add_shape(self, new_shape):
        self.shapes.append(new_shape)

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
                width="800px" height="800px"
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
        # Debug switch to show the joint nodes between bones.
        nodes = []
        if self.show_nodes:
            for segments in self.strokes:
                for seg in segments:
                    nodes.append(Circle(seg.a, seg.width / 4))
                    nodes.append(Circle(seg.b, seg.width / 6))

        output = []
        for shape in self.shapes + nodes:
            output.append(shape.format(self.precision))

        return '\n'.join(output)

    def svg_path(self):
        output = []
        for segments in self.strokes:
            # Start a new stroke.
            start_point = p = Point(*segments[0].a)
            output.append(path_move(p.x, p.y, self.precision))

            # Draw the rest of the stroke.
            for seg in segments:
                p = Point(*seg.b)
                #TODO: tell, don't ask
                if isinstance(seg, LineSegment):
                    output.append(path_line(
                        p.x,
                        p.y,
                        self.precision,
                    ))
                elif isinstance(seg, ArcSegment):
                    output.append(path_arc(
                        p.x,
                        p.y,
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
        pen = Pen()
        pen.paper.precision = self.precision
        for segments in self.strokes:
            self.draw_stroke_thick(pen, segments)
        path_data = pen.paper.svg_path()
        if self.show_bones:
            path_data += ' ' + self.svg_path()
        return path_data

    def draw_stroke_thick(self, pen, segments):
        for seg in segments:
            if seg.width is None:
                raise SegmentError(
                    'Cannot draw a thick segment without a width '
                    'specified.'
                )

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
            pen.move_to(seg.a_left)
            pen.line_to(seg.a_right)

        # Draw along the length of the segment.
        seg.draw_right(pen)

    @staticmethod
    def draw_segment_left(pen, seg, first=False, last=False):
        if last:
            # Draw the ending thickness edge.
            pen.line_to(seg.b_left)

        # Continue path back towards the beginning.
        seg.draw_left(pen)
