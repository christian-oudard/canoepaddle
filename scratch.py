from canoepaddle import Pen

p = Pen()

p.move_to((-5, 0))
p.turn_to(0)
p.arc_to((0, 5))
p.arc_to((5, 0))

p.move_to((-5, 0))
p.turn_to(0)
p.arc_to((0, -5))
p.arc_to((5, 0))

#p.paper.set_precision(3)

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
#print(p.paper.format_svg(thick=True))
print(p.paper.format_svg(thick=False))
