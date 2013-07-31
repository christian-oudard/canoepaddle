#TODO: offwidth errors can just start a new path instead.

from nose.plugins.skip import SkipTest

import os
import math
from nose.tools import (
    assert_equal,
    assert_almost_equal,
    assert_raises,
)

import vec
from grapefruit import Color

from util import assert_segments_equal, assert_points_equal
from canoepaddle import Pen
from canoepaddle.error import SegmentError
from canoepaddle.bounds import Bounds

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def _read_test_file(svg_filename):
    path = os.path.join(
        os.path.dirname(__file__),
        'files',
        svg_filename,
    )
    with open(path) as f:
        return f.read()


def assert_svg_file(path_data, svg_filename):
    content = _read_test_file(svg_filename)
    assert path_data in content


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
    p.set_width(2)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    path = p.paper.elements[0]
    assert_equal(
        path.draw(0),
        'M0,0 L5,0',
    )


def test_line_zero():
    p = Pen()
    p.set_width(1.0)
    p.line_forward(0)
    assert_equal(p.paper.elements, [])


def test_line_thick():
    p = Pen()
    p.set_width(2)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(0),
        'M0,-1 L0,1 L5,1 L5,-1 L0,-1 z',
    )

    p = Pen()
    p.set_width(1.0)
    p.turn_to(-45)
    p.line_forward(5)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        'M0.35,-0.35 L-0.35,0.35 L3.18,3.89 L3.89,3.18 L0.35,-0.35 z',
    )


def test_long_line_thick():
    p = Pen()
    p.set_width(2)
    p.move_to((0, 0))
    p.turn_to(0)
    for _ in range(2):
        p.line_forward(5)
        p.turn_right(90)
        p.line_forward(5)
        p.turn_left(90)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(0),
        'M0,-1 L0,1 L4,1 L4,6 L9,6 L9,10 L11,10 L11,4 L6,4 L6,-1 L0,-1 z'
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


def test_set_view_box():
    # Test that the view box gets set correctly.
    p = Pen()
    p.paper.set_view_box(-1, -1, 3, 3)

    # The view box is transformed into svg coordinates by flipping the
    # Y-coordinate and adjusting for height.
    svg_data = p.paper.format_svg()
    assert 'viewBox="-1 -2 3 3"' in svg_data

    p.paper.set_view_box(-10, -10, 20, 20)
    svg_data = p.paper.format_svg()
    assert 'viewBox="-10 -10 20 20"' in svg_data


def test_angle():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10, start_angle=-45, end_angle=30)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        'M-0.50,-0.50 L0.50,0.50 L9.13,0.50 L10.87,-0.50 L-0.50,-0.50 z',
    )

    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(10, start_angle=90, end_angle=None)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        'M0.00,-0.71 L0.00,0.71 L6.72,7.42 L7.42,6.72 L0.00,-0.71 z',
    )


def test_angle_error():
    # Creating an angle close to 0 is not allowed.
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(10, start_angle=0)
    )
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(10, end_angle=0)
    )

    # A combination of angles can also create a degenerate segment.
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        SegmentError,
        lambda: p.line_forward(1, start_angle=40, end_angle=-40)
    )


def test_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        (
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L2.57,5.45 '
            'L3.43,4.95 L0.29,-0.50 L-6.00,-0.50 z'
        ),
    )


def test_show_joints():
    p = Pen()
    p.show_joints = True

    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        (
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L0.29,-0.50 L-6.00,-0.50 z '
            'M0.29,-0.50 L-0.29,0.50 L2.57,5.45 L3.43,4.95 L0.29,-0.50 z'
        ),
    )


def test_show_nodes():
    p = Pen()
    p.show_nodes = True

    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)

    assert_equal(
        p.paper.svg_elements(3)[0].split('\n')[1:],
        [
            '<circle cx="-6.000" cy="0.000" r="0.125" fill="#008000" />',
            '<rect x="-0.125" y="-0.125" width="0.250" height="0.250" fill="#800000" />',
            '<circle cx="0.000" cy="0.000" r="0.125" fill="#008000" />',
            '<rect x="2.875" y="5.071" width="0.250" height="0.250" fill="#800000" />',
        ]
    )


def test_show_bones():
    p = Pen()
    p.show_bones = True

    p.set_width(1.0)
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)
    p.turn_right(60)
    p.line_forward(6)

    assert_equal(
        p.paper.svg_elements(2)[0].split('\n'),
        [
            (
                '<path d="M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L2.57,5.45 '
                'L3.43,4.95 L0.29,-0.50 L-6.00,-0.50 z" '
                'fill="none" stroke="#000000" stroke-width="0.0625" />'
            ),
            (
                '<path d="M-6.00,0.00 L0.00,0.00 L3.00,5.20" '
                'fill="none" stroke="#000000" stroke-width="0.0625" />'
            ),
        ]
    )


def test_flip():
    def stroke(p):
        p.move_to((0, 0))
        p.turn_to(180)
        p.move_forward(6)
        p.turn_to(0)
        p.line_forward(6)
        p.turn_right(60)
        p.line_forward(6)

    p = Pen()
    stroke(p)
    path = p.paper.elements[0]
    assert_equal(
        path.draw(2),
        'M-6.00,0.00 L0.00,0.00 L3.00,5.20'
    )

    p = Pen()
    p.flip_x()
    stroke(p)
    path = p.paper.elements[0]
    assert_equal(
        path.draw(2),
        'M6.00,0.00 L0.00,0.00 L-3.00,5.20'
    )

    p = Pen()
    p.flip_y()
    stroke(p)
    path = p.paper.elements[0]
    assert_equal(
        path.draw(2),
        'M-6.00,0.00 L0.00,0.00 L3.00,-5.20'
    )


def test_circle_bounds():
    raise SkipTest()


def test_rectangle_bounds():
    raise SkipTest()


def test_line_segment_bounds():
    raise SkipTest()
    # No-width segment.

    # Segment with a width.

    # Set an end angle, the bounds update.


def test_arc_segment_bounds():
    raise SkipTest()


def test_translate():
    p = Pen()
    p.set_width(1.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.arc_left(90, 3)
    p.turn_left(90)
    p.move_forward(3)
    p.circle(0.5)
    p.move_forward(3)
    p.square(1)

    p.paper.translate((1, 1))

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M1.0,-1.5 L1.0,-0.5 L4.0,-0.5 A 3.5,3.5 0 0 0 '
                '7.5,-4.0 L6.5,-4.0 A 2.5,2.5 0 0 1 4.0,-1.5 L1.0,-1.5 z" '
                'fill="#000000" />'
            ),
            '<circle cx="4.0" cy="-4.0" r="0.5" fill="#000000" />',
            '<rect x="0.5" y="-4.5" width="1.0" height="1.0" fill="#000000" />',
        ]
    )


def test_center_on_xy():
    p = Pen()
    p.set_width(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.move_to((2, 1))
    p.circle(1)

    p.paper.center_on_x(0)

    assert_equal(
        p.paper.svg_elements(0),
        [
            '<path d="M-2,-1 L-2,1 L2,1 L2,-1 L-2,-1 z" fill="#000000" />',
            '<circle cx="0" cy="-1" r="1" fill="#000000" />',
        ]
    )

    p.paper.center_on_y(0)

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M-2.0,-0.5 L-2.0,1.5 L2.0,1.5 L2.0,-0.5 L-2.0,-0.5 z" '
                'fill="#000000" />'
            ),
            '<circle cx="0.0" cy="-0.5" r="1.0" fill="#000000" />',
        ]
    )


def test_straight_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-90)
    p.line_forward(1)
    p.line_forward(1)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
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
        SegmentError,
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

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
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
        SegmentError,
        lambda: p.line_forward(3)
    )


def test_straight_joint_headings():
    raise SkipTest()

    # The math in calculating joint geometry can get numerically unstable
    # very close to straight joints at various headings.
    for heading_angle in range(0, 360):
        p = Pen()
        p.set_width(1.0)
        p.move_to((0, 0))
        p.turn_to(heading_angle)
        p.line_forward(10)
        p.line_forward(10)

        path = p.paper.elements[0]
        path.draw_thick(2)  # Doesn't crash.

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
    p.set_width(1.0)
    p.turn_to(0)
    p.move_to((0, 0))
    p.line_forward(3)
    p.move_to((0, 3))
    p.line_forward(3)

    assert_equal(
        [path.draw_thick(2) for path in p.paper.elements],
        [
            'M0.00,-0.50 L0.00,0.50 L3.00,0.50 L3.00,-0.50 L0.00,-0.50 z',
            'M0.00,-3.50 L0.00,-2.50 L3.00,-2.50 L3.00,-3.50 L0.00,-3.50 z',
        ]
    )


def test_last_slant_width():
    p = Pen()
    p.set_width(1.0)

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

    # Adding shapes on the end doesn't affect it. It still uses the last path.
    p.circle(1)
    assert_almost_equal(p.last_slant_width(), 2 / sqrt3)


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

    assert_equal(
        [path.draw(0) for path in p.paper.elements],
        [
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0',
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0',
        ],
    )


def test_arc_center():
    # Draw the same arcs as in test_arc, but using centers instead of radii.
    p = Pen()

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(90, center=(-5, 5))
    p.arc_right(270, center=(5, 5))

    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_right(90, center=(-5, -5))
    p.arc_left(270, center=(5, -5))

    assert_equal(
        [path.draw(0) for path in p.paper.elements],
        [
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0',
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0',
        ],
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

    assert_equal(
        [path.draw(0) for path in p.paper.elements],
        [
            'M-5,0 A 5,5 0 0 0 0,-5 A 5,5 0 1 1 5,0',
            'M-5,0 A 5,5 0 0 1 0,5 A 5,5 0 1 0 5,0',
        ],
    )


def test_arc_zero():
    # Zero-angle and zero-radius arcs have zero length, so they are not added.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_left(0, radius=1)
    assert_equal(p.paper.elements, [])

    p.arc_left(90, radius=0)
    assert_equal(p.paper.elements, [])


def test_arc_normalize():
    # Arc angles larger than 360 behave correctly.
    p = Pen()
    p.move_to((-5, 0))
    p.turn_to(0)
    p.arc_left(360 + 90, radius=5)

    path = p.paper.elements[0]
    assert_equal(
        path.draw(0),
        'M-5,0 A 5,5 0 0 0 0,-5'
    )


def test_arc_angle():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_left(90, radius=5, start_angle=45, end_angle=45)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(2),
        (
            'M0.53,-0.53 L-0.48,0.48 A 5.50,5.50 0 0 0 5.48,-5.48 '
            'L4.47,-4.47 A 4.50,4.50 0 0 1 0.53,-0.53 z'
        ),
    )


def test_arc_angle_error():
    # Endpoints with certain angles do not go all the way across the
    # stroke, and are disallowed.
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 10, start_angle=0)
    )
    p = Pen()
    p.set_width(1.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 10, end_angle=90)
    )
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, radius=5, start_angle=25)
    )

    # A combination of angles can also create a degenerate arc.
    p = Pen()
    p.set_width(1.0)
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

    p.set_width(1.0)
    p.arc_left(90, 5)

    p.set_width(2.0)
    assert_raises(
        SegmentError,
        lambda: p.arc_left(90, 5)
    )


def test_degenerate_arc():
    p = Pen()
    p.set_width(2.0)

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


def test_arc_line_joint():
    p = Pen()
    p.set_width(1.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.turn_left(90)
    p.arc_left(180, 3)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
        (
            'M0.000,-0.500 L0.000,0.500 L3.464,0.500 '
            'A 3.500,3.500 0 1 0 -3.500,0.000 L-2.500,0.000 '
            'A 2.500,2.500 0 0 1 2.449,-0.500 L0.000,-0.500 z'
        ),
    )


def test_arc_sweep_bug():
    p = Pen()
    p.set_width(2.0)

    p.move_to((3, 0))
    p.turn_to(90)
    p.arc_left(270, 3)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(0),
        'M2,0 L4,0 A 4,4 0 1 0 0,4 L0,2 A 2,2 0 1 1 2,0 z'
    )


def test_arc_arc_joint():
    top = (0, 5)
    left = (-2, 0)
    right = (2, 0)

    # Convex-convex.
    p = Pen()
    p.set_width(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_left(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_left(5)
    p.arc_to(right, end_angle=0)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
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
    p.set_width(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_right(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_right(5)
    p.arc_to(right, end_angle=0)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
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
    p.set_width(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_left(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_right(5)
    p.arc_to(right, end_angle=0)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
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
    p.set_width(1.0)

    p.move_to(left)
    p.turn_toward(top)
    p.turn_right(5)
    p.arc_to(top, start_angle=0)
    p.turn_toward(right)
    p.turn_left(5)
    p.arc_to(right, end_angle=0)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
        (
            'M-2.561,0.000 L-1.441,0.000 '
            'A 31.394,31.394 0 0 0 0.090,-3.656 '
            'A 30.394,30.394 0 0 1 1.477,0.000 '
            'L2.522,0.000 '
            'A 31.394,31.394 0 0 0 -0.144,-6.339 '
            'A 30.394,30.394 0 0 1 -2.561,0.000 z'
        )
    )


def test_arc_line_joint_bug():
    # When using arc_to, sometimes the b_left and b_right would get
    # reversed.
    p = Pen()
    p.set_width(1.0)

    p.move_to((0, 0))
    p.turn_to(90)
    p.arc_to((5, 5))
    p.turn_to(-90)
    p.line_forward(5)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(3),
        (
            'M-0.500,0.000 L0.500,0.000 '
            'A 4.500,4.500 0 0 1 4.500,-4.472 '
            'L4.500,0.000 L5.500,0.000 L5.500,-5.477 '
            'A 5.500,5.500 0 0 0 -0.500,0.000 z'
        )
    )


def test_various_joins():
    p = Pen()
    p.set_width(0.5)
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

    path = p.paper.elements[0]
    assert_svg_file(
        path.draw_thick(2),
        'test_various_joins.svg',
    )


def test_offwidth_arc_joins():
    # Join arcs and lines of different widths.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(0)

    p.set_width(0.8)
    p.line_forward(5)
    p.turn_left(45)
    p.set_width(3.0)
    p.arc_left(90, 5)

    p.turn_to(-180)
    p.line_forward(5)
    p.turn_left(45)
    p.set_width(0.8)
    p.arc_left(45, 5)

    p.turn_right(90)
    p.set_width(3.0)
    p.arc_right(90, 4)

    path = p.paper.elements[0]
    assert_svg_file(
        path.draw_thick(3),
        'test_offwidth_arc_joins.svg'
    )


def test_width_error():
    p = Pen()
    # Don't set width.
    p.line_forward(1)

    path = p.paper.elements[0]
    assert_raises(
        SegmentError,
        lambda: path.draw_thick(0),
    )


def test_repr():
    p = Pen()
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
            'center=(1.0, 1.0), radius=1, start_heading=0, end_heading=90)'
        )
    )


def test_circle():
    p = Pen()
    p.circle(1)

    assert_equal(
        p.paper.svg_elements(0),
        ['<circle cx="0" cy="0" r="1" fill="#000000" />'],
    )


def test_circle_color():
    p = Pen()

    p.move_to((0, 0))
    p.turn_to(0)

    p.turn_to(0)
    p.set_color((1.0, 0.0, 0.0))
    p.circle(1)
    p.move_forward(2)
    p.set_color((0.0, 1.0, 0.0))
    p.circle(1)
    p.move_forward(2)
    p.set_color((0.0, 0.0, 1.0))
    p.circle(1)

    assert_equal(
        p.paper.svg_elements(0),
        [
            '<circle cx="0" cy="0" r="1" fill="#ff0000" />',
            '<circle cx="2" cy="0" r="1" fill="#00ff00" />',
            '<circle cx="4" cy="0" r="1" fill="#0000ff" />',
        ]
    )


def test_circle_line_overlap():
    p = Pen()
    p.set_width(1.0)

    p.set_color((1.0, 0.0, 0.0))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.set_color((0.0, 1.0, 0.0))
    p.move_to((2, 2))
    p.circle(2)

    p.set_color((0.0, 0.0, 1.0))
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
            '<circle cx="2.0" cy="-2.0" r="2.0" fill="#00ff00" />',
            (
                '<path d="M0.0,-4.5 L0.0,-3.5 L4.0,-3.5 L4.0,-4.5 L0.0,-4.5 z" '
                'fill="#0000ff" />'
            ),
        ]
    )


def test_color_path():
    # Changing colors starts a new path.
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)

    p.set_color((1.0, 0.0, 0.0))
    p.line_forward(1)
    p.set_color((0.0, 1.0, 0.0))
    p.line_forward(1)
    p.set_color((0.0, 0.0, 1.0))
    p.line_forward(1)

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M0.0,-0.5 L0.0,0.5 L1.0,0.5 L1.0,-0.5 L0.0,-0.5 z" '
                'fill="#ff0000" />'
            ),
            (
                '<path d="M1.0,-0.5 L1.0,0.5 L2.0,0.5 L2.0,-0.5 L1.0,-0.5 z" '
                'fill="#00ff00" />'
            ),
            (
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
        p.set_width(2.0)
        p.set_color(color)
        p.move_to((0, 0))
        p.turn_to(0)
        p.line_forward(5)

        assert_equal(
            p.paper.svg_elements(0)[0],
            '<path d="M0,-1 L0,1 L5,1 L5,-1 L0,-1 z" fill="{}" />'.format(output)
        )


def test_color_joint():
    p = Pen()
    p.set_width(1.0)

    p.set_color('red')
    p.move_to((-6, 0))
    p.turn_to(0)
    p.line_forward(6)

    p.set_color('green')
    p.turn_right(60)
    p.line_forward(6)

    assert_equal(
        [path.draw_thick(2) for path in p.paper.elements],
        [
            'M-6.00,-0.50 L-6.00,0.50 L-0.29,0.50 L0.29,-0.50 L-6.00,-0.50 z',
            'M0.29,-0.50 L-0.29,0.50 L2.57,5.45 L3.43,4.95 L0.29,-0.50 z',
        ]
    )


def test_arc_joint_continue():
    p = Pen()
    p.set_width(2.0)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_left(90, 5)
    p.arc_left(90, 5)

    p.move_to((0, 0))
    p.turn_to(0)

    p.arc_right(90, 5)
    p.arc_right(90, 5)

    assert_equal(
        [path.draw_thick(0) for path in p.paper.elements],
        [
            (
                'M0,-1 L0,1 A 6,6 0 0 0 6,-5 A 6,6 0 0 0 0,-11 '
                'L0,-9 A 4,4 0 0 1 4,-5 A 4,4 0 0 1 0,-1 z'
            ),
            (
                'M0,-1 L0,1 A 4,4 0 0 1 4,5 A 4,4 0 0 1 0,9 '
                'L0,11 A 6,6 0 0 0 6,5 A 6,6 0 0 0 0,-1 z'
            )
        ]
    )


def test_zero_length_side():
    # It is possible and legal to create a segment that just barely goes to
    # zero on one side.
    p = Pen()
    p.set_width(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(1.0, end_angle=45)

    path = p.paper.elements[0]
    assert_equal(
        path.draw_thick(0),
        'M0,-1 L0,1 L2,-1 L0,-1 z',
    )
