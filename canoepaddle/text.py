import vec

from .point import Point
from .bounds import Bounds
from .svg import text_element


class Text:

    def __init__(self, text, position, font_family, size, color, centered=False):
        self.text = text
        self.position = Point(*position)
        self.font_family = font_family
        self.size = size
        self.color = color
        self.centered = centered

    def svg(self, precision):
        return text_element(
            self.text,
            self.position,
            self.font_family,
            self.size,
            self.color,
            precision,
        )

    def bounds(self):
        # Approximate bounds with one letter.
        return Bounds(
            self.position.x,
            self.position.y,
            self.position.x + self.size,
            self.position.y + self.size,
        )

    def translate(self, offset):
        self.position = Point(*vec.add(self.position, offset))

    def mirror_x(self, x_center):
        p = self.position
        new_x = x_center - p.x
        self.position = Point(x_center + new_x, p.y)

    def mirror_y(self, y_center):
        p = self.position
        new_y = y_center - p.y
        self.position = Point(p.x, y_center + new_y)
