from nose.tools import assert_equal, assert_almost_equal

from stroke import Pen, sqrt2

def assert_points_equal(a, b):
    xa, ya = a
    xb, yb = b
    assert_almost_equal(xa, xb, places=12)
    assert_almost_equal(ya, yb, places=12)

def assert_segments_equal(s1, s2):
    assert_points_equal(s1[0], s2[0])
    assert_points_equal(s1[1], s2[1])

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
    p = Pen()
    p.paper.precision = 2
    p.turn_to(-45)
    p.stroke_forward(5)
    path_data = p.paper.to_svg_path_thick(width=1.0)
    assert_equal(
        path_data,
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 z',
    )
