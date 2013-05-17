from canoepaddle import Pen, format_svg

p = Pen()
p.set_width(1.0)

def arm(inner=1.5, outer=3):
    p.move_forward(inner)
    p.turn_right(90)
    p.arc_right(180, radius=inner)
    p.arc_right(200, radius=outer)

orientation = 70

p.move_to((0, 0))
p.turn_to(orientation)
arm()

p.move_to((0, 0))
p.turn_to(180 + orientation)
arm()

path_data = p.paper.to_svg_path()

path_style = '''
    stroke: black;
    stroke-width: 1.0;
    stroke-linecap: round;
    fill: none;
'''

print(format_svg(path_data, path_style))
