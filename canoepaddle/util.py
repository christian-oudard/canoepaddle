from textwrap import dedent
from string import Template


epsilon = 10e-15


def format_svg(path_data, path_style):
    svg_template = dedent('''\
        <?xml version="1.0" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
            "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        <svg
            xmlns="http://www.w3.org/2000/svg" version="1.1"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            viewBox="-10 -10 20 20"
            width="400px" height="400px"
        >
            <style type="text/css">
                path {
                    $path_style
                }
            </style>
            <path d="
                $path_data
                " />
        </svg>
    ''')
    t = Template(svg_template)
    return t.substitute(
        path_data=path_data,
        path_style=path_style,
    )
