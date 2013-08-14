# TODO: Rename element to path? It is always a path right now.

from textwrap import dedent
from string import Template

from .bounds import Bounds
from .geometry import find_point_pairs
from .point import points_equal


class Paper:

    def __init__(self):
        self.elements = []

        # Default values.
        self.set_view_box(-10, -10, 20, 20)
        self.set_pixel_size(800, 800)

    def add_element(self, element):
        self.elements.append(element)

    def merge(self, other):
        """
        Add all the elements of the other on top of this one.
        """
        self.elements.extend(other.elements)
        return self

    def merge_under(self, other):
        """
        Add all the elements of the other paper underneath this one.
        """
        self.elements = other.elements + self.elements
        return self

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
        return Bounds.union_all(
            element.bounds()
            for element in self.elements
        )

    def translate(self, offset):
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

    def set_view_box(self, x, y, width, height):
        self.view_x = x
        self.view_y = y
        self.view_width = width
        self.view_height = height

    def set_pixel_size(self, width, height):
        self.pixel_width = width
        self.pixel_height = height

    def format_svg(self, precision=12):
        element_data = '\n'.join(self.svg_elements(precision))

        # Transform world-coordinate view box into svg-coordinate view box.
        view_x = self.view_x
        view_y = -self.view_y - self.view_height
        view_width = self.view_width
        view_height = self.view_height

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
            pixel_width=self.pixel_width,
            pixel_height=self.pixel_height,
            view_x=view_x,
            view_y=view_y,
            view_height=view_height,
            view_width=view_width,
        )

    def svg_elements(self, precision):
        return [
            element.svg(precision)
            for element in self.elements
        ]
