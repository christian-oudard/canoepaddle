from canoepaddle import Pen
from canoepaddle.pen import flip_angle_y

p = Pen()
p.set_width(2)
p.move_to((0, 0))
p.turn_to(0)
for _ in range(2):
    p.line_forward(5)
    p.turn_right(90)
    p.line_forward(5)
    p.turn_left(90)
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
