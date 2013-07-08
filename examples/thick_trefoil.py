from canoepaddle import Pen

p = Pen()
p.set_width(1.0)


def trefoil(origin, radius, num_leaves, leaf_angle, step=1):
    p.turn_to(90)
    points = []
    for i in range(num_leaves):
        p.move_to(origin)
        p.turn_right(360 / num_leaves)
        p.move_forward(radius)
        points.append(p.position)

    p.move_to(points[0])
    for i in range(num_leaves):
        next_point = points[((i + 1) * step) % num_leaves]
        p.turn_toward(origin)
        p.turn_right(leaf_angle / 2)
        p.arc_to(next_point)

trefoil((0, 0), 8, 3, 110)

p.paper.set_style('''
    stroke: black;
    stroke-width: 0.15;
    stroke-linecap: round;
    fill: red;
''')
print(p.paper.format_svg(thick=True))
