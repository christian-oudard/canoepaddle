from collections import namedtuple

from .bounds import Bounds

epsilon = 10e-10

Point = namedtuple('Point', 'x, y')


def float_equal(a, b):
    return abs(a - b) <= epsilon


def points_equal(a, b):
    return all(
        float_equal(da, db)
        for (da, db) in zip(a, b)
    )


def point_bounds(p):
    p = Point(*p)
    return Bounds(p.x, p.y, p.x, p.y)
