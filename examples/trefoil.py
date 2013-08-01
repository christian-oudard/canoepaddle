from canoepaddle import Pen

#TODO: Make the ends close correctly.

p = Pen()
p.set_width(0.15)


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

trefoil((-6, 6), 3, 3, 110)
trefoil((0, 6), 2.7, 4, 120)
trefoil((6, 6), 2.7, 4, 70)
trefoil((-6, 0), 2.7, 5, 70)
trefoil((0, 0), 2.7, 5, 130)
trefoil((6, 0), 2.7, 5, 110, step=2)
trefoil((-6, -6), 2.7, 31, 20, step=14)
trefoil((0, -6), 3, 8, 120, step=3)
trefoil((6, -6), 2.7, 30, -90, step=1)

print(p.paper.format_svg())
