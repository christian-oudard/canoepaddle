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

    For all thick mode types, the color and width attributes apply per-segment,
    while other attributes such as outline_width and outline_color apply
    per-path.
    """

    def __repr__(self):
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

    def copy_colors(self, other):
        # Update the current mode based on a new one, but keeping old colors if
        # they weren't specified.
        for color_attr in ['color', 'outline_color']:
            self_color = getattr(self, color_attr, None)
            other_color = getattr(other, color_attr, None)
            if self_color is None and other_color is not None:
                setattr(self, color_attr, other_color)


class FillMode(Mode):

    thick = False
    repr_fields = ['color']

    def __init__(self, color=None):
        self.width = None
        self.color = color

    def iter_render(self, path, precision):
        yield self.color, path.render_path(precision)

    def compatible_with(self, other):
        return self.color == other.color


class StrokeMode(Mode):

    thick = True
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

        for path in pen.paper.elements:
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

    thick = True
    repr_fields = ['width', 'outline_width', 'outline_color']

    def __init__(self, width, outline_width, outline_color=None):
        self.width = width
        self.color = None
        self.outline_width = outline_width
        self.outline_color = outline_color

    def outliner_mode(self):
        return StrokeMode(self.outline_width, self.outline_color)

    def compatible_with(self, other):
        # Outlines have to be consistent through the whole stroke.
        return (
            self.outline_width == other.outline_width and
            self.outline_color == other.outline_color
        )
