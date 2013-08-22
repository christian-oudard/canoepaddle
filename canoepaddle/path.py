from .point import Point, points_equal
from .bounds import Bounds
from .segment import LineSegment, ArcSegment
from .svg import (
    path_move,
    path_line,
    path_arc,
    path_close,
)
from .geometry import collinear


class Path:

    def __init__(self, mode):
        self.mode = mode
        self.segments = []

        self.loop_start_segment = None

    def svg(self, precision):
        # Defer to the drawing mode to actually turn our path data into
        # svg code. The mode will then call some combination of
        # Path.render_path() and Path.draw_outline() to produce the finished
        # styled drawing.
        return self.mode.svg(self, precision)

    def bounds(self):
        return Bounds.union_all(seg.bounds() for seg in self.segments)

    def copy(self):
        other = Path(self.mode.copy())
        other.segments = [seg.copy() for seg in self.segments]
        other.loop_start_segment = self.loop_start_segment.copy()
        return other

    def translate(self, offset):
        for seg in self.segments:
            seg.translate(offset)

    def mirror_x(self, x_center):
        for seg in self.segments:
            seg.mirror_x(x_center)

    def mirror_y(self, y_center):
        for seg in self.segments:
            seg.mirror_y(y_center)

    def join_with(self, other):
        # Selectively reverse paths so that the last point of this path leads
        # into the first point of the other path.
        self_first = self.segments[0].a
        self_last = self.segments[-1].b
        other_first = other.segments[0].a
        other_last = other.segments[-1].b
        if points_equal(self_first, other_last):
            self.reverse()
            other.reverse()
        elif points_equal(self_first, other_first):
            self.reverse()
        elif points_equal(self_last, other_last):
            other.reverse()

        #print('join {}-{} < {}-{} ({} < {})'.format(
            #tuple(self.segments[0].a),
            #tuple(self.segments[-1].b),
            #tuple(other.segments[0].a),
            #tuple(other.segments[-1].b),
            #id(self), id(other),
        #))

        self.segments[-1].join_with(other.segments[0])
        self.segments.extend(other.segments)

    def reverse(self):
        self.segments.reverse()
        for segment in self.segments:
            segment.reverse()

    def fuse(self):
        """
        Find consecutive straight segments in this path that could be
        combined without loss into a single segment.
        """
        # TODO: Don't fuse unless they have None as the end slants?
        i = 0
        while i < len(self.segments) - 1:
            left = self.segments[i]
            right = self.segments[i + 1]
            if (
                isinstance(left, LineSegment) and
                isinstance(right, LineSegment) and
                left.width == right.width and
                left.color == right.color and
                collinear(left.a, left.b, right.b)
            ):
                fused_segment = left.fused_with(right)
                self.segments[i:i+2] = [fused_segment]
                # Leave i unchanged so fused_segment will be the
                # "left" segment next iteration.
            else:
                # Cannot fuse, try the next pair.
                i += 1

    def add_segment(self, new_segment):
        if not self.segments:
            self.segments.append(new_segment)
            self.loop_start_segment = new_segment
            return

        # Check whether we need to join with the last segment.
        last_segment = self.segments[-1]
        if points_equal(last_segment.b, new_segment.a):
            last_segment.join_with(new_segment)
        else:
            # The new segment does not connect to the last one, so it starts a
            # new potential loop.
            self.loop_start_segment = new_segment

        # Check whether we need to join to the first segment.
        if (
            self.loop_start_segment is not None and
            points_equal(new_segment.b, self.loop_start_segment.a)
        ):
            new_segment.join_with(self.loop_start_segment)
            self.loop_start_segment = None

        self.segments.append(new_segment)

    def render_path(self, precision):
        assert len(self.segments) > 0

        path_data = []
        start_point = p = Point(*self.segments[0].a)
        last_point = None
        for seg in self.segments:
            if not points_equal(seg.a, last_point):
                start_point = seg.a
                path_data.append(path_move(seg.a.x, seg.a.y, precision))
            last_point = p = Point(*seg.b)
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
                last_point = None

        return ' '.join(path_data)

    def draw_outline(self, pen, precision):
        # Draw along the outline of each path section using the temporary pen
        # we are given.
        for color, segments in group_segments(self.segments):
            mode = pen.mode
            mode.color = color
            pen.set_mode(mode)
            loop = points_equal(segments[-1].b, segments[0].a)
            draw_thick_segments(pen, segments, loop=loop)


def draw_thick_segments(pen, segments, loop):

    def draw_segment_right(seg, first=False, last=False):
        if first:
            # This starts on the left of the first segment.
            if loop:
                # If this segment starts a loop, start directly on right side of
                # the loop.
                pen.move_to(seg.a_right)
            else:
                # Draw the beginning edge of the stroke.
                pen.move_to(seg.a_left)
                pen.line_to(seg.a_right)

        # Draw along the length of the segment.
        # If we are not in the right position, go there.
        if not points_equal(pen.position, seg.a_right):
            pen.line_to(seg.a_right)
        seg.draw_right(pen)
        assert pen.position == seg.b_right

    def draw_segment_left(seg, first=False, last=False):
        if last:
            # This starts on the right of the last segment.
            if loop:
                # If this segment ends a loop, finish the right side and start the
                # left side of the loop.
                # Draw a line between the loop start segment a_left and
                # seg.b_left, in case there was a joint error.
                pen.move_to(segments[0].a_left)
                pen.line_to(seg.b_left)
            else:
                # Draw the ending thickness edge.
                pen.line_to(seg.b_left)

        # Continue path back towards the beginning.
        # If we are not in the right position, go there.
        if not points_equal(pen.position, seg.b_left):
            pen.line_to(seg.b_left)
        seg.draw_left(pen)
        assert points_equal(pen.position, seg.a_left)

    # Draw segments.
    if len(segments) == 1:
        seg = segments[0]
        draw_segment_right(seg, first=True, last=True)
        draw_segment_left(seg, first=True, last=True)
    else:
        # Draw all the segments, going out along the right side, then back
        # along the left, treating the first and last segments specially.
        first_seg = segments[0]
        last_seg = segments[-1]
        middle_segments = segments[1:-1]

        draw_segment_right(first_seg, first=True)
        for seg in middle_segments:
            draw_segment_right(seg)
        draw_segment_right(last_seg, last=True)

        draw_segment_left(last_seg, last=True)
        for seg in reversed(middle_segments):
            draw_segment_left(seg)
        draw_segment_left(first_seg, first=True)


def group_segments(segments):
    """
    Split segments into continuous runs of the same color.
    """
    group = []
    for seg in segments:
        if not group:
            group.append(seg)
            continue
        last_seg = group[-1]
        if (
            seg.color == last_seg.color and
            points_equal(last_seg.b, seg.a)
        ):
            group.append(seg)
        else:  # Finish this group and start another.
            yield last_seg.color, group
            group = [seg]
    yield seg.color, group
