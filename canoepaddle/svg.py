def number(n, precision):
    # Handle numbers near zero formatting inconsistently as
    # either "0.0" or "-0.0".
    if abs(n) < 0.5 * 10**(-precision):
        n = 0
    return '{n:.{p}f}'.format(n=n, p=precision)


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


def circle(x, y, radius, precision):
    return (
        '<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r}" />'
    ).format(
        x=number(x, precision),
        y=number(-y, precision),
        r=number(abs(radius), precision),
    )
