from .point import Point, points_equal
from .segment import LineSegment, ArcSegment
from .shape import Circle, Rectangle
from .svg import (
    path_element,
    path_move,
    path_line,
    path_arc,
    path_close,
)
from .error import SegmentError


class Path:

    def __init__(self, color):
        self.segments = []
        self.color = color
        self.show_joints = False
        self.show_nodes = False
        self.show_bones = False

    def add_segment(self, new_segment):
        if len(self.segments) > 0:
            last_segment = self.segments[-1]
            last_segment.join_with(new_segment)
        self.segments.append(new_segment)

    def svg(self, precision):
        assert len(self.segments) > 0
        output = []

        stroke_width = None  # Default to fill, not stroke.
        if self.show_bones:
            stroke_width = min(seg.width for seg in self.segments) / 16

        output.append(path_element(
            self.draw_thick(precision),
            self.color,
            stroke_width,
        ))

        if self.show_bones:
            output.append(path_element(
                self.draw(precision),
                self.color,
                stroke_width,
            ))
        if self.show_nodes:
            output.append(self.draw_nodes(precision))
        return '\n'.join(output)

    def draw(self, precision):
        output = []

        start_point = p = Point(*self.segments[0].a)
        output.append(path_move(p.x, p.y, precision))

        # Draw the rest of the stroke.
        for seg in self.segments:
            p = Point(*seg.b)
            if isinstance(seg, LineSegment):
                output.append(path_line(
                    p.x,
                    p.y,
                    precision,
                ))
            elif isinstance(seg, ArcSegment):
                output.append(path_arc(
                    p.x,
                    p.y,
                    seg.arc_angle,
                    seg.radius,
                    precision,
                ))

        # Close the path if necessary.
        if points_equal(seg.b, start_point):
            output.append(path_close())

        return ' '.join(output)

    def draw_thick(self, precision):
        # Create a temporary pen to draw the outline of the path segments,
        # taking into account the thickness of the path.
        from .pen import Pen
        pen = Pen()
        draw_thick_segments(pen, self.segments, self.show_joints)

        # Render the path created by our temporary pen.
        return ' '.join(
            path.draw(precision)
            for path in pen.paper.elements
        )

    def draw_nodes(self, precision):
        shapes = []
        for seg in self.segments:
            shapes.append(Circle(
                seg.a,
                seg.width / 8,
                color=(0, .5, 0),
            ))
            shapes.append(Rectangle(
                seg.b.x - seg.width / 8,
                seg.b.y - seg.width / 8,
                seg.width / 4,
                seg.width / 4,
                color=(.5, 0, 0),
            ))
        return '\n'.join(
            s.svg(precision)
            for s in shapes
        )


def draw_thick_segments(pen, segments, show_joints=False):
    for seg in segments:
        if seg.width is None:
            raise SegmentError(
                'Cannot draw a thick segment without a width '
                'specified.'
            )

    if show_joints:
        for seg in segments:
            draw_segment_right(pen, seg, first=True, last=True)
            draw_segment_left(pen, seg, first=True, last=True)
        return

    if len(segments) == 1:
        seg = segments[0]
        draw_segment_right(pen, seg, first=True, last=True)
        draw_segment_left(pen, seg, first=True, last=True)
    else:
        # Draw all the segments, going out along the right side, then back
        # along the left, treating the first and last segments specially.
        first_seg = segments[0]
        last_seg = segments[-1]
        middle_segments = segments[1:-1]

        draw_segment_right(pen, first_seg, first=True)
        for seg in middle_segments:
            draw_segment_right(pen, seg)
        draw_segment_right(pen, last_seg, last=True)

        draw_segment_left(pen, last_seg, last=True)
        for seg in reversed(middle_segments):
            draw_segment_left(pen, seg)
        draw_segment_left(pen, first_seg, first=True)


def draw_segment_right(pen, seg, first=False, last=False):
    if first:
        # Draw the beginning edge.
        pen.move_to(seg.a_left)
        pen.line_to(seg.a_right)

    # Draw along the length of the segment.
    seg.draw_right(pen)


def draw_segment_left(pen, seg, first=False, last=False):
    if last:
        # Draw the ending thickness edge.
        pen.line_to(seg.b_left)

    # Continue path back towards the beginning.
    seg.draw_left(pen)
