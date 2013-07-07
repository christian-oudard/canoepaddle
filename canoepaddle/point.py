from collections import namedtuple

epsilon = 10e-15

Point = namedtuple('Point', 'x, y')


def float_equal(a, b):
    return abs(a - b) <= epsilon


def points_equal(a, b):
    return all(
        float_equal(da, db)
        for (da, db) in zip(a, b)
    )
