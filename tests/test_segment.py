from nose.tools import assert_equal, assert_raises
from util import (
    assert_segments_equal,
    assert_points_equal,
    sqrt2,
)

from canoepaddle.pen import Pen
from canoepaddle.point import epsilon
from canoepaddle.error import SegmentError


def test_line_segments():
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.turn_to(45)
    p.line_forward(2.0)

    assert_points_equal(p.position, (sqrt2, sqrt2))
    assert_equal(len(p.paper.elements), 1)
    segments = p.paper.elements[0].segments
    for actual, target in zip(segments, [
        ((0, 0), (sqrt2, sqrt2)),
    ]):
        assert_segments_equal(actual, target)


def test_degenerate_segment():

    def draw(offset):
        p = Pen()
        p.stroke_mode(1.0)
        p.move_to((0, 0))
        p.turn_to(0)
        p.line_forward(0.5 + offset, end_slant=45)
        return p

    # No exception raised because the endcaps don't cross.
    p = draw(+0.1)

    # For values within epsilon of crossing, it counts as being on top of the
    # side point.
    p = draw(+epsilon / 2)
    p = draw(0)
    p = draw(-epsilon / 2)

    # Once they really cross, a SegmentError is raised.
    assert_raises(
        SegmentError,
        lambda: draw(-0.1)
    )
