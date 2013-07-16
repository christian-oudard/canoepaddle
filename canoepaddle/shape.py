from .point import Point
from .svg import circle


class Circle:
    def __init__(self, center, radius, color):
        self.center = Point(*center)
        self.radius = radius
        self.color = color

    def svg(self, precision):
        return circle(
            self.center.x,
            self.center.y,
            self.radius,
            precision,
            self.color,
        )
