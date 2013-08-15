from canoepaddle import Pen


def draw(p):
    p.stroke_mode(2.0, '#650360')

    p.move_to((3, -4))
    p.turn_to(90)
    p.line_forward(4)
    p.arc_left(270, 3)
    p.line_forward(1, end_slant=45)

if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
