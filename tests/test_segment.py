from nose.tools import assert_equal
from .util import (
    assert_path_data,
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


def test_slant_error():
    # Creating a slant angle close to 0 is not allowed.
    p = Pen()
    p.stroke_mode(1.0)
    p.line_forward(10, start_slant=0)
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert not seg.end_joint_illegal

    p = Pen()
    p.stroke_mode(1.0)
    p.line_forward(10, end_slant=0)
    seg = p.last_segment()
    assert not seg.start_joint_illegal
    assert seg.end_joint_illegal

    # A combination of angles can also create a degenerate segment.
    p = Pen()
    p.stroke_mode(1.0)
    p.line_forward(1, start_slant=40, end_slant=-40)
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert seg.end_joint_illegal


def test_turn_back_no_joint():
    # Make a line turn back on itself, and it doesn't join.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(180)
    p.line_forward(5)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 1,
        (
            'M0.0,-0.5 L0.0,0.5 L10.0,0.5 L10.0,-0.5 '
            'L5.0,-0.5 L5.0,0.5 L10.0,0.5 L10.0,-0.5 L0.0,-0.5 z'
        )
    )


def test_straight_offwidth_no_joint():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.stroke_mode(2.0)
    p.line_forward(3)
    p.stroke_mode(1.0)
    p.line_forward(3)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 1,
        (
            'M0.0,-1.0 L0.0,1.0 L3.0,1.0 L3.0,0.5 L6.0,0.5 '
            'L6.0,-0.5 L3.0,-0.5 L3.0,-1.0 L0.0,-1.0 z'
        )
    )


def test_close_loop_joint_error():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)

    p.line_forward(10)
    p.turn_right(90)
    p.line_forward(10)
    p.turn_right(180)
    p.arc_left(90, 10)

    arc = p.last_segment()
    assert arc.start_joint_illegal
    assert arc.end_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M4.47,0.50 L9.50,0.50 L9.50,5.53 A 10.50,10.50 0 0 0 4.47,0.50 z '
            'M0.00,-0.50 L0.00,0.50 A 9.50,9.50 0 0 1 9.50,10.00 '
            'L10.50,10.00 L10.50,-0.50 L0.00,-0.50 z'
        )
    )


def test_too_sharp_joint():
    # Joint is considered too sharp, so the joint is not made.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_left(175)
    p.line_forward(10)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L10.00,0.50 L10.04,-0.50 L0.08,-1.37 '
            'L-0.01,-0.37 L9.96,0.50 L10.00,-0.50 L0.00,-0.50 z'
        )
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(175)
    p.line_forward(10)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L10.00,0.50 L9.96,-0.50 L-0.01,0.37 '
            'L0.08,1.37 L10.04,0.50 L10.00,-0.50 L0.00,-0.50 z'
        )
    )

    # Joint is considered too sharp, so the outside is not drawn, but the
    # inside joint works.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(20)
    p.turn_left(175)
    p.line_forward(20)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L20.00,0.50 L20.04,-0.50 '
            'L0.12,-2.24 L0.03,-1.25 L8.55,-0.50 L0.00,-0.50 z'
        )
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(20)
    p.turn_right(175)
    p.line_forward(20)

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L8.55,0.50 L0.03,1.25 '
            'L0.12,2.24 L20.04,0.50 L20.00,-0.50 L0.00,-0.50 z'
        )
    )


def test_line_line_half_illegal_joint():
    # The outside edge meets, but the inside is too short to meet.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)

    p.line_forward(2)
    p.turn_left(165)
    p.line_forward(2)

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L5.80,0.50 L0.20,-1.00 '
            'L-0.06,-0.03 L1.87,0.48 L2.00,-0.50 L0.00,-0.50 z'
        )
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)

    p.line_forward(2)
    p.turn_right(165)
    p.line_forward(2)

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L2.00,0.50 L1.87,-0.48 '
            'L-0.06,0.03 L0.20,1.00 L5.80,-0.50 L0.00,-0.50 z'
        )
    )


def test_arc_line_half_illegal_joint():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.line_to((1, 0))
    p.turn_to(180 - 15)
    p.arc_to((-1, 0))

    line, arc = p.last_path().segments
    assert line.end_joint_illegal
    assert arc.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,-0.50 L0.00,0.50 L2.93,0.50 '
            'A 4.36,4.36 0 0 0 -1.13,-0.48 L-0.87,0.48 '
            'A 3.36,3.36 0 0 1 0.87,0.48 L1.00,-0.50 L0.00,-0.50 z'
        )
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((-1, 0))
    p.turn_to(15)
    p.arc_to((1, 0))
    p.line_to((0, 0))

    arc, line = p.paper.paths[0].segments
    assert arc.end_joint_illegal
    assert line.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M-1.13,-0.48 L-0.87,0.48 A 3.36,3.36 0 0 1 0.87,0.48 '
            'L1.00,-0.50 L0.00,-0.50 L0.00,0.50 L2.93,0.50 '
            'A 4.36,4.36 0 0 0 -1.13,-0.48 z'
        )
    )


def test_arc_angle_error():
    # Endpoints with certain angles do not go all the way across the
    # stroke, and are disallowed.
    p = Pen()
    p.stroke_mode(1.0)
    p.arc_left(90, 10, start_slant=0)
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert not seg.end_joint_illegal

    p = Pen()
    p.stroke_mode(1.0)
    p.arc_left(90, 10, end_slant=90)
    seg = p.last_segment()
    assert not seg.start_joint_illegal
    assert seg.end_joint_illegal

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5, start_slant=25)
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert not seg.end_joint_illegal

    # A combination of angles can also create a degenerate arc.
    p = Pen()
    p.stroke_mode(1.0)
    p.turn_toward((1, 0))
    p.turn_left(1)
    p.arc_to((1, 0), start_slant=40, end_slant=-40)
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert seg.end_joint_illegal


def test_arc_no_joint():
    # Try to create an impossible joint between arcs of different widths.
    # It doesn't join.
    p = Pen()
    p.move_to((0, -5))
    p.turn_to(0)

    p.stroke_mode(1.0)
    p.arc_to((5, 0), center=(0, 0))
    p.stroke_mode(2.0)
    p.arc_to((0, 5), center=(0, 0))

    arc1, arc2 = p.last_path().segments
    assert arc1.end_joint_illegal
    assert arc2.start_joint_illegal

    assert_path_data(
        p, 1,
        (
            'M0.0,4.5 L0.0,5.5 A 5.5,5.5 0 0 0 5.5,0.0 L6.0,0.0 '
            'A 6.0,6.0 0 0 0 0.0,-6.0 L0.0,-4.0 '
            'A 4.0,4.0 0 0 1 4.0,0.0 L4.5,0.0 '
            'A 4.5,4.5 0 0 1 0.0,4.5 z'
        )
    )

    # Join two arcs together illegally, but don't make them concentric.
    p = Pen()
    p.move_to((0, -5))
    p.turn_to(0)

    p.stroke_mode(1.0)
    p.arc_to((5, 0), center=(0, 0))
    p.stroke_mode(2.0)
    p.arc_to((0, 5), center=(0, 0.1))

    arc1, arc2 = p.last_path().segments
    assert arc1.end_joint_illegal
    assert arc2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,4.50 L0.00,5.50 A 5.50,5.50 0 0 0 5.50,0.00 L6.00,0.02 '
            'A 6.00,6.00 0 0 0 0.00,-6.10 L0.00,-4.10 '
            'A 4.00,4.00 0 0 1 4.00,-0.02 L4.50,0.00 '
            'A 4.50,4.50 0 0 1 0.00,4.50 z'
        )
    )


def test_arc_arc_half_illegal_joint():
    p = Pen()
    p.move_to((0, -5))
    p.turn_to(0)

    p.stroke_mode(1.0)
    p.arc_to((5, 0), center=(0, 0))
    p.stroke_mode(2.0)
    p.arc_to((10, 5), center=(10, 0))

    arc1, arc2 = p.last_path().segments
    assert arc1.end_joint_illegal
    assert arc2.start_joint_illegal

    assert_path_data(
        p, 2,
        (
            'M0.00,4.50 L0.00,5.50 A 5.50,5.50 0 0 0 5.50,0.00 L6.00,0.00 '
            'A 4.00,4.00 0 0 1 10.00,-4.00 L10.00,-6.00 '
            'A 6.00,6.00 0 0 0 4.21,1.58 '
            'A 4.50,4.50 0 0 1 0.00,4.50 z'
        )
    )


def test_degenerate_arc():
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_to(
        (5, 0),
        center=(0, -200),
        start_slant=-5,
        end_slant=5,
    )
    seg = p.last_segment()
    assert seg.start_joint_illegal
    assert seg.end_joint_illegal


def test_custom_cap():

    def circle_cap(pen, end):
        pen.arc_to(end)

    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.last_segment().end_cap = circle_cap
    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L5,1 A 1,1 0 0 0 5,-1 L0,-1 z'
    )

    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.last_segment().start_cap = circle_cap
    assert_path_data(
        p, 0,
        'M0,-1 A 1,1 0 1 0 0,1 L5,1 L5,-1 L0,-1 z'
    )
