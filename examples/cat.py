import math

from canoepaddle import Pen

sqrt2 = math.sqrt(2)


def draw(p):
    # Kitty!
    gray = '#333'
    pink = '#e88'
    green = '#7BD41C'
    cat_color = '#F5EADA'

    p.move_to((0, 0))
    p.turn_to(0)

    # Head.
    p.fill_mode(cat_color)
    p.circle(5)
    p.stroke_mode(1.0, gray)
    p.circle(5)

    # Mouth.
    p.stroke_mode(0.5, gray)
    p.turn_to(-90)
    p.move_forward(2)
    mouth_top = p.position
    p.arc_left(60, 2.8)
    p.move_to(mouth_top)
    p.turn_to(-90)
    p.arc_right(60, 2.8)

    # Nose.
    p.move_to(mouth_top)
    p.fill_mode(pink)
    p.move_to(mouth_top)
    p.turn_to(45)
    p.line_forward(sqrt2)
    p.turn_left(135)
    p.line_forward(2)
    p.turn_left(135)
    p.line_to(mouth_top)

    # Whiskers.
    p.stroke_mode(0.15, gray)
    dot_angles_and_distances = [
        (-16, 1.5),
        (-3, 1.4),
        (10, 1.5),
    ]
    for angle, distance in dot_angles_and_distances:
        p.move_to(mouth_top)
        p.turn_to(0)
        p.turn_left(angle)
        p.move_forward(distance)
        p.line_forward(distance)

        p.move_to(mouth_top)
        p.turn_to(180)
        p.turn_right(angle)
        p.move_forward(distance)
        p.line_forward(distance)

    # Eyes.
    def eye():
        center = p.position
        p.fill_mode(green)
        p.circle(1.0)
        p.stroke_mode(0.4, gray)
        p.circle(1.0)

        p.move_to(center)
        p.turn_to(90)
        p.move_forward(0.8)
        top = p.position
        p.move_to(center)
        p.turn_to(-90)
        p.move_forward(0.8)
        bottom = p.position

        angle = 25
        p.stroke_mode(0.30, gray)
        p.turn_to(90 - angle)
        p.arc_to(top)
        p.turn_left(180 - 2 * angle)
        p.arc_to(bottom)

    p.move_to((-2, 1))
    eye()
    p.move_to((2, 1))
    eye()

    # Ears.
    p.stroke_mode(1.0, gray)
    p.move_to((1, 5))
    p.turn_to(20)
    p.line_forward(3.5)
    p.turn_to(-85)
    p.line_forward(4)
    p.move_to((-1, 5))
    p.turn_to(180 - 20)
    p.line_forward(3.5)
    p.turn_to(180 + 85)
    p.line_forward(4)


if __name__ == '__main__':
    p = Pen()
    draw(p)
    print(p.paper.format_svg())
