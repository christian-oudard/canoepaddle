import math
from canoepaddle import Pen

p = Pen()
p.paper.set_view_box(-120, -120, 240, 240)
p.paper.set_pixel_size(720, 720)

p.move_to((0.5, 0.5))


def f(n):
    a = 12
    b = 0.03
    c = 0.2
    d = 1.5
    e = 0.5
    wobble = a * math.exp(-b * n) * math.sin(c * n + d * n**e)
    return (
        -24 + wobble,
        24 + wobble
    )

center_heading = 90
p.turn_to(center_heading)
center = p.position

num_layers = 26
for layer in range(num_layers):
    lo, hi = f(layer)
    lo = center_heading + lo
    hi = center_heading + hi

    p.arc_right((p.heading + 90) - lo, center=center)
    p.turn_to(lo)
    p.turn_right(90)
    p.arc_left(180, 1)

    p.arc_left(hi - (p.heading - 90), center=center)
    if layer < (num_layers - 1):
        p.arc_right(180, 1)

p.paper.set_style('''
    stroke: #15A;
    stroke-width: 1.0;
    stroke-linecap: round;
    fill: none;
''')
print(p.paper.format_svg())
