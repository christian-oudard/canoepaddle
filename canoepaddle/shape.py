from .point import Point
from .svg import circle


class Circle:
    def __init__(self, center, radius):
        self.center = Point(*center)
        self.radius = radius

    def format(self, precision):
        return circle(
            self.center.x,
            self.center.y,
            self.radius,
            precision,
        )
