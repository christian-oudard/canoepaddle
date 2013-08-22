from nose.tools import assert_equal
from util import (
    assert_segments_equal,
    assert_points_equal,
    sqrt2,
)

from canoepaddle.pen import Pen
from canoepaddle.point import epsilon


def test_line_segments():
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.turn_to(45)
    p.line_forward(2.0)

    assert_points_equal(p.position, (sqrt2, sqrt2))
    assert_equal(len(p.paper.paths), 1)
    segments = p.last_path().segments
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

    # No error when the endcaps don't cross.
    p = draw(+0.1)
    assert not p.last_segment().start_joint_illegal
    assert not p.last_segment().end_joint_illegal

    # For values within epsilon of crossing, it counts as being on top of the
    # side point.
    p = draw(+epsilon / 2)
    assert not p.last_segment().start_joint_illegal
    assert not p.last_segment().end_joint_illegal
    p = draw(0)
    assert not p.last_segment().start_joint_illegal
    assert not p.last_segment().end_joint_illegal
    p = draw(-epsilon / 2)
    assert not p.last_segment().start_joint_illegal
    assert not p.last_segment().end_joint_illegal

    # Once they really cross, there is an error.
    p = draw(-0.1)
    assert p.last_segment().start_joint_illegal
    assert p.last_segment().end_joint_illegal
