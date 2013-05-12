import math

#from nose.tools import (
#    assert_equal,
#    assert_almost_equal,
#    assert_raises,
#)

from canoepaddle import Pen, Paper, Segment, Point

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

def test_stroke_to_coordinate():
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(45)
    p.stroke_to_y(3)
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
        p.stroke_to_y(y * 2)
        assert_points_equal(p.position, (x * 2, y * 2))

        p.move_to((0, 0))
        p.turn_toward((x, y))
        p.stroke_to_x(x * 3)
        assert_points_equal(p.position, (x * 3, y * 3))

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

def test_straight_joint():
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(-90)
    p.stroke_forward(1)
    p.stroke_forward(1)
    path_data = p.paper.to_svg_path_thick(precision=2)
    assert_equal(
        path_data,
        'M0.50,0.00 L-0.50,-0.00 L-0.50,1.00 L-0.50,2.00 L0.50,2.00 L0.50,1.00 z',
    )

    # Make a line turn back on itself; it doesn't work.
    p = Pen()
    p.set_width(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.stroke_forward(10)
    p.turn_right(180)
    p.stroke_forward(10)
    assert_raises(
        ValueError,
        lambda: p.paper.to_svg_path_thick(),
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
    assert_raises(
        ValueError,
        lambda: p.stroke_forward(3)
    )

def test_calc_joint_angle():
    paper = Paper()

    # 90 degree turn, same width.
    assert_almost_equal(
        paper.calc_joint_angle(
            Segment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            Segment(
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
            Segment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            Segment(
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
            Segment(
                Point(0, 0),
                Point(10, 0),
                width=1,
            ),
            Segment(
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
        #print(heading_angle)
        p = Pen()
        p.set_width(1.0)
        p.move_to((0, 0))
        p.turn_to(heading_angle)
        p.stroke_forward(10)
        p.stroke_forward(10)
        path_data = p.paper.to_svg_path_thick(precision=2) # Doesn't crash.

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

def test_arc():
    p = Pen()
    p.move_to((0, 0))
    p.arc_to((5, 5), 5)
    path_data = p.paper.to_svg_path(precision=2)
    assert_equal(
        path_data,
        'M0.00,0.00 A 5.00,5.00 0 0 0 5.00,-5.00',
    )


if __name__ == '__main__':
    import traceback

    def assert_equal(a, b):
        assert a == b, '{} != {}'.format(a, b)

    def assert_almost_equal(a, b, places=12):
        _epsilon = 10**-places
        assert abs(a - b) < _epsilon, '{} != {}'.format(a, b)

    def assert_raises(exc_class, func):
        try:
            func()
        except Exception as e:
            assert isinstance(e, exc_class)
        else:
            raise AssertionError('No exception raised.')

    results = []

    for value in globals().values():
        if hasattr(value, '__call__') and value.__name__.startswith('test_'):
            print(value.__name__)
            try:
                value()
            except AssertionError:
                results.append('FAIL')
                traceback.print_exc()
            except:
                results.append('ERROR')
                traceback.print_exc()
            else:
                results.append('OK')
            print(results[-1])
    if all(r == 'OK' for r in results):
        print('ALL PASS')

