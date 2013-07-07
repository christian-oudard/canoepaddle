from canoepaddle import Pen

p = Pen()
p.set_width(1.0)

p.move_to((0, -3))
p.turn_to(90)
p.line_forward(3)
p.turn_right(90)
p.line_forward(3)
p.turn_left(90)
p.arc_left(180, 3)
p.line_forward(3)

#p.paper.show_joints = True
p.paper.show_bones = True
p.paper.show_nodes = True
p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: none;
    '''
)
print(p.paper.format_svg(thick=True))
