import vec

from .point import Point
from .svg import circle, rectangle
from .bounds import Bounds


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

    def bounds(self):
        return Bounds(
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.center.x + self.radius,
            self.center.y + self.radius,
        )

    def translate(self, offset):
        self.center = Point(*vec.add(self.center, offset))


class PathCircle(Circle):

    #TODO: Ew, we're using width for pen width here, but for rectangle width later.
    def __init__(self, center, radius, width, color):
        self.center = Point(*center)
        self.radius = radius
        self.width = width
        self.color = color

    def svg(self, precision):
        from .pen import Pen
        pen = Pen()
        pen.set_color(self.color)
        pen.set_width(self.width)
        pen.move_to(self.center)
        pen.turn_to(0)
        pen.move_forward(self.radius)
        pen.turn_left(90)
        pen.arc_left(180, self.radius)
        pen.arc_left(180, self.radius)
        return pen.paper.elements[0].svg(precision)


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

    def bounds(self):
        return Bounds(
            self.left,
            self.bottom,
            self.left + self.width,
            self.bottom + self.height,
        )

    def translate(self, offset):
        dx, dy = offset
        self.left += dx
        self.bottom += dy
