from .point import Point
from .svg import circle, rectangle


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
            self.color,
            precision,
        )


class Rectangle:
    def __init__(self, left, bottom, width, height, color):
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
        self.color = color

    def svg(self, precision):
        return rectangle(
            self.left,
            self.bottom,
            self.width,
            self.height,
            self.color,
            precision,
        )
