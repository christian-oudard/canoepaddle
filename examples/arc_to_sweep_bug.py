from canoepaddle import Pen

p = Pen()

p.move_to((0, 0))
p.turn_to(0)

p.line_forward(2)
p.arc_left(45, 2)
p.turn_left(135)
p.line_forward(2)
p.arc_to((p.position.x, -p.position.y), center=(0, 0))

p.paper.set_style('''
    stroke: black;
    stroke-width: 0.25;
    stroke-linecap: round;
    fill: none;
''')
print(p.paper.format_svg(thick=False))
