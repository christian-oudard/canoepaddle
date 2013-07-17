#TODO: refactor this into an object, so we don't have to say "precision" so much.

from grapefruit import Color


def number(n, precision):
    # Handle numbers near zero formatting inconsistently as
    # either "0.0" or "-0.0".
    if abs(n) <= 0.5 * 10**(-precision):
        n = 0
    return '{n:.{p}f}'.format(n=n, p=precision)


def svg_coord(x, y):
    return x, -y


def svg_rect(left, bottom, width, height):
    x = left
    y = -bottom - height
    return x, y, width, height


def html_color(color):
    if isinstance(color, Color):
        return color.html
    if isinstance(color, str):
        return Color.NewFromHtml(color).html

    return Color.RgbToHtml(*color)


def path_element(path_data, color, stroke_width=None):
    color = html_color(color)
    if stroke_width is not None:
        color_attrs = 'fill="none" stroke="{}" stroke-width="{}"'.format(
            color,
            stroke_width,
        )
    else:
        color_attrs = 'fill="{}"'.format(color)

    return '<path d="{path_data}" {color_attrs} />'.format(
        path_data=path_data,
        color_attrs=color_attrs,
    )


def path_move(x, y, precision):
    return 'M{x},{y}'.format(
        x=number(x, precision),
        y=number(-y, precision),
    )


def path_close():
    return 'z'


def path_line(x, y, precision):
    return 'L{x},{y}'.format(
        x=number(x, precision),
        y=number(-y, precision),
    )


def path_arc(x, y, arc_angle, radius, precision):
    direction_flag = int(arc_angle < 0)
    sweep_flag = int(abs(arc_angle) % 360 > 180)
    return (
        'A {r},{r} 0 {sweep_flag} {direction_flag} {x},{y}'
    ).format(
        x=number(x, precision),
        y=number(-y, precision),
        r=number(abs(radius), precision),
        direction_flag=direction_flag,
        sweep_flag=sweep_flag,
    )


def circle(x, y, radius, color, precision):
    x, y = svg_coord(x, y)
    return (
        '<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" />'
    ).format(
        x=number(x, precision),
        y=number(y, precision),
        r=number(abs(radius), precision),
        color=html_color(color),
    )


def rectangle(left, bottom, width, height, color, precision):
    x, y, width, height = svg_rect(left, bottom, width, height)
    return (
        '<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{color}" />'
    ).format(
        x=number(x, precision),
        y=number(y, precision),
        width=number(width, precision),
        height=number(height, precision),
        color=html_color(color),
    )
