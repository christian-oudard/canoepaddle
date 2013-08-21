from copy import copy

import vec

from .point import Point
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
            self.centered,
            precision,
        )

    def copy(self):
        return copy(self)

    def translate(self, offset):
        self.position = Point(*vec.add(self.position, offset))
