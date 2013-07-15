from canoepaddle import Pen

p = Pen()

p.turn_to(0)

p.set_color('red')
p.circle(2)
p.move_forward(1)
p.set_color('green')
p.circle(2)
p.turn_left(120)
p.move_forward(1)
p.set_color('blue')
p.circle(2)

#p.paper.show_joints = True
#p.paper.show_bones = True
#p.paper.show_nodes = True
print(p.paper.format_svg(thick=False))
