from canoepaddle import Pen

p = Pen()


def petal(start_radius, distance, heading):
    radius = start_radius
    p.move_to((0, 0))
    p.turn_to(heading)
    p.move_forward(distance)
    for _ in range(50):
        p.circle(radius)
        p.turn_left(12)
        new_radius = radius / 1.1
        p.move_forward(radius + new_radius)
        radius = new_radius

num_petals = 8
heading = 0
for _ in range(num_petals):
    petal(0.7, 2.0, heading)
    heading += (360 / num_petals)

p.paper.set_style('''
    stroke: none;
    fill: #84f;
''')
print(p.paper.format_svg())
