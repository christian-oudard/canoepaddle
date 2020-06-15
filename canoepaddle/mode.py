from copy import copy

from .svg import (
    path_element,
)


def modes_compatible(a, b):
    # Can these modes be used together in a single stroke?
    if type(a) != type(b):
        return False
    return a.compatible_with(b)


class Mode:
    """
    A strategy for rendering a Path.

    For all mode types with a width, the color and width attributes apply
    per-segment, while other attributes such as outline_width and outline_color
    apply per-path.
    """

    def __repr__(self):  # pragma: no cover
        strings = []
        for field in self.repr_fields:
            value = getattr(self, field)
            if value is None:
                continue
            strings.append(repr(value))
        return '{}({})'.format(self.__class__.__name__, ', '.join(strings))

    def svg(self, path, precision):
        return ''.join(
            path_element(path_data, color)
            for color, path_data in self.iter_render(path, precision)
        )

    def copy(self):
        return copy(self)

    def copy_colors(self, other):
        # Update the current mode based on a new one, but keeping old colors if
        # they weren't specified.
        for color_attr in ['color', 'outline_color']:
            self_color = getattr(self, color_attr, None)
            other_color = getattr(other, color_attr, None)
            if self_color is None and other_color is not None:
                setattr(self, color_attr, other_color)


class FillMode(Mode):

    repr_fields = ['color']

    def __init__(self, color=None):
        self.width = None
        self.color = color

    def iter_render(self, path, precision):
        yield self.color, path.render_path(precision)

    def compatible_with(self, other):
        return self.color == other.color


class StrokeMode(Mode):

    repr_fields = ['width', 'color']

    def __init__(self, width, color=None):
        self.width = width
        self.color = color

    def iter_render(self, path, precision):
        # Create a temporary pen to draw along the outline of the path
        # segments, taking into account the thickness of the path.
        from .pen import Pen
        pen = Pen()
        mode = self.outliner_mode()
        pen.set_mode(mode)
        path.draw_outline(pen, precision)

        for path in pen.paper.paths:
            color = path.segments[0].color
            path_data = ' '.join(
                p for c, p in
                mode.iter_render(path, precision)
            )
            yield color, path_data

    def outliner_mode(self):
        # Give the mode, that if used to draw the outline, will produce the
        # correct results.
        return FillMode(self.color)

    def compatible_with(self, other):
        return True


class OutlineMode(StrokeMode):

    repr_fields = ['width', 'outline_width', 'outline_color']

    def __init__(self, width, outline_width, outline_color=None):
        self.width = width
        self.color = None
        self.outline_width = outline_width
        self.outline_color = outline_color

    def iter_render(self, path, precision):
        for color, path_data in super().iter_render(path, precision):
            yield self.outline_color, path_data

    def outliner_mode(self):
        return StrokeMode(self.outline_width, self.outline_color)

    def compatible_with(self, other):
        # Outlines have to be consistent through the whole stroke.
        return (
            self.outline_width == other.outline_width
            and self.outline_color == other.outline_color
        )


class StrokeFillMode(StrokeMode):

    repr_fields = ['width', 'color', 'fill_color']

    def __init__(self, width, color=None, fill_color=None):
        self.width = width
        self.color = color
        self.fill_color = fill_color

    def iter_render(self, path, precision):
        fill_mode = FillMode(self.fill_color)
        yield from fill_mode.iter_render(path, precision)
        stroke_mode = StrokeMode(self.width, self.color)
        yield from stroke_mode.iter_render(path, precision)


class StrokeOutlineMode(StrokeMode):

    repr_fields = ['width', 'outline_width', 'color', 'outline_color']

    def __init__(self, width, outline_width, color=None, outline_color=None):
        self.width = width
        self.outline_width = outline_width
        self.color = color
        self.outline_color = outline_color

    def iter_render(self, path, precision):
        stroke_mode = StrokeMode(self.width, self.color)
        yield from stroke_mode.iter_render(path, precision)
        outline_mode = OutlineMode(self.width, self.outline_width, self.outline_color)
        yield from outline_mode.iter_render(path, precision)

    def outliner_mode(self):
        return StrokeFillMode(
            self.outline_width,
            self.outline_color,
            self.color,
        )
