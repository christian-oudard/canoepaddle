from nose.tools import (
    assert_equal,
    assert_almost_equal,
    assert_raises,
)

from stroke import Pen, Paper, Segment, sqrt2

def assert_points_equal(a, b):
    xa, ya = a
    xb, yb = b
    assert_almost_equal(xa, xb, places=12)
    assert_almost_equal(ya, yb, places=12)

def assert_segments_equal(s1, s2):
    a1, b1 = s1
    a2, b2 = s2
    assert_points_equal(a1, a2)
    assert_points_equal(b1, b2)

def test_movement():
    p = Pen()

    p.move_to((0, 0))
    p.turn_toward((1, 1))
    assert_equal(p.heading, 45)

def test_stroke():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(45)
    p.stroke_forward(2.0)

    assert_points_equal(p.position, (sqrt2, sqrt2))
    assert_equal(len(p.paper.strokes), 1)
    segments = p.paper.strokes[0]
    for actual, target in zip(segments, [
        ((0, 0), (sqrt2, sqrt2)),
    ]):
        assert_segments_equal(actual, target)

def test_svg_path_thick():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(-45)
    p.stroke_forward(5)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 z',
    )

def test_angle():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.stroke_forward(10, start_angle=-45, end_angle=30)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M-0.50,-0.50 L0.50,0.50 L9.13,0.50 L10.87,-0.50 z',
    )

    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.stroke_forward(10, start_angle=90, end_angle=None)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M0.00,-0.71 L-0.00,0.71 L6.72,7.42 L7.42,6.72 z',
    )

def test_angle_error():
    p = Pen()
    p.set_width(1.0)
    p.stroke_forward(10, start_angle=0)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(),
    )

    p = Pen()
    p.set_width(1.0)
    p.stroke_forward(1, start_angle=40, end_angle=-40)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(),
    )

def test_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.stroke_forward(6)
    p.turn_right(60)
    p.stroke_forward(6)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L2.57,5.45 L3.43,4.95 L0.29,-0.50 z',
    )

def test_offwidth_joint():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.move_forward(-3)
    p.stroke_forward(3)
    p.set_width(0.5)
    p.turn_left(90)
    p.stroke_forward(3)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M-3.00,-0.50 L-3.00,0.50 L0.25,0.50 L0.25,-3.00 L-0.25,-3.00 L-0.25,-0.50 z'
    )

def test_offwidth_joint_error():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.stroke_forward(3)
    p.set_width(0.5)
    p.stroke_forward(3)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(),
    )

def test_multiple_strokes():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.move_to((0, 0))
    p.stroke_forward(3)
    p.move_to((0, 3))
    p.stroke_forward(3)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        (
            'M0.00,-0.50 L-0.00,0.50 L3.00,0.50 L3.00,-0.50 z '
            'M0.00,-3.50 L-0.00,-2.50 L3.00,-2.50 L3.00,-3.50 z'
        ),
    )
