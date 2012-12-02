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
    s1 = Segment(*s1)
    s2 = Segment(*s2)
    assert_points_equal(s1.a, s2.a)
    assert_points_equal(s1.b, s2.b)

def test_movement():
    p = Pen()

    p.move_to((0, 0))
    p.turn_towards((1, 1))
    assert_equal(p.heading, 45)

def test_stroke():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(45)
    p.stroke_forward(2.0)

    assert_points_equal(p.position, (sqrt2, sqrt2))
    assert_equal(len(p.paper.segments), 1)
    for actual, target in zip(p.paper.segments, [
        ((0, 0), (sqrt2, sqrt2)),
    ]):
        assert_segments_equal(actual, target)

def test_svg_path_thick():
    Paper.precision = 2

    p = Pen()
    p.turn_to(-45)
    p.stroke_forward(5)
    path_data = p.paper.to_svg_path_thick(width=1.0)
    assert_equal(
        path_data,
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 z',
    )

def test_start_angle():
    Paper.precision = 2

    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)
    p.stroke_forward(10, start_angle=-45, end_angle=30)
    path_data = p.paper.to_svg_path_thick(width=1.0)
    assert_equal(
        path_data,
        'M-0.50,-0.50 L0.50,0.50 L9.13,0.50 L10.87,-0.50 z',
    )

    p = Pen()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.stroke_forward(10, start_angle=90, end_angle=None)
    path_data = p.paper.to_svg_path_thick(width=1.0)
    assert_equal(
        path_data,
        'M0.00,-0.71 L-0.00,0.71 L6.72,7.42 L7.42,6.72 z',
    )

def test_start_angle_error():
    p = Pen()
    p.stroke_forward(10, start_angle=0)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(width=1.0),
    )

    p = Pen()
    p.stroke_forward(1, start_angle=40, end_angle=-40)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(width=1.0),
    )
