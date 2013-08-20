import math

from nose.tools import assert_equal

from util import assert_path_data
from canoepaddle import Pen
from canoepaddle.bounds import Bounds

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def test_repr():
    assert_equal(
        repr(Bounds(-2, -3, 1, 2)),
        'Bounds(-2, -3, 1, 2)',
    )


def test_iter():
    bounds = Bounds(1, 2, 3, 4)
    assert_equal(
        tuple(bounds),
        (1, 2, 3, 4),
    )


def test_bounds_union():
    assert_equal(
        Bounds.union_all([
            Bounds(-2, -3, 1, 2),
            Bounds(0, 0, 3, 4),
        ]),
        Bounds(-2, -3, 3, 4)
    )


def test_draw_bounds():
    p = Pen()
    p.fill_mode()
    Bounds(-2, -3, 1, 2).draw(p)

    assert_path_data(
        p, 0,
        'M-2,3 L1,3 L1,-2 L-2,-2 L-2,3 z'
    )


def test_circle_bounds():
    p = Pen()
    p.fill_mode()
    p.move_to((1, 1))
    p.circle(1.5)

    assert_equal(
        p.paper.bounds(),
        Bounds(-0.5, -0.5, 2.5, 2.5)
    )


def test_square_bounds():
    p = Pen()
    p.fill_mode()
    p.move_to((1, 1))
    p.square(4)

    assert_equal(
        p.paper.bounds(),
        Bounds(-1, -1, 3, 3)
    )


def test_line_segment_bounds():
    # Fill mode segment.
    p = Pen()
    p.fill_mode()
    p.move_to((1, 0))
    p.line_to((2, 3))

    line = p.last_segment()
    assert_equal(
        line.bounds(),
        Bounds(1, 0, 2, 3)
    )

    # Stroke mode segment.
    p = Pen()
    p.stroke_mode(sqrt2)
    p.move_to((0, 0))
    p.line_to((5, 5))

    line = p.last_segment()
    assert_equal(
        line.bounds(),
        Bounds(-0.5, -0.5, 5.5, 5.5)
    )


def test_arc_segment_bounds():
    # Arc which occupies its entire circle.
    p = Pen()
    p.fill_mode()
    p.move_to((1, 0))
    p.turn_to(90)
    p.arc_left(359, 1)

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(-1, -1, 1, 1)
    )

    # Arc which pushes the boundary only with the endpoints.
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(30)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(30, center=(0, 0))

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(0.5, 0.5, sqrt3 / 2, sqrt3 / 2)
    )

    # Arc which pushes the boundary with the middle in one spot.
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(90, center=(0, 0))

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(sqrt2 / 2, -sqrt2 / 2, 1, sqrt2 / 2)
    )

    # Arc which pushes the boundary with the middle in two spots.
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(-45)
    p.move_forward(1)
    p.turn_left(90)
    p.arc_left(180, center=(0, 0))

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(-sqrt2 / 2, -sqrt2 / 2, 1, 1)
    )

    # Half circle, right side
    p = Pen()
    p.fill_mode()
    p.move_to((0, 0))
    p.turn_to(0)
    p.arc_right(180, 5)

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(0, -10, 5, 0)
    )

    # Thick circle,
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.move_forward(5)
    p.turn_left(90)
    p.arc_left(180, 5, start_slant=45)

    arc = p.last_segment()
    assert_equal(
        arc.bounds(),
        Bounds(-5.5, -0.5314980314970469, 5.5, 5.5)
    )
