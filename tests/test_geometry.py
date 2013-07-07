import math
from nose.tools import (
    assert_equal,
    assert_almost_equal,
)
from util import assert_points_equal
from canoepaddle.geometry import (
    intersect_lines,
    intersect_circle_line,
    quadratic_formula,
)

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def test_intersect_lines():
    assert_points_equal(
        intersect_lines(
            (0, 0), (10, 10),
            (0, 10), (10, 0),
        ),
        (5, 5),
    )
    assert_points_equal(
        intersect_lines(
            (0, 0), (10, 0),
            (5, 0), (15, 0.01),
        ),
        (5, 0),
    )
    assert_equal(
        intersect_lines(
            (0, 0), (1, 0),
            (0, 1), (1, 1),
        ),
        None,
    )
    assert_equal(
        intersect_lines(
            (0, 0), (1, 0),
            (2, 1), (2, -1),
            segment=True,
        ),
        None,
    )
    assert_equal(
        intersect_lines(
            (2, 1), (2, -1),
            (0, 0), (1, 0),
            segment=True,
        ),
        None,
    )


def test_intersect_circle_line():
    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (1, 2), (1, -2),
        ),
        [(1, 1), (1, -1)],
    )

    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (2, 0), (0, 2),
        ),
        [(1, 1)],
    )

    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (2, 0), (0, 2.00001),
        ),
        [],
    )


def test_quadratic_formula():
    x1, x2 = quadratic_formula(2, 4, -4)
    assert_almost_equal(x1, (-1 - sqrt3))
    assert_almost_equal(x2, (-1 + sqrt3))

    x1, x2 = quadratic_formula(-2, -4, 4)
    assert_almost_equal(x1, (-1 + sqrt3))
    assert_almost_equal(x2, (-1 - sqrt3))
