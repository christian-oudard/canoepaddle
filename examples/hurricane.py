# TODO: round endcaps

from canoepaddle import Pen

p = Pen()
p.set_width(1.0)


def arm(inner=1.5, outer=3):
    p.move_forward(inner)
    p.turn_right(90)
    p.arc_right(200, radius=outer)
    p.circle(p.width / 2)  # Makeshift round endcaps.

orientation = 70

p.move_to((0, 0))
p.path_circle(1.5)

p.move_to((0, 0))
p.turn_to(orientation)
arm()

p.move_to((0, 0))
p.turn_to(180 + orientation)
arm()

print(p.paper.format_svg())
