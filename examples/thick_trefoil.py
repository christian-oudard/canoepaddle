from canoepaddle import Pen


p = Pen()


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

p.set_stroke_mode(1.0, '#a00')
trefoil((0, 0), 8, 3, 110)
p.set_outline_mode(1.0, 0.1, '#111')
trefoil((0, 0), 8, 3, 110)

print(p.paper.format_svg())
