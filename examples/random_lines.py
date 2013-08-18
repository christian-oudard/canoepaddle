from collections import defaultdict
import random

from canoepaddle import Pen
from canoepaddle.error import SegmentError


# Randomly draw lines between random points. Don't draw more than two lines
# that meet at the same point.

def gen_points(num_points):
    for _ in range(num_points):
        x = random.uniform(0.0, 1.0)
        y = random.uniform(0.0, 1.0)
        yield x, y


def gen_lines(num_points, num_lines):
    points = list(gen_points(num_points))
    point_occupancy = defaultdict(int)
    for _ in range(num_lines):
        a = random.choice(points)
        if point_occupancy[a] >= 2:
            continue
        else:
            point_occupancy[a] += 1

        b = random.choice(points)
        if point_occupancy[b] >= 2:
            continue
        else:
            point_occupancy[b] += 1

        yield a, b


if __name__ == '__main__':
    # Now that the lines are calculated, draw the figure.
    while True:
        p = Pen()
        p.stroke_mode(0.01)
        for a, b in gen_lines(200, 100):
            p.move_to(a)
            p.line_to(b)
            p.break_stroke()
        try:
            p.paper.join_paths()
        except SegmentError:
            continue
        else:
            break
    print(p.paper.format_svg(6, resolution=1000, background='#808080'))
