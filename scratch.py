from canoepaddle import Pen
from canoepaddle.pen import flip_angle_y

p = Pen()
p.flip_x()
p.turn_to(180)
p.move_forward(6)
p.turn_to(0)
p.line_forward(6)
p.turn_right(60)
p.line_forward(6)

p.paper.set_precision(2)

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
print(p.paper.format_svg(thick=False))
