from canoepaddle import Pen

p = Pen()

p.move_to((0, 0))
p.turn_to(0)

radius = 0.01

for _ in range(100):
    p.circle(radius)
    p.turn_left(15)
    new_radius = radius * 1.1
    p.move_forward(radius + new_radius)
    radius = new_radius

p.paper.set_style('''
    stroke: none;
    fill: green;
''')
print(p.paper.format_svg())
