from canoepaddle import Pen

p = Pen()
p.set_width(2.0)

p.move_to((3, -4))
p.turn_to(90)
p.line_forward(4)
p.arc_left(270, 3)
p.line_forward(1, end_angle=45)

p.paper.set_style('''
    stroke: none;
    fill: #650360;
''')
print(p.paper.format_svg(thick=True))
