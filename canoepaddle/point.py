from collections import namedtuple

epsilon = 10e-10

PointBase = namedtuple('Point', 'x, y')


class Point(PointBase):

    def flipped_x(self, x_center):
        return Point(flip(self.x, x_center), self.y)

    def flipped_y(self, y_center):
        return Point(self.x, flip(self.y, y_center))


def float_equal(a, b):
    return abs(a - b) <= epsilon


def points_equal(a, b):
    if a is None or b is None:
        return False
    return all(
        float_equal(da, db)
        for (da, db) in zip(a, b)
    )


def flip(d, c):
    new_d = c - d
    return c + new_d
