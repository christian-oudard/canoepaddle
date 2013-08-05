from .point import Point, float_equal


class Bounds:

    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def __eq__(self, other):
        return (
            float_equal(self.left, other.left) and
            float_equal(self.bottom, other.bottom) and
            float_equal(self.right, other.right) and
            float_equal(self.top, other.top)
        )

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(
            self.__class__.__name__,
            self.left,
            self.bottom,
            self.right,
            self.top,
        )

    def __iter__(self):
        yield self.left
        yield self.bottom
        yield self.right
        yield self.top

    @classmethod
    def from_point(self, point):
        p = Point(*point)
        return Bounds(p.x, p.y, p.x, p.y)

    def union(self, other):
        self.left = min(self.left, other.left)
        self.bottom = min(self.bottom, other.bottom)
        self.right = max(self.right, other.right)
        self.top = max(self.top, other.top)

    @staticmethod
    def union_all(bounds_list):
        bounds_list = iter(bounds_list)
        current = Bounds(*next(bounds_list))
        for b in bounds_list:
            current.union(b)
        return current

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    def draw(self, pen):
        pen.move_to((self.left, self.bottom))
        pen.turn_to(0)
        pen.line_to_x(self.right)
        pen.turn_left(90)
        pen.line_to_y(self.top)
        pen.turn_left(90)
        pen.line_to_x(self.left)
        pen.turn_left(90)
        pen.line_to_y(self.bottom)
