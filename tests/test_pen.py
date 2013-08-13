import math

from nose.plugins.skip import SkipTest
from nose.tools import (
    assert_equal,
    assert_almost_equal,
    assert_raises,
)

import vec
from grapefruit import Color

from util import (
    assert_segments_equal,
    assert_points_equal,
    assert_svg_file,
    assert_path_data,
    sqrt2,
    sqrt3,
)
from canoepaddle.pen import Pen
from canoepaddle.mode import (
    FillMode,
    StrokeFillMode,
    StrokeOutlineMode,
)
from canoepaddle.point import Point
from canoepaddle.error import SegmentError


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


def test_line():
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        'M0,0 L5,0'
    )


def test_line_zero():
    p = Pen()
    p.stroke_mode(1.0)
    p.line_forward(0)
    assert_equal(p.paper.elements, [])


def test_line_thick():
    p = Pen()
    p.stroke_mode(2)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L5,1 L5,-1 L0,-1 z'
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.turn_to(-45)
    p.line_forward(5)

    assert_path_data(
        p, 2,
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 L0.35,-0.35 z'
    )


def test_long_line_thick():
    p = Pen()
    p.stroke_mode(2)
    p.move_to((0, 0))
    p.turn_to(0)
    for _ in range(2):
        p.line_forward(5)
        p.turn_right(90)
        p.line_forward(5)
        p.turn_left(90)

    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L4,1 L4,6 L9,6 L9,10 L11,10 L11,4 L6,4 L6,-1 L0,-1 z'
    )


def test_line_to_coordinate():
    p = Pen()
    p.fill_mode()
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
        p.fill_mode()

        p.move_to((0, 0))
        p.turn_toward((x, y))
        p.line_to_y(y * 2)
        assert_points_equal(p.position, (x * 2, y * 2))

        p.move_to((0, 0))
        p.turn_toward((x, y))
        p.line_to_x(x * 3)
        assert_points_equal(p.position, (x * 3, y * 3))


def test_angle():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10, start_angle=-45, end_angle=30)

    assert_path_data(
        p, 2,
        'M-0.50,-0.50 L0.50,0.50 L9.13,0.50 L10.87,-0.50 L-0.50,-0.50 z'
    )

    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(10, start_angle=90, end_angle=None)

    assert_path_data(
        p, 2,
        'M0.00,-0.71 L0.00,0.71 L6.72,7.42 L7.42,6.72 L0.00,-0.71 z'
    )


def test_angle_error():
    # Creating an angle close to 0 is not allowed.
    p = Pen()
    p.stroke_mode(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(10, start_angle=0)
    )
    p = Pen()
    p.stroke_mode(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(10, end_angle=0)
    )

    # A combination of angles can also create a degenerate segment.
    p = Pen()
    p.stroke_mode(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(1, start_angle=40, end_angle=-40)
    )


def test_joint():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)

    assert_path_data(
        p, 2,
        (
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L2.57,5.45 '
            'L3.43,4.95 L0.29,-0.50 L-6.00,-0.50 z'
        ),
    )


def test_joint_loop():
    p = Pen()

    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)

    # Draw a square.
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        (
            'M-1,1 L6,1 L6,-6 L-1,-6 L-1,1 z '
            'M1,-1 L1,-4 L4,-4 L4,-1 L1,-1 z'
        )
    )


def test_joint_loop_color():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(0)

    # Draw a square with one side a different color. It joins to the
    # beginning correctly.
    p.stroke_mode(2.0, color='black')
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.stroke_mode(2.0, color='red')
    p.line_forward(5)

    assert_equal(len(p.paper.elements), 1)

    assert_path_data(
        p, 0,
        [
            'M1,-1 L-1,1 L6,1 L6,-6 L-1,-6 L1,-4 L4,-4 L4,-1 L1,-1 z',
            'M1,-4 L-1,-6 L-1,1 L1,-1 L1,-4 z',
        ]
    )


def test_joint_loop_multiple():
    p = Pen()
    p.stroke_mode(0.2)

    def square():
        p.turn_to(180)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)
        p.turn_left(90)
        p.line_forward(1)

    p.move_to((0, 0))
    square()
    p.move_to((2, 0))
    square()

    assert_path_data(
        p, 1,
        (
            'M0.1,-0.1 L-1.1,-0.1 L-1.1,1.1 L0.1,1.1 L0.1,-0.1 z '
            'M-0.1,0.1 L-0.1,0.9 L-0.9,0.9 L-0.9,0.1 L-0.1,0.1 z '
            'M2.1,-0.1 L0.9,-0.1 L0.9,1.1 L2.1,1.1 L2.1,-0.1 z '
            'M1.9,0.1 L1.9,0.9 L1.1,0.9 L1.1,0.1 L1.9,0.1 z'
        )
    )


def test_straight_joint():
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.line_forward(3)

    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L3,1 L6,1 L6,-1 L3,-1 L0,-1 z'
    )


def test_break_stroke():
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.break_stroke()
    p.line_forward(3)

    assert_path_data(
        p, 0,
        [
            'M0,-1 L0,1 L3,1 L3,-1 L0,-1 z',
            'M3,-1 L3,1 L6,1 L6,-1 L3,-1 z',
        ]
    )


def test_turn_back_error():
    # Make a line turn back on itself; it doesn't work.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(180)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(10),
    )


def test_offwidth_joint():
    p = Pen()
    p.stroke_mode(1.0)
    p.turn_to(0)
    p.move_forward(-3)
    p.line_forward(3)
    p.stroke_mode(0.5)
    p.turn_left(90)
    p.line_forward(3)

    assert_path_data(
        p, 2,
        (
            'M-3.00,-0.50 L-3.00,0.50 L0.25,0.50 L0.25,-3.00 '
            'L-0.25,-3.00 L-0.25,-0.50 L-3.00,-0.50 z'
        ),
    )


def test_offwidth_joint_error():
    p = Pen()
    p.stroke_mode(1.0)
    p.turn_to(0)
    p.line_forward(3)
    p.stroke_mode(0.5)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(3)
    )


def test_straight_joint_headings():
    raise SkipTest()

    # The math in calculating joint geometry can get numerically unstable
    # very close to straight joints at various headings.
    for heading_angle in range(0, 360):
        p = Pen()
        p.stroke_mode(1.0)
        p.move_to((0, 0))
        p.turn_to(heading_angle)
        p.line_forward(10)
        p.line_forward(10)

        path = p.paper.elements[0]
        path.render_path(2)  # Doesn't crash.

        # Check that the joint angle is 90 degrees from the heading.
        assert_equal(len(p.paper.elements), 1)
        segments = p.paper.elements[0].segments
        assert_equal(len(segments), 2)
        s0, s1 = segments

        target_angle = (heading_angle + 90) % 180

        joint_angle = math.degrees(vec.heading(vec.vfrom(s0.b_right, s0.b_left)))
        assert_almost_equal(joint_angle % 180, target_angle)

        joint_angle = math.degrees(vec.heading(vec.vfrom(s1.a_right, s1.a_left)))
        assert_almost_equal(joint_angle % 180, target_angle)


def test_multiple_strokes():
    p = Pen()
    p.stroke_mode(1.0)
    p.turn_to(0)
    p.move_to((0, 0))
    p.line_forward(3)
    p.move_to((0, 3))
    p.line_forward(3)

    assert_path_data(
        p, 1,
        (
            'M0.0,-0.5 L0.0,0.5 L3.0,0.5 L3.0,-0.5 L0.0,-0.5 z '
            'M0.0,-3.5 L0.0,-2.5 L3.0,-2.5 L3.0,-3.5 L0.0,-3.5 z'
        )
    )


def test_last_slant_width():
    p = Pen()
    p.stroke_mode(1.0)

    # If we haven't drawn any path segments yet, there is no last slant width.
    assert_equal(p.last_slant_width(), None)

    # 45 degree slant.
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(1, end_angle=90)
    assert_almost_equal(p.last_slant_width(), sqrt2)

    # 30 degree slant.
    p.move_to((0, 0))
    p.turn_to(30)
    p.line_forward(1, end_angle=90)
    assert_almost_equal(p.last_slant_width(), 2 / sqrt3)


def test_arc():
    # Draw arcs with all four combinations of sweep and direction flags.
    p = Pen()
    p.fill_mode()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5)
    p.arc_right(270, radius=5)

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_right(90, radius=5)
    p.arc_left(270, radius=5)

    assert_path_data(
        p, 0,
        (
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0 '
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0'
        )
    )


def test_arc_center():
    # Draw the same arcs as in test_arc, but using centers instead of radii.
    p = Pen()
    p.fill_mode()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(90, center=(-5, 5))
    p.arc_right(270, center=(5, 5))

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_right(90, center=(-5, -5))
    p.arc_left(270, center=(5, -5))

    assert_path_data(
        p, 0,
        (
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0 '
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0'
        ),
    )


def test_arc_to():
    # Make the same arcs as test_arc, but using the destination points instead
    # of the angles.
    p = Pen()
    p.fill_mode()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_to((0, 5))
    p.arc_to((5, 0))

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_to((0, -5))
    p.arc_to((5, 0))

    assert_path_data(
        p, 0,
        (
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0 '
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0'
        ),
    )


def test_arc_zero():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)

    # Zero-angle and zero-radius arcs have zero length, so they are not added.
    p.arc_left(0, radius=1)
    assert_equal(p.paper.elements, [])

    p.arc_left(90, radius=0)
    assert_equal(p.paper.elements, [])


def test_arc_normalize():
    # Arc angles larger than 360 behave correctly.
    p = Pen()
    p.fill_mode()
    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(360 + 90, radius=5)

    assert_path_data(
        p, 0,
        'M-5,0 A 5,5 0 0 0 0,-5'
    )


def test_arc_angle():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5, start_angle=45, end_angle=45)

    assert_path_data(
        p, 2,
        (
            'M0.53,-0.53 L-0.48,0.48 A 5.50,5.50 0 0 0 5.48,-5.48 '
            'L4.47,-4.47 A 4.50,4.50 0 0 1 0.53,-0.53 z'
        ),
    )


def test_arc_angle_error():
    # Endpoints with certain angles do not go all the way across the
    # stroke, and are disallowed.
    p = Pen()
    p.stroke_mode(1.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 10, start_angle=0)
    )
    p = Pen()
    p.stroke_mode(1.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 10, end_angle=90)
    )
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, radius=5, start_angle=25)
    )

    # A combination of angles can also create a degenerate arc.
    p = Pen()
    p.stroke_mode(1.0)
    p.turn_toward((1, 0))
    p.turn_left(1)
    assert_raises(
        SegmentError,
        lambda: p.arc_to((1, 0), start_angle=40, end_angle=-40)
    )


def test_offwidth_arc_joint_error():
    # Try to create an impossible joint between concentric arcs of
    # different widths.
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(0)

    p.stroke_mode(1.0)
    p.arc_left(90, 5)

    p.stroke_mode(2.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 5)
    )


def test_arc_joint_error_nonconcentric():
    # Join two arcs together illegally, but don't make them concentric.
    p = Pen()

    p.move_to((0, -1))
    p.stroke_mode(1.0)
    p.arc_to((1, 0), center=(0, 0))
    p.stroke_mode(0.1)
    assert_raises(
        SegmentError,
        lambda: p.arc_to((0, 1), center=(0.1, 0)),
    )


def test_degenerate_arc():
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((-5, 0))
    p.turn_to(0)
    assert_raises(
        SegmentError,
        lambda: p.arc_to(
            (5, 0),
            center=(0, -200),
            start_angle=-5,
            end_angle=5,
        )
    )


def test_arc_pie_slice():
    # Draw a "pie slice" arc that is wide enough to reach all the way to the
    # arc center.
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0.5, 0))
    p.turn_to(90)
    p.arc_left(90, 0.5)

    assert_path_data(
        p, 0,
        'M0,0 L1,0 A 1,1 0 0 0 0,-1 L0,0 z'
    )


def test_arc_start_angle_bug():
    # Some arcs are not reporting their start and end angles correctly.

    # Set up positions on a circle at angles -120 and 30
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.turn_to(30)
    p.move_forward(3)
    p1 = p.position
    p.turn_left(90)
    h1 = p.heading

    p.move_to((0, 0))
    p.turn_to(-120)
    p.move_forward(3)
    p2 = p.position

    # Create an arc using arc_left.
    p = Pen()
    p.fill_mode()

    p.move_to(p1)
    p.turn_to(h1)
    p.arc_left(210, 3)
    arc = p.paper.elements[0].segments[0]
    assert_almost_equal(arc.start_heading, 120)
    assert_almost_equal(arc.end_heading, 330)

    # Create the same arc using arc_to.
    p = Pen()
    p.fill_mode()

    p.move_to(p1)
    p.turn_to(h1)
    p.arc_to(p2)
    arc = p.paper.elements[0].segments[0]
    assert_almost_equal(arc.start_heading, 120)
    assert_almost_equal(arc.end_heading, 330)


def test_arc_line_joint():
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.turn_left(90)
    p.arc_left(180, 3)

    assert_path_data(
        p, 3,
        (
            'M0.000,-0.500 L0.000,0.500 L3.464,0.500 '
            'A 3.500,3.500 0 1 0 -3.500,0.000 L-2.500,0.000 '
            'A 2.500,2.500 0 0 1 2.449,-0.500 L0.000,-0.500 z'
        ),
    )


def test_arc_sweep_bug():
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((3, 0))
    p.turn_to(90)
    p.arc_left(270, 3)

    assert_path_data(
        p, 0,
        'M2,0 L4,0 A 4,4 0 1 0 0,4 L0,2 A 2,2 0 1 1 2,0 z'
    )


def test_arc_arc_joint():
    top = (0, 5)
    left = (-2, 0)
    right = (2, 0)

    # Convex-convex.
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_left(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_left(5)
    p.arc_to(right, end_angle=0)

    assert_path_data(
        p, 3,
        (
            'M-2.522,0.000 L-1.477,0.000 '
            'A 30.394,30.394 0 0 1 0.000,-3.853 '
            'A 30.394,30.394 0 0 1 1.477,0.000 '
            'L2.522,0.000 '
            'A 31.394,31.394 0 0 0 0.000,-6.076 '
            'A 31.394,31.394 0 0 0 -2.522,0.000 z'
        )
    )

    # Concave-concave.
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_right(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_right(5)
    p.arc_to(right, end_angle=0)

    assert_path_data(
        p, 3,
        (
            'M-2.561,0.000 L-1.441,0.000 '
            'A 31.394,31.394 0 0 0 0.000,-3.400 '
            'A 31.394,31.394 0 0 0 1.441,0.000 '
            'L2.561,0.000 '
            'A 30.394,30.394 0 0 1 0.000,-6.923 '
            'A 30.394,30.394 0 0 1 -2.561,0.000 z'
        )
    )

    # Convex-concave.
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_left(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_right(5)
    p.arc_to(right, end_angle=0)

    assert_path_data(
        p, 3,
        (
            'M-2.522,0.000 L-1.477,0.000 '
            'A 30.394,30.394 0 0 1 -0.090,-3.656 '
            'A 31.394,31.394 0 0 0 1.441,0.000 '
            'L2.561,0.000 '
            'A 30.394,30.394 0 0 1 0.144,-6.339 '
            'A 31.394,31.394 0 0 0 -2.522,0.000 z'
        )
    )

    # Concave-convex.
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_right(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_left(5)
    p.arc_to(right, end_angle=0)

    assert_path_data(
        p, 3,
        (
            'M-2.561,0.000 L-1.441,0.000 '
            'A 31.394,31.394 0 0 0 0.090,-3.656 '
            'A 30.394,30.394 0 0 1 1.477,0.000 '
            'L2.522,0.000 '
            'A 31.394,31.394 0 0 0 -0.144,-6.339 '
            'A 30.394,30.394 0 0 1 -2.561,0.000 z'
        )
    )


def test_arc_arc_joint_off_radius():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(180, 1)
    p.arc_left(90, 2)

    assert_path_data(
        p, 1,
        (
            'M0.0,-0.5 L0.0,0.5 '
            'A 1.5,1.5 0 0 0 0.0,-2.5 '
            'A 2.5,2.5 0 0 0 -2.5,0.0 '
            'L-1.5,0.0 '
            'A 1.5,1.5 0 0 1 0.0,-1.5 '
            'A 0.5,0.5 0 0 1 0.0,-0.5 z'
        )
    )


def test_arc_line_joint_bug():
    # When using arc_to, sometimes the b_left and b_right would get
    # reversed.
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to((0, 0))
    p.turn_to(90)
    p.arc_to((5, 5))
    p.turn_to(-90)
    p.line_forward(5)

    assert_path_data(
        p, 3,
        (
            'M-0.500,0.000 L0.500,0.000 '
            'A 4.500,4.500 0 0 1 4.500,-4.472 '
            'L4.500,0.000 L5.500,0.000 L5.500,-5.477 '
            'A 5.500,5.500 0 0 0 -0.500,0.000 z'
        )
    )


def test_various_joins():
    p = Pen()
    p.stroke_mode(0.5)
    p.move_to((-2, 0))
    p.turn_to(0)
    p.line_forward(1)
    p.turn_left(90)
    p.line_forward(1)
    p.turn_right(90)
    p.arc_right(90, 1)
    p.arc_left(90, 1)
    p.turn_left(90)
    p.line_forward(1)

    p.paper.set_view_box(-3, -3, 6, 6)

    assert_svg_file(
        p, 2,
        'test_various_joins.svg',
    )


def test_offwidth_arc_joins():
    # Join arcs and lines of different widths.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.stroke_mode(0.8)
    p.line_forward(5)
    p.turn_left(45)
    p.stroke_mode(3.0)
    p.arc_left(90, 5)

    p.turn_to(-180)
    p.line_forward(5)
    p.turn_left(45)
    p.stroke_mode(0.8)
    p.arc_left(45, 5)

    p.turn_right(90)
    p.stroke_mode(3.0)
    p.arc_right(90, 4)

    assert_svg_file(
        p, 3,
        'test_offwidth_arc_joins.svg'
    )


def test_repr():
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(1)
    p.arc_left(90, 1)

    path = p.paper.elements[0]
    line, arc = path.segments
    assert_equal(
        repr(line),
        'LineSegment(a=Point(x=0, y=0), b=Point(x=1.0, y=0.0))'
    )
    assert_equal(
        repr(arc),
        (
            'ArcSegment(a=Point(x=1.0, y=0.0), b=Point(x=2.0, y=0.9999999999999999), '
            'center=Point(x=1.0, y=1.0), radius=1, start_heading=0, end_heading=90)'
        )
    )


def test_circle():
    p = Pen()
    p.fill_mode()
    p.circle(1)

    assert_equal(
        p.paper.svg_elements(0),
        ['<path d="M1,0 A 1,1 0 0 0 -1,0 A 1,1 0 0 0 1,0 z" fill="#000000" />']
    )


def test_circle_degenerate():
    p = Pen()
    p.stroke_mode(2.0)
    p.circle(1)
    assert_equal(
        p.paper.svg_elements(0),
        ['<path d="M2,0 A 2,2 0 0 0 -2,0 A 2,2 0 0 0 2,0 z" fill="#000000" />']
    )


def test_circle_color():
    p = Pen()
    p.move_to((0, 0))

    p.turn_to(0)
    p.fill_mode((1.0, 0.0, 0.0))
    p.circle(1)
    p.move_forward(2)
    p.fill_mode((0.0, 1.0, 0.0))
    p.circle(1)
    p.move_forward(2)
    p.fill_mode((0.0, 0.0, 1.0))
    p.circle(1)

    assert_equal(
        p.paper.svg_elements(0),
        [
            '<path d="M1,0 A 1,1 0 0 0 -1,0 A 1,1 0 0 0 1,0 z" fill="#ff0000" />',
            '<path d="M3,0 A 1,1 0 0 0 1,0 A 1,1 0 0 0 3,0 z" fill="#00ff00" />',
            '<path d="M5,0 A 1,1 0 0 0 3,0 A 1,1 0 0 0 5,0 z" fill="#0000ff" />',
        ]
    )


def test_circle_line_overlap():
    # Draw a circle that is above one line but below the other line.
    p = Pen()

    p.stroke_mode(1.0, color=(1.0, 0.0, 0.0))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.fill_mode(color=(0.0, 1.0, 0.0))
    p.move_to((2, 2))
    p.circle(2)

    p.stroke_mode(1.0, color=(0.0, 0.0, 1.0))
    p.move_to((0, 4))
    p.turn_to(0)
    p.line_forward(4)

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M0.0,-0.5 L0.0,0.5 L4.0,0.5 L4.0,-0.5 L0.0,-0.5 z" '
                'fill="#ff0000" />'
            ),
            (
                '<path d="M4.0,-2.0 A 2.0,2.0 0 0 0 0.0,-2.0 '
                'A 2.0,2.0 0 0 0 4.0,-2.0 z" fill="#00ff00" />'
            ),
            (
                '<path d="M0.0,-4.5 L0.0,-3.5 L4.0,-3.5 L4.0,-4.5 L0.0,-4.5 z" '
                'fill="#0000ff" />'
            ),
        ]
    )


def test_color_path():
    # Changing colors starts a new path.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.stroke_mode(1.0, (1.0, 0.0, 0.0))
    p.line_forward(1)
    p.stroke_mode(1.0, (0.0, 1.0, 0.0))
    p.line_forward(1)
    p.stroke_mode(1.0, (0.0, 0.0, 1.0))
    p.line_forward(1)

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M0.0,-0.5 L0.0,0.5 L1.0,0.5 L1.0,-0.5 L0.0,-0.5 z" '
                'fill="#ff0000" />'
                '<path d="M1.0,-0.5 L1.0,0.5 L2.0,0.5 L2.0,-0.5 L1.0,-0.5 z" '
                'fill="#00ff00" />'
                '<path d="M2.0,-0.5 L2.0,0.5 L3.0,0.5 L3.0,-0.5 L2.0,-0.5 z" '
                'fill="#0000ff" />'
            ),
        ]
    )


def test_color_formats():
    for color, output in [
        (
            (1.0, 0.0, 0.0),
            '#ff0000',
        ),
        (
            Color.NewFromHtml('red'),
            '#ff0000',
        ),
        (
            'green',
            '#008000',
        ),
        (
            '#123456',
            '#123456',
        ),
    ]:
        p = Pen()
        p.stroke_mode(2.0, color)
        p.move_to((0, 0))
        p.turn_to(0)
        p.line_forward(5)

        assert_equal(
            p.paper.svg_elements(0)[0],
            '<path d="M0,-1 L0,1 L5,1 L5,-1 L0,-1 z" fill="{}" />'.format(output)
        )


def test_color_joint():
    p = Pen()

    p.stroke_mode(1.0, 'red')
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)

    p.stroke_mode(1.0, 'green')
    p.turn_right(60)
    p.line_forward(6)

    assert_path_data(
        p, 2,
        [
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L0.29,-0.50 L-6.00,-0.50 z',
            'M0.29,-0.50 L-0.29,0.50 L2.57,5.45 L3.43,4.95 L0.29,-0.50 z',
        ]
    )


def test_arc_joint_continue():
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_left(90, 5)
    p.arc_left(90, 5)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_right(90, 5)
    p.arc_right(90, 5)

    assert_path_data(
        p, 0,
        (
            'M0,-1 L0,1 A 6,6 0 0 0 6,-5 A 6,6 0 0 0 0,-11 '
            'L0,-9 A 4,4 0 0 1 4,-5 A 4,4 0 0 1 0,-1 z '
            'M0,-1 L0,1 A 4,4 0 0 1 4,5 A 4,4 0 0 1 0,9 '
            'L0,11 A 6,6 0 0 0 6,5 A 6,6 0 0 0 0,-1 z'
        ),
    )


def test_arc_joint_numerical():
    # Sometimes arc joints can miss the mark if they have odd float numbers.
    p = Pen()
    p.stroke_mode(0.5)
    p.move_to((-26.685559703113075, 65.00539003547281))
    p.turn_to(202.85281173472714)
    p.arc_right(180, 1)
    # This shouldn't error:
    p.arc_right(50.443252846269075, center=(0.5, 0.5))


def test_zero_length_side():
    # It is possible and legal to create a segment that just barely goes to
    # zero on one side.
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(1.0, end_angle=45)

    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L2,-1 L0,-1 z',
    )


def test_mode():
    # Fill mode square.
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        'M0,0 L5,0 L5,-5 L0,-5 L0,0 z',
    )


def test_mode_repr():
    assert_equal(
        repr(FillMode('black')),
        "FillMode('black')"
    )


def test_mode_error():
    p = Pen()
    # Don't set a mode.
    assert_raises(
        AttributeError,
        lambda: p.line_forward(1)
    )


def test_change_mode():
    # Change mode but don't change colors. It starts a new path.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.stroke_mode(2.0, 'black')
    p.line_forward(5)
    p.fill_mode('black')
    p.line_forward(5)

    assert_equal(
        p.paper.svg_elements(0),
        [
            '<path d="M0,-1 L0,1 L5,1 L5,-1 L0,-1 z" fill="#000000" />',
            '<path d="M5,0 L10,0" fill="#000000" />',
        ]
    )


def test_outline():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)
    p.outline_mode(1.0, 0.2)
    p.line_forward(3)

    assert_path_data(
        p, 1,
        (
            'M-0.1,-0.6 L-0.1,0.6 L3.1,0.6 L3.1,-0.6 L-0.1,-0.6 z '
            'M0.1,-0.4 L2.9,-0.4 L2.9,0.4 L0.1,0.4 L0.1,-0.4 z'
        )
    )


def test_change_outline_width():
    # Changing the outline width starts a new path.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)
    p.outline_mode(1.0, 0.2)
    p.line_forward(3)
    p.outline_mode(1.0, 0.4)
    p.line_forward(3)

    assert_path_data(
        p, 1,
        [
            (
                'M-0.1,-0.6 L-0.1,0.6 L3.1,0.6 L3.1,-0.6 L-0.1,-0.6 z '
                'M0.1,-0.4 L2.9,-0.4 L2.9,0.4 L0.1,0.4 L0.1,-0.4 z'
            ),
            (
                'M2.8,-0.7 L2.8,0.7 L6.2,0.7 L6.2,-0.7 L2.8,-0.7 z '
                'M3.2,-0.3 L5.8,-0.3 L5.8,0.3 L3.2,0.3 L3.2,-0.3 z'
            ),
        ]
    )


def test_save_mode():
    p = Pen()
    p.stroke_mode(2.0, 'red')
    old_mode = p.mode
    p.line_forward(5)
    p.fill_mode('blue')
    p.square(2)
    p.set_mode(old_mode)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        [
            'M0,-1 L0,1 L5,1 L5,-1 L0,-1 z',
            'M4,1 L6,1 L6,-1 L4,-1 L4,1 z',
            'M5,-1 L5,1 L10,1 L10,-1 L5,-1 z',
        ]
    )


def test_stroke_fill_mode():
    p = Pen()
    p.set_mode(StrokeFillMode(0.2, 'black', 'red'))
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(180, 5)
    assert_equal(
        p.paper.svg_elements(1)[0],
        (
            '<path d="M0.0,0.0 A 5.0,5.0 0 0 0 0.0,-10.0" fill="#ff0000" />'
            '<path d="M0.0,-0.1 L0.0,0.1 A 5.1,5.1 0 0 0 0.0,-10.1 '
            'L0.0,-9.9 A 4.9,4.9 0 0 1 0.0,-0.1 z" fill="#000000" />'
        )
    )


def test_stroke_outline_mode():
    p = Pen()
    p.set_mode(StrokeOutlineMode(1.0, 0.2, 'red', 'black'))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    assert_equal(
        p.paper.svg_elements(1)[0],
        (
            '<path d="M0.0,-0.5 L0.0,0.5 L5.0,0.5 L5.0,-0.5 L0.0,-0.5 z" '
            'fill="#ff0000" />'
            '<path d="M-0.1,-0.6 L-0.1,0.6 L5.1,0.6 L5.1,-0.6 L-0.1,-0.6 z '
            'M0.1,-0.4 L4.9,-0.4 L4.9,0.4 L0.1,0.4 L0.1,-0.4 z" '
            'fill="#000000" />'
        )
    )


def test_log():
    p = Pen()
    p.stroke_mode(1)
    p.move_to(Point(-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)
    assert_equal(
        p.log(),
        [
            'stroke_mode(1)',
            'move_to((-6, 0))',  # Points are converted to tuples.
            'turn_to(0)',
            'line_forward(6)',
            'turn_right(60)',
            'line_forward(6)',
        ]
    )
