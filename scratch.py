from canoepaddle import Pen
from canoepaddle.pen import flip_angle_y

p = Pen()
p.set_width(1.0)

p = Pen()
p.set_width(1.0)

p.move_to((-1, 0))
p.turn_to(90)
p.arc_to((0, 5))
p.turn_to(flip_angle_y(p.heading))
p.arc_to((-1, 0))

p.paper.set_precision(3)

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
