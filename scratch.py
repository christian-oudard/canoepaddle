from canoepaddle import Pen


def draw(p):
    p.paper.set_precision(1)

    p.set_width(1.0)

    p.set_color((1.0, 0.0, 0.0))
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.set_color((0.0, 1.0, 0.0))
    p.move_to((2, 2))
    p.circle(2)

    p.set_color((0.0, 0.0, 1.0))
    p.move_to((0, 4))
    p.turn_to(0)
    p.line_forward(4)


if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
