from canoepaddle import Pen, format_svg

p = Pen()
p.set_width(1.0)
p.flip_x()
p.turn_to(180)
p.move_forward(6)
p.turn_to(0)
p.stroke_forward(6)
p.turn_right(60)
p.stroke_forward(6)
path_data = p.paper.to_svg_path_thick(precision=2)

path_style = '''
    stroke: black;
    stroke-width: 0.1;
    stroke-linecap: butt;
    fill: #a00;
'''
print(format_svg(path_data, path_style))
