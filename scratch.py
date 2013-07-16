from canoepaddle import Pen

p = Pen()

#p.paper.show_joints = True
#p.paper.show_bones = True
p.paper.show_nodes = True

p.set_width(0.5)
p.move_to((-2, 0))
p.turn_to(0)
p.line_forward(1)
p.turn_left(90)
p.line_forward(1)
p.turn_right(90)
p.arc_right(90, 1)
p.arc_left(90, 1)
p.turn_left(90)
p.line_forward(1)

p.paper.set_view_box(-3, -3, 6, 6)
p.paper.set_precision(2)

p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: none;
    '''
)
print(p.paper.format_svg(thick=True))
