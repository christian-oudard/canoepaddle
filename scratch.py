from canoepaddle import Pen

p = Pen()
p.set_width(0.5)

p.move_to((-5, 0))
p.turn_to(0)
p.arc_to((5, 0), center=(0, -200), start_angle=-5, end_angle=5)

p.paper.set_style(
    '''
    stroke: black;
    stroke-width: 0.05;
    fill: red;
    '''
)
print(p.paper.format_svg(thick=True))
