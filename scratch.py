from canoepaddle import Pen

p = Pen()
p.move_to((0, 0))
p.turn_to(0)

p.set_width(0.8)
p.line_forward(5)
p.turn_left(45)
p.set_width(3.0)
p.arc_left(90, 5)

p.turn_to(-180)
p.line_forward(5)
p.turn_left(45)
p.set_width(0.8)
p.arc_left(45, 5)

p.turn_right(90)
p.set_width(3.0)
p.arc_right(90, 4)

p.paper.set_precision(3)

#p.paper.show_joints = True
#p.paper.show_bones = True
#p.paper.show_nodes = True
p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: none;
    '''
)
print(p.paper.format_svg(thick=True))
