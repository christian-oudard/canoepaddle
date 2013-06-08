from canoepaddle import Pen

p = Pen()

p.move_to((0, 0))
p.circle(3)
p.circle(4)
p.circle(5)

p.turn_to(180)
p.stroke_forward(8)

p.move_to((-4, 0))
p.turn_to(45)
p.move_forward(-3)
p.stroke_forward(6)

p.paper.set_style('''
    stroke: black;
    stroke-width: 0.1;
    fill: none;
''')
print(p.paper.format_svg())
