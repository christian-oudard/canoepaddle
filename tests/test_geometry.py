from nose.tools import (
    assert_equal,
    assert_almost_equal,
)
from util import assert_points_equal, sqrt2, sqrt3
from canoepaddle.geometry import (
    intersect_lines,
    intersect_circle_line,
    intersect_circles,
    quadratic_formula,
    collinear,
    find_point_pairs,
)
from canoepaddle.point import epsilon


def test_quadratic_formula():
    x1, x2 = quadratic_formula(2, 4, -4)
    assert_almost_equal(x1, (-1 - sqrt3))
    assert_almost_equal(x2, (-1 + sqrt3))

    x1, x2 = quadratic_formula(-2, -4, 4)
    assert_almost_equal(x1, (-1 + sqrt3))
    assert_almost_equal(x2, (-1 - sqrt3))


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
    # Two points.
    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (1, 2), (1, -2),
        ),
        [(1, 1), (1, -1)],
    )
    # Two points, negative radius
    assert_equal(
        intersect_circle_line(
            (0, 0), -sqrt2,
            (1, 2), (1, -2),
        ),
        [(1, 1), (1, -1)],
    )
    # Single point.
    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (2, 0), (0, 2),
        ),
        [(1, 1)],
    )
    # No intersection.
    assert_equal(
        intersect_circle_line(
            (0, 0), sqrt2,
            (2, 0), (0, 2.00001),
        ),
        [],
    )


def test_intersect_circles():
    # Coincident circles, no single intersection point.
    assert_equal(
        intersect_circles(
            (0, 0), 1,
            (0, 0), 1,
        ),
        [],
    )
    # No intersection, separated circles.
    assert_equal(
        intersect_circles(
            (0, 0), 1,
            (5, 0), 1,
        ),
        [],
    )
    # No intersection, concentric circles.
    assert_equal(
        intersect_circles(
            (0, 0), 1,
            (0, 0), 2,
        ),
        [],
    )
    # One point, exterior tangent.
    assert_equal(
        intersect_circles(
            (0, 0), 1,
            (2, 0), 1,
        ),
        [(1, 0)],
    )
    # One point, interior tangent.
    assert_equal(
        intersect_circles(
            (0, 0), 2,
            (1, 0), 1,
        ),
        [(2, 0)],
    )
    assert_equal(
        intersect_circles(
            (0, 1), 1.5,
            (0, 0), 2.5,
        ),
        [(0, 2.5)],
    )
    # Two points, same size circles.
    assert_equal(
        intersect_circles(
            (-1, 0), sqrt2,
            (1, 0), sqrt2,
        ),
        [(0, 1), (0, -1)],
    )
    # Two points, different size circles.
    p1, p2 = intersect_circles(
        (0, 0), sqrt2,
        (1, 0), 1,
    )
    assert_points_equal(p1, (1, 1))
    assert_points_equal(p2, (1, -1))


def test_intersect_circles_numerical():
    assert_equal(
        intersect_circles(
            (-27.073924841728974, 65.92689560740814), -1.25,
            (0.5, 0.5), -72.25000000000001,
        ),
        [(-27.55938126499886, 67.07877757232733)],
    )


def test_collinear():
    assert collinear(
        (0, 0),
        (1, 1),
        (2, 2),
    )
    assert not collinear(
        (0, 0),
        (1, 1),
        (2, 1),
    )
    # Order matters.
    assert not collinear(
        (0, 0),
        (2, 2),
        (1, 1),
    )


def test_find_point_pairs():
    # No pairs.
    assert_equal(
        find_point_pairs([
            (3, 0),
            (4, 0),
            (5, 0),
        ]),
        []
    )
    # Simple pair.
    assert_equal(
        find_point_pairs([
            (3, 0),
            (3, 0),
            (4, 0),
        ]),
        [(0, 1)]
    )
    # Multiple pairs.
    assert_equal(
        find_point_pairs([
            (3, 0),
            (4, 0),
            (10, 0),
            (3, 0),
            (4, 0),
        ]),
        [(0, 3), (1, 4)]
    )
    # Three or more the same does not count as a pair.
    assert_equal(
        find_point_pairs([
            (3, 0),
            (3, 0),
            (3, 0),
        ]),
        []
    )
    assert_equal(
        find_point_pairs([
            (3, 0),
            (3, 0),
            (3, 0),
            (3, 0),
        ]),
        []
    )
    # Partial pair interference.
    # Because of the epsilon equality test, equality is not strictly
    # transitive. In this test case, A == B, and B == C, but A != C.
    assert_equal(
        find_point_pairs([
            (0, 0),
            (epsilon * 0.6, 0),
            (epsilon * 1.2, 0),
        ]),
        [],
    )
