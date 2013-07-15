from canoepaddle import Pen

if True:
    p = Pen()
    p.move_to((0, 0))
    p.line_to((1, 1))
    p.paper.set_precision(0)

    p.paper.set_view_box(-1, -1, 3, 3)

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
