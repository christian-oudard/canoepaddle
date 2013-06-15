from canoepaddle import Pen

p = Pen()
p.set_width(1.0)
p.move_to((0, 0))
p.turn_to(0)
p.arc_left(90, radius=5, start_angle=26, end_angle=45)


p.paper.set_precision(2)
p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: red;
    '''
)
print(p.paper.format_svg(thick=True))
