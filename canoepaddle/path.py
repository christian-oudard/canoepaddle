from .point import Point, points_equal
from .bounds import Bounds
from .segment import LineSegment, ArcSegment
from .svg import (
    path_element,
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
        assert len(self.segments) > 0
        output = []

        output.append(path_element(
            self.draw(precision),
            self.mode.color,
        ))

        return '\n'.join(output)

    def draw(self, precision):
        if self.mode.name == 'fill':
            return self.draw_fill(precision)
        elif self.mode.name == 'stroke':
            return self.draw_stroke(precision)
        elif self.mode.name == 'outline':
            return self.draw_outline(precision)

    def draw_fill(self, precision):
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

    def draw_stroke(self, precision):
        # Create a temporary pen to draw the outline of the path segments,
        # taking into account the thickness of the path.
        from .pen import Pen
        pen = Pen()
        pen.fill_mode()
        draw_thick_segments(pen, self.segments, self.mode)

        # Render the path created by our temporary pen.
        return ' '.join(
            path.draw(precision)
            for path in pen.paper.elements
        )

    def draw_outline(self, precision):
        # Create a temporary pen to draw the outline of the path segments,
        # taking into account the thickness of the path and the outline thickness.
        from .pen import Pen
        pen = Pen()
        pen.stroke_mode(self.mode.outline_width)
        draw_thick_segments(pen, self.segments, self.mode)

        # Render the path created by our temporary pen.
        return ' '.join(
            path.draw(precision)
            for path in pen.paper.elements
        )


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
