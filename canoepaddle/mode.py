from .svg import (
    path_element,
)


def modes_compatible(a, b):
    # Can these modes be used together in a single stroke?
    if type(a) != type(b):
        return False
    return a.compatible_with(b)


class Mode:

    def __repr__(self):
        strings = []
        for field in self.repr_fields:
            value = getattr(self, field)
            if value is None:
                continue
            strings.append(repr(value))
        return '{}({})'.format(self.__class__.__name__, ', '.join(strings))

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
        if color is None:
            color = 'black'
        self.color = color

    def svg(self, path, precision):
        return path_element(
            self.render(path, precision),
            self.color,
        )

    def render(self, path, precision):
        return path.render_path(precision)

    def compatible_with(self, other):
        return self.color == other.color


class StrokeMode(Mode):

    thick = True
    repr_fields = ['width', 'color']

    def __init__(self, width, color=None):
        if color is None:
            color = 'black'
        self.color = color
        self.width = width

    def svg(self, path, precision):
        return path_element(
            self.render(path, precision),
            self.color,
        )

    def render(self, path, precision):
        # Create a temporary pen to draw along the outline of the path
        # segments, taking into account the thickness of the path.
        from .pen import Pen
        pen = Pen()
        mode = self.outliner_mode()
        pen.set_mode(mode)
        path.draw_outline(pen, precision)

        return ' '.join(
            mode.render(path, precision)
            for path in pen.paper.elements
        )

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
        if outline_color is None:
            outline_color = 'black'
        self.outline_color = outline_color
        self.width = width
        self.outline_width = outline_width

    def svg(self, path, precision):
        return path_element(
            self.render(path, precision),
            self.outline_color,
        )

    def outliner_mode(self):
        return StrokeMode(self.outline_width)

    def compatible_with(self, other):
        # Outlines have to be consistent through the whole stroke.
        return (
            self.outline_width == other.outline_width and
            self.outline_color == other.outline_color
        )


class OutlinedFillMode(Mode):
    thick = False
    #STUB


class OutlinedStrokeMode(Mode):
    thick = True
    #STUB
