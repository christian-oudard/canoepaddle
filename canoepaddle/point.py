from collections import namedtuple
from util import epsilon


Point = namedtuple('Point', 'x, y')


def points_equal(a, b):
    return all(
        abs(da - db) <= epsilon
        for (da, db) in zip(a, b)
    )
