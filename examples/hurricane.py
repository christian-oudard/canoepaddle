from canoepaddle import Pen

p = Pen()


def arm(inner=1.5, outer=3):
    p.move_forward(inner)
    p.turn_right(90)
    p.arc_right(200, radius=outer)

orientation = 70

p.move_to((0, 0))
p.circle(1.5)

p.move_to((0, 0))
p.turn_to(orientation)
arm()

p.move_to((0, 0))
p.turn_to(180 + orientation)
arm()

p.paper.set_style('''
    stroke: black;
    stroke-width: 1.0;
    stroke-linecap: round;
    fill: none;
''')
print(p.paper.format_svg())
