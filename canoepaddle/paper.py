#TODO: remove set_precision, only specify it on render.

from textwrap import dedent
from string import Template


class Paper:

    def __init__(self):
        self.elements = []

        self.shapes = []  # Deprecated.

        # Default values.
        self.set_precision(12)
        self.set_style('')
        self.set_view_box(-10, -10, 20, 20)
        self.set_pixel_size(800, 800)

    def add_element(self, element):
        self.elements.append(element)

    def center_on_x(self, x_center):
        raise NotImplementedError

    def center_on_y(self, y_center):
        raise NotImplementedError

    def set_style(self, style):
        self.style = style

    def set_view_box(self, x, y, width, height):
        self.view_x = x
        self.view_y = y
        self.view_width = width
        self.view_height = height

    def set_pixel_size(self, width, height):
        self.pixel_width = width
        self.pixel_height = height

    def set_precision(self, precision):
        self.precision = precision

    def format_svg(self, thick=True):
        element_data = '\n'.join(self.svg_elements())

        # Transform world-coordinate view box into svg-coordinate view box.
        view_x = self.view_x
        view_y = -self.view_y - self.view_height
        view_width = self.view_width
        view_height = self.view_height

        #TODO: remove style
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
                <style type="text/css">
                    path {
                        $style
                    }
                </style>
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
            style=self.style,
            pixel_width=self.pixel_width,
            pixel_height=self.pixel_height,
            view_x=view_x,
            view_y=view_y,
            view_height=view_height,
            view_width=view_width,
        )

    def svg_elements(self):
        return [
            element.svg(self.precision)
            for element in self.elements
        ]
