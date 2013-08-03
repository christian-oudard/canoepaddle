import math

from nose.tools import assert_equal

from canoepaddle import Pen
from canoepaddle.bounds import Bounds
from canoepaddle.shape import Circle, Rectangle

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def test_repr():
    assert_equal(
        repr(Bounds(-2, -3, 1, 2)),
        'Bounds(-2, -3, 1, 2)',
    )


def test_bounds_union():
    assert_equal(
        Bounds.union_all([
            Bounds(-2, -3, 1, 2),
            Bounds(0, 0, 3, 4),
        ]),
        Bounds(-2, -3, 3, 4)
    )


def test_circle_bounds():
    circle = Circle((1, 1), 1.5, 'color')
    assert_equal(
        circle.bounds(),
        Bounds(-0.5, -0.5, 2.5, 2.5)
    )


def test_rectangle_bounds():
    rectangle = Rectangle(1, 1, 3, 4, 'color')
    assert_equal(
        rectangle.bounds(),
        Bounds(1, 1, 4, 5)
    )


def test_line_segment_bounds():
    # No-width segment.
    p = Pen()
    p.move_to((1, 0))
    p.line_to((2, 3))

    line = p.paper.elements[0].segments[0]
    assert_equal(
        line.bounds(),
        Bounds(1, 0, 2, 3)
    )

    # Segment with a width.
    p = Pen()
    p.set_width(sqrt2)
    p.move_to((0, 0))
    p.line_to((5, 5))

    line = p.paper.elements[0].segments[0]
    assert_equal(
        line.bounds(),
        Bounds(-0.5, -0.5, 5.5, 5.5)
    )

    # Set a start angle, and the bounds change.
    p = Pen()
    p.set_width(math.sqrt(2))
    p.move_to((0, 0))
    p.line_to((5, 5), start_angle=0)

    line = p.paper.elements[0].segments[0]
    assert_equal(
        line.bounds(),
        Bounds(-1.0, 0.0, 5.5, 5.5)
    )


def test_arc_segment_bounds():
    # Arc which occupies its entire circle.
    p = Pen()
    p.move_to((1, 0))
    p.turn_to(90)
    p.arc_left(359, 1)

    arc = p.paper.elements[0].segments[0]
    assert_equal(
        arc.bounds(),
        Bounds(-1, -1, 1, 1)
    )

    # Arc which pushes the boundary only with the endpoints.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(30)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(30, center=(0, 0))

    arc = p.paper.elements[0].segments[0]
    assert_equal(
        arc.bounds(),
        Bounds(0.5, 0.5, sqrt3 / 2, sqrt3 / 2),
    )

    # Arc which pushes the boundary with the middle in one spot.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(90, center=(0, 0))

    arc = p.paper.elements[0].segments[0]
    assert_equal(
        arc.bounds(),
        Bounds(sqrt2 / 2, -sqrt2 / 2, 1, sqrt2 / 2)
    )

    # Arc which pushes the boundary with the middle in two spots.
    p = Pen()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(180, center=(0, 0))

    arc = p.paper.elements[0].segments[0]
    assert_equal(
        arc.bounds(),
        Bounds(-sqrt2 / 2, -sqrt2 / 2, 1, 1)
    )
