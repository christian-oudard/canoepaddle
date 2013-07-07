from canoepaddle import Pen

p = Pen()
p.set_width(2.0)

p.move_to((3, 0))
p.turn_to(90)
p.arc_left(270, 3)

p.paper.set_precision(0)

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
