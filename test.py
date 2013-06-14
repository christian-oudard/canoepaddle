import math

from nose.tools import (
    assert_equal,
    assert_almost_equal,
    assert_raises,
)

from canoepaddle import Pen
from canoepaddle.paper import Paper
from canoepaddle.segment import LineSegment
from canoepaddle.point import Point
from canoepaddle.geometry import intersect_lines


sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


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


def test_move_to_xy():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.move_to_x(1)
    assert_points_equal(p.position, (1, -1))

    p = Pen()
    p.move_to((0, 0))
    p.turn_toward((3, 4))
    p.move_to_y(8)
    assert_points_equal(p.position, (6, 8))


def test_stroke():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(45)
    p.line_forward(2.0)

    assert_points_equal(p.position, (sqrt2, sqrt2))
    assert_equal(len(p.paper.strokes), 1)
    segments = p.paper.strokes[0]
    for actual, target in zip(segments, [
        ((0, 0), (sqrt2, sqrt2)),
    ]):
        assert_segments_equal(actual, target)


def test_line_to_coordinate():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(45)
    p.line_to_y(3)
    assert_points_equal(p.position, (3, 3))

    for x, y in [
        (2, 1),
        (3, -4),
        (-7, -5),
        (-6, 6),
    ]:
        p = Pen()

        p.move_to((0, 0))
        p.turn_toward((x, y))
        p.line_to_y(y * 2)
        assert_points_equal(p.position, (x * 2, y * 2))

        p.move_to((0, 0))
        p.turn_toward((x, y))
        p.line_to_x(x * 3)
        assert_points_equal(p.position, (x * 3, y * 3))


def test_format_svg():
    p = Pen()
    svg = p.paper.format_svg()
    assert svg.startswith('<?xml')
    svg = p.paper.format_svg(thick=True)
    assert svg.startswith('<?xml')


def test_svg_path_thick():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(-45)
    p.line_forward(5)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 L0.35,-0.35 z',
    )


def test_angle():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10, start_angle=-45, end_angle=30)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        'M-0.50,-0.50 L0.50,0.50 L9.13,0.50 L10.87,-0.50 L-0.50,-0.50 z',
    )

    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(10, start_angle=90, end_angle=None)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        'M0.00,-0.71 L0.00,0.71 L6.72,7.42 L7.42,6.72 L0.00,-0.71 z',
    )


def test_angle_error():
    p = Pen()
    p.set_width(1.0)
    p.line_forward(10, start_angle=0)
    assert_raises(
        ValueError,
        lambda: p.paper.svg_path_thick(),
    )

    p = Pen()
    p.set_width(1.0)
    p.line_forward(1, start_angle=40, end_angle=-40)
    assert_raises(
        ValueError,
        lambda: p.paper.svg_path_thick(),
    )


def test_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L2.57,5.45 '
            'L3.43,4.95 L0.29,-0.50 L-6.00,-0.50 z'
        ),
    )


def test_show_joints():
    p = Pen()
    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)
    p.paper.show_joints = True
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L0.29,-0.50 L-6.00,-0.50 z '
            'M0.29,-0.50 L-0.29,0.50 L2.57,5.45 L3.43,4.95 L0.29,-0.50 z'
        ),
    )


def test_flip_x():
    p = Pen()
    p.set_width(1.0)
    p.flip_x()
    p.turn_to(180)
    p.move_forward(6)
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        'M6.00,0.50 L6.00,-0.50 L-0.29,-0.50 L-3.43,4.95 '
        'L-2.57,5.45 L0.29,0.50 L6.00,0.50 z'
    )


def test_center_on_x():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)
    p.paper.center_on_x(0)
    p.paper.set_precision(0)
    path_data = p.paper.svg_path()
    assert_equal(
        path_data,
        'M-2,0 L2,0',
    )


def test_straight_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-90)
    p.line_forward(1)
    p.line_forward(1)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M0.50,0.00 L-0.50,0.00 L-0.50,1.00 L-0.50,2.00 '
            'L0.50,2.00 L0.50,1.00 L0.50,0.00 z'
        ),
    )

    # Make a line turn back on itself; it doesn't work.
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(180)
    p.line_forward(10)
    assert_raises(
        ValueError,
        lambda: p.paper.svg_path_thick(),
    )


def test_offwidth_joint():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.move_forward(-3)
    p.line_forward(3)
    p.set_width(0.5)
    p.turn_left(90)
    p.line_forward(3)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M-3.00,-0.50 L-3.00,0.50 L0.25,0.50 L0.25,-3.00 '
            'L-0.25,-3.00 L-0.25,-0.50 L-3.00,-0.50 z'
        ),
    )


def test_offwidth_joint_error():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.line_forward(3)
    p.set_width(0.5)
    assert_raises(
        ValueError,
        lambda: p.line_forward(3)
    )


def test_calc_joint_angle():
    paper = Paper()

    # 90 degree turn, same width.
    assert_almost_equal(
        paper.calc_joint_angle(
            LineSegment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            LineSegment(
                Point(10, 0),
                Point(10, -10),
                width=1,
            ),
        ),
        45,
    )

    # 90 degree turn, different width.
    assert_almost_equal(
        paper.calc_joint_angle(
            LineSegment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            LineSegment(
                Point(10, 0),
                Point(10, -10),
                width=2,
            ),
        ),
        math.degrees(math.atan2(1, 2)),
    )

    # Straight on to the right, same width.
    assert_almost_equal(
        paper.calc_joint_angle(
            LineSegment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            LineSegment(
                Point(10, 0),
                Point(20, 0),
                width=1,
            ),
        ),
        90,
    )


def test_calc_joint_angle_straight():
    # The math in calc_joint_angle can get numerically unstable very close to
    # straight joints at various headings.
    for heading_angle in range(0, 360):
        p = Pen()
        p.set_width(1.0)
        p.move_to((0, 0))
        p.turn_to(heading_angle)
        p.line_forward(10)
        p.line_forward(10)
        p.paper.set_precision(2)
        p.paper.svg_path_thick()  # Doesn't crash.

        # Check that the joint angle is 90 degrees from the heading.
        strokes = p.paper.strokes
        assert_equal(len(strokes), 1)
        segments = strokes[0]
        assert_equal(len(segments), 2)
        a, b = segments
        joint_angle = p.paper.calc_joint_angle(a, b)
        assert_almost_equal(joint_angle % 180, (heading_angle + 90) % 180)


def test_multiple_strokes():
    p = Pen()
    p.set_width(1.0)
    p.turn_to(0)
    p.move_to((0, 0))
    p.line_forward(3)
    p.move_to((0, 3))
    p.line_forward(3)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()

    assert_equal(
        path_data,
        (
            'M0.00,-0.50 L0.00,0.50 L3.00,0.50 L3.00,-0.50 L0.00,-0.50 z '
            'M0.00,-3.50 L0.00,-2.50 L3.00,-2.50 L3.00,-3.50 L0.00,-3.50 z'
        ),
    )


def test_last_slant_width():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(1, end_angle=90)

    assert_almost_equal(p.last_slant_width(), sqrt2)

    p.move_to((0, 0))
    p.turn_to(30)
    p.line_forward(1, end_angle=90)
    assert_almost_equal(p.last_slant_width(), 2 / sqrt3)


def test_intersect_lines():
    assert_points_equal(
        intersect_lines(
            (0, 0),
            (10, 10),
            (0, 10),
            (10, 0),
        ),
        (5, 5),
    )
    assert_points_equal(
        intersect_lines(
            (0, 0),
            (10, 0),
            (5, 0),
            (15, 0.01),
        ),
        (5, 0),
    )
    assert_raises(
        ValueError,
        lambda: intersect_lines(
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1),
        )
    )


def test_arc():
    # Draw arcs with all four combinations of sweep and direction flags.
    p = Pen()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5)
    p.arc_right(270, radius=5)

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_right(90, radius=5)
    p.arc_left(270, radius=5)

    p.paper.set_precision(0)
    path_data = p.paper.svg_path()
    assert_equal(
        path_data,
        (
            'M-5,0 A 5,5 0 0 0 0,-5 '
            'A 5,5 0 1 1 5,0 '
            'M-5,0 A 5,5 0 0 1 0,5 '
            'A 5,5 0 1 0 5,0'
        ),
    )


def test_arc_to():
    # Make the same arcs as test_arc, but using the destination points instead
    # of the angles.
    p = Pen()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_to((0, 5))
    p.arc_to((5, 0))

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_to((0, -5))
    p.arc_to((5, 0))

    p.paper.set_precision(0)
    path_data = p.paper.svg_path()
    assert_equal(
        path_data,
        (
            'M-5,0 A 5,5 0 0 0 0,-5 '
            'A 5,5 0 1 1 5,0 '
            'M-5,0 A 5,5 0 0 1 0,5 '
            'A 5,5 0 1 0 5,0'
        ),
    )


def test_arc_zero():
    # Zero-angle and zero-radius arcs have zero length, so they are not added.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_left(0, radius=1)
    assert_equal(p.paper.strokes, [])

    p.arc_left(90, radius=0)
    assert_equal(p.paper.strokes, [])


def test_arc_normalize():
    # Arc angles larger than 360 behave correctly.
    p = Pen()
    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(360 + 90, radius=5)

    p.paper.set_precision(0)
    path_data = p.paper.svg_path()
    assert_equal(
        path_data,
        'M-5,0 A 5,5 0 0 0 0,-5'
    )


def test_thick_arc():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5)
    p.line_forward(p.width / 2)
    p.turn_to(0)
    p.line_forward(p.width / 2)
    p.arc_left(90, radius=5)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M0.00,-0.50 L0.00,0.50 '
            'A 5.50,5.50 0 0 0 5.50,-5.00 '
            'A 5.50,5.50 0 0 0 11.00,-10.50 '
            'L10.00,-10.50 '
            'A 4.50,4.50 0 0 1 5.50,-6.00 '
            'L4.50,-6.00 L4.50,-5.00 '
            'A 4.50,4.50 0 0 1 0.00,-0.50 z'
        ),
    )


def test_circle():
    p = Pen()
    p.circle(1)

    p.paper.set_precision(0)
    assert_equal(
        p.paper.svg_shapes(),
        '<ellipse cx="0" cy="0" rx="1" ry="1" />',
    )
