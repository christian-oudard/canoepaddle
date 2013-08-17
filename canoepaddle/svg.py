from grapefruit import Color


def number(n, precision):
    # Handle numbers near zero formatting inconsistently as
    # either "0.0" or "-0.0".
    if abs(n) <= 0.5 * 10**(-precision):
        n = 0
    return '{n:.{p}f}'.format(n=n, p=precision)


def html_color(color):
    if color is None:
        return '#000000'
    if isinstance(color, Color):
        return color.html
    if isinstance(color, str):
        return Color.NewFromHtml(color).html

    return Color.RgbToHtml(*color)


def text_element(text, position, font_family, font_size, color, precision):
    color = html_color(color)
    return (
        '<text x="{x}" y="{y}" '
        'font-family="{font_family}" font-size="{font_size}" '
        'fill="{color}">{text}</text>'
    ).format(
        x=number(position.x, precision),
        y=number(-position.y, precision),
        font_family=font_family,
        font_size=font_size,
        color=color,
        text=text,
    )


def path_element(path_data, color):
    color = html_color(color)
    return '<path d="{path_data}" fill="{color}" />'.format(
        path_data=path_data,
        color=color,
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
