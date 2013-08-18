# TODO: Rename element to path? It is always a path right now.

from copy import copy
from textwrap import dedent
from string import Template

from .bounds import Bounds
from .geometry import find_point_pairs
from .point import Point, points_equal
from .svg import text_element


class Paper:

    def __init__(self):
        self.elements = []
        self.text_elements = []
        self._bounds_override = None

    def add_element(self, element):
        self.elements.append(element)

    def add_text(self, text, position, size, font_family='sans-serif', color=None):
        self.text_elements.append([
            text,
            Point(*position),
            font_family,
            size,
            color,
        ])

    def merge(self, other):
        """
        Add all the elements of the other paper on top of this one.
        """
        self._merge_bounds(other)
        self.elements.extend(other.elements)

    def merge_under(self, other):
        """
        Add all the elements of the other paper underneath this one.
        """
        self._merge_bounds(other)
        self.elements[0:0] = other.elements

    def _merge_bounds(self, other):
        if self._bounds_override is None and other._bounds_override is None:
            return

        # If there are overridden boundaries, make sure that the merged
        # boundaries account for this.
        self_empty = (len(self.elements) == 0)
        other_empty = (len(other.elements) == 0)
        if self_empty and other_empty:
            return
        elif self_empty:
            bounds = other.bounds()
        elif other_empty:
            bounds = self.bounds()
        else:
            bounds = Bounds.union_all([self.bounds(), other.bounds()])
        self.override_bounds(bounds)

    def join_paths(self):
        """
        Find all paths that come to a common point with another path, and join
        them together.
        """
        # Index paths by their end nodes.
        nodes_and_paths = []
        for path in self.elements:
            start = path.segments[0].a
            end = path.segments[-1].b
            if points_equal(start, end):
                continue  # This is a path looping back on itself.
            nodes_and_paths.append((start, path))
            nodes_and_paths.append((end, path))

        # Find paths that meet at a common point and join them.
        nodes = [n for (n, p) in nodes_and_paths]
        pair_indexes = find_point_pairs(nodes)
        for left_index, right_index in pair_indexes:
            left_node, left_path = nodes_and_paths[left_index]
            right_node, right_path = nodes_and_paths[right_index]
            self.elements.remove(right_path)
            left_path.join_with(right_path)

    def fuse_paths(self):
        for path in self.elements:
            path.fuse()

    def bounds(self):
        if self._bounds_override is not None:
            return copy(self._bounds_override)
        if len(self.elements) == 0:
            raise ValueError('Empty page, cannot calculate bounds.')
        return Bounds.union_all(
            element.bounds()
            for element in self.elements
        )

    def override_bounds(self, *args):
        """
        Manually determine the bounding box.

        You can pass in a Bounds object,
        >>> paper = Paper()
        >>> paper.override_bounds(Bounds(1, 2, 3, 4))

        or you can pass left, bottom, right, and top individually.
        >>> paper.override_bounds(1, 2, 3, 4)

        Passing in None will clear the bounds overriding, and revert to
        automatic bounds calculation.
        >>> paper.override_bounds(None)
        """
        if len(args) == 1:
            bounds = args[0]
            self._bounds_override = bounds
        else:
            self._bounds_override = Bounds(*args)

    def translate(self, offset, bounds=True):
        """
        Move all the elements in the paper by `offset`.

        If `bounds` is True, then the paper bounds will update as well.
        If `bounds` is False, the bounds will stay the same.
        """
        if bounds:
            if self._bounds_override is not None:
                self._bounds_override.translate(offset)
        else:
            # There are no overridden bounds, and all the elements are about to
            # move. Override the bounds to stay in place.
            if self._bounds_override is None:
                self.override_bounds(self.bounds())

        for element in self.elements:
            element.translate(offset)

    def center_on_x(self, x_center):
        bounds = self.bounds()
        current_x_center = (bounds.left + bounds.right) / 2
        self.translate((x_center - current_x_center, 0))

    def center_on_y(self, y_center):
        bounds = self.bounds()
        current_y_center = (bounds.bottom + bounds.top) / 2
        self.translate((0, y_center - current_y_center))

    def mirror_x(self, x_center):
        for element in self.elements:
            element.mirror_x(x_center)

    def mirror_y(self, y_center):
        for element in self.elements:
            element.mirror_y(y_center)

    def format_svg(self, precision=12, resolution=10):
        element_data = '\n'.join(self.svg_elements(precision))
        for text_args in self.text_elements:
            text_args.append(precision)
            element_data += '\n' + text_element(*text_args)

        # Transform world-coordinate bounding box into svg-coordinate view box.
        bounds = self.bounds()
        view_x = bounds.left
        view_y = -bounds.top
        view_width = bounds.width
        view_height = bounds.height

        # Calculate pixel size.
        pixel_width = resolution * bounds.width
        pixel_height = resolution * bounds.height

        #TODO: remove background rectangle?
        svg_template = dedent('''\
            <?xml version="1.0" standalone="no"?>
            <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
            <svg
                xmlns="http://www.w3.org/2000/svg" version="1.1"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                viewBox="$view_x $view_y $view_width $view_height"
                width="${pixel_width}px" height="${pixel_height}px"
            >
                <rect
                    style="fill: #FFF"
                    x="$view_x"
                    y="$view_y"
                    width="$view_width"
                    height="$view_height"
                />
                $element_data
            </svg>
        ''')
        t = Template(svg_template)
        return t.substitute(
            element_data=element_data,
            view_x=view_x,
            view_y=view_y,
            view_height=view_height,
            view_width=view_width,
            pixel_width=pixel_width,
            pixel_height=pixel_height,
        )

    def svg_elements(self, precision):
        return [
            element.svg(precision)
            for element in self.elements
        ]
