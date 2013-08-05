from .point import Point, points_equal
from .bounds import Bounds
from .segment import LineSegment, ArcSegment
from .svg import (
    path_move,
    path_line,
    path_arc,
    path_close,
)


class Path:

    def __init__(self, mode):
        self.mode = mode
        self.segments = []

    def bounds(self):
        return Bounds.union_all(seg.bounds() for seg in self.segments)

    def translate(self, offset):
        for seg in self.segments:
            seg.translate(offset)

    def svg(self, precision):
        # Defer to the drawing mode to actually turn our path data into
        # svg code. The mode will then call some combination of
        # Path.render_path() and Path.draw_outline() to produce the finished
        # styled drawing.
        return self.mode.svg(self, precision)

    def render_path(self, precision):
        assert len(self.segments) > 0

        path_data = []

        start_point = p = Point(*self.segments[0].a)
        path_data.append(path_move(p.x, p.y, precision))

        for seg in self.segments:
            p = Point(*seg.b)
            if isinstance(seg, LineSegment):
                path_data.append(path_line(
                    p.x,
                    p.y,
                    precision,
                ))
            elif isinstance(seg, ArcSegment):
                path_data.append(path_arc(
                    p.x,
                    p.y,
                    seg.arc_angle,
                    seg.radius,
                    precision,
                ))

        # Close the path if necessary.
        if points_equal(seg.b, start_point):
            path_data.append(path_close())

        return ' '.join(path_data)

    def draw_outline(self, pen, precision):
        # Draw along the outline using a temporary pen we are given.
        draw_thick_segments(pen, self.segments, self.mode)


def draw_thick_segments(pen, segments, mode):
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
        if seg.loop_start:
            # If this segment starts a loop, start directly on right side of
            # the loop.
            pen.move_to(seg.a_right)
        else:
            # Draw the beginning edge of the stroke.
            pen.move_to(seg.a_left)
            pen.line_to(seg.a_right)

    # Draw along the length of the segment.
    seg.draw_right(pen)


def draw_segment_left(pen, seg, first=False, last=False):
    if last:
        if seg.loop_end:
            # If this segment ends a loop, finish the right side and start the
            # left side of the loop.
            pen.move_to(seg.b_left)
        else:
            # Draw the ending thickness edge.
            pen.line_to(seg.b_left)

    # Continue path back towards the beginning.
    seg.draw_left(pen)
