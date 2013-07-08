from canoepaddle import Pen

p = Pen()
p.set_width(1.0)
p.move_to((0, 0))
p.turn_to(0)
p.line_forward(5, start_angle=-45, end_angle=30)

p.paper.set_precision(2)

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
