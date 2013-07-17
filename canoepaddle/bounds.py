class Bounds:

    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def __eq__(self, other):
        return (
            self.left == other.left and
            self.bottom == other.bottom and
            self.right == other.right and
            self.top == other.top
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
