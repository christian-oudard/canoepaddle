import math

from canoepaddle import Pen
from grapefruit import Color


def draw(p):
    radius = 4
    num_colors = 36
    angle_step = 360 / num_colors

    p.move_to((0, 0))
    p.turn_to(90)
    p.move_forward(radius)
    p.turn_right(90)

    angle = 60
    for _ in range(num_colors):
        l = 74
        chroma = 0.4
        a = chroma * math.sin(math.radians(angle))
        b = chroma * math.cos(math.radians(angle))
        color = Color.from_lab(l, a, b)
        assert color.is_legal
        p.stroke_mode(1.0, color)

        p.arc_right(
            angle_step,
            center=(0, 0),
        )
        angle += angle_step


if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
