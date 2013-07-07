import math

from nose.tools import (
    assert_equal,
    assert_almost_equal,
    assert_raises,
)

import vec
from canoepaddle import Pen
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


def test_line():
    p = Pen()
    p.set_width(2)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.paper.set_precision(0)
    path_data = p.paper.svg_path()
    assert_equal(
        path_data,
        'M0,0 L5,0',
    )


def test_line_thick():
    p = Pen()
    p.set_width(2)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.paper.set_precision(0)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        'M0,-1 L0,1 L5,1 L5,-1 L0,-1 z',
    )


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
    # Creating an angle close to 0 is not allowed.
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        ValueError,
        lambda: p.line_forward(10, start_angle=0)
    )

    # A combination of angles can also create a degenerate segment.
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        ValueError,
        lambda: p.line_forward(1, start_angle=40, end_angle=-40),
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


def test_turn_back_error():
    # Make a line turn back on itself; it doesn't work.
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(180)
    assert_raises(
        ValueError,
        lambda: p.line_forward(10),
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


def test_straight_joint_headings():
    # The math in calculating joint geometry can get numerically unstable
    # very close to straight joints at various headings.
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
        s0, s1 = segments

        target_angle = (heading_angle + 90) % 180

        joint_angle = math.degrees(vec.heading(vec.vfrom(s0.b_right, s0.b_left)))
        assert_almost_equal(joint_angle % 180, target_angle)

        joint_angle = math.degrees(vec.heading(vec.vfrom(s1.a_right, s1.a_left)))
        assert_almost_equal(joint_angle % 180, target_angle)


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
    p.set_width(1.0)

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
    assert_equal(
        intersect_lines(
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1),
        ),
        None,
    )
    assert_equal(
        intersect_lines(
            (0, 0),
            (1, 0),
            (2, 1),
            (2, -1),
            segment=True,
        ),
        None,
    )
    assert_equal(
        intersect_lines(
            (2, 1),
            (2, -1),
            (0, 0),
            (1, 0),
            segment=True,
        ),
        None,
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


def test_arc_angle():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5, start_angle=45, end_angle=45)
    p.paper.set_precision(2)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M0.53,-0.53 L-0.48,0.48 A 5.50,5.50 0 0 0 5.48,-5.48 '
            'L4.47,-4.47 A 4.50,4.50 0 0 1 0.53,-0.53 z'
        ),
    )


def test_arc_angle_error():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    assert_raises(
        ValueError,
        lambda: p.arc_left(90, radius=5, start_angle=25)
    )


def test_degenerate_arc():
    p = Pen()
    p.set_width(2.0)

    p.move_to((-5, 0))
    p.turn_to(0)
    assert_raises(
        ValueError,
        lambda: p.arc_to(
            (5, 0),
            center=(0, -200),
            start_angle=-5,
            end_angle=5,
        )
    )


def test_arc_joint():
    p = Pen()
    p.set_width(1.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.turn_left(90)
    p.arc_left(180, 3)

    p.paper.set_precision(3)
    path_data = p.paper.svg_path_thick()
    assert_equal(
        path_data,
        (
            'M0.000,-0.500 L0.000,0.500 L3.464,0.500 '
            'A 3.500,3.500 0 1 0 -3.500,0.000 L-2.500,0.000 '
            'A 2.500,2.500 0 0 1 2.449,-0.500 L0.000,-0.500 z'
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
