from canoepaddle import Pen

p = Pen()
p.set_width(1.0)

top = (0, 5)
left = (-2, 0)
right = (2, 0)

p.move_to(left)
p.turn_toward(top)
p.turn_right(5)
p.arc_to(top, start_angle=0)
p.turn_toward(right)
p.turn_left(5)
p.arc_to(right, end_angle=0)

p.paper.set_precision(3)

#p.paper.show_joints = True
#p.paper.show_bones = True
p.paper.show_nodes = True
p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: none;
    '''
)
print(p.paper.format_svg(thick=True))
