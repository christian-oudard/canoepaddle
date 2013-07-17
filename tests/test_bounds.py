from nose.tools import assert_equal

from canoepaddle.bounds import Bounds


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
