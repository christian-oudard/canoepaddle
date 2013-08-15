from collections import defaultdict
import itertools
from math import sqrt

import vec
from .point import float_equal, points_equal, epsilon


def closest_point_to(target, points):
    return min(
        points,
        key=lambda p: vec.mag2(vec.vfrom(target, p))
    )


def intersect_lines(a, b, c, d, segment=False):
    """
    Find the intersection of lines a-b and c-d.

    If the "segment" argument is true, treat the lines as segments, and check
    whether the intersection point is off the end of either segment.
    """
    # Reference:
    # http://geomalgorithms.com/a05-_intersect-1.html
    u = vec.vfrom(a, b)
    v = vec.vfrom(c, d)
    w = vec.vfrom(c, a)

    u_perp_dot_v = vec.dot(vec.perp(u), v)
    if float_equal(u_perp_dot_v, 0):
        return None  # We have collinear segments, no single intersection.

    v_perp_dot_w = vec.dot(vec.perp(v), w)
    s = v_perp_dot_w / u_perp_dot_v
    if segment and (s < 0 or s > 1):
        return None

    u_perp_dot_w = vec.dot(vec.perp(u), w)
    t = u_perp_dot_w / u_perp_dot_v
    if segment and (t < 0 or t > 1):
        return None

    return vec.add(a, vec.mul(u, s))


def quadratic_formula(a, b, c):
    # Reference:
    # http://people.csail.mit.edu/bkph/articles/Quadratics.pdf
    if b >= 0:
        d = -b - sqrt(b**2 - 4*a*c)
        return (
            d / (2 * a),
            (2 * c) / d,
        )
    else:
        d = -b + sqrt(b**2 - 4*a*c)
        return (
            (2 * c) / d,
            d / (2 * a),
        )


def intersect_circle_line(center, radius, line_start, line_end):
    """
    Find the intersection of a circle with a line.
    """
    radius = abs(radius)

    # First check whether the line is too far away, or if we have a
    # single point of contact.
    # Reference:
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    r = vec.vfrom(center, line_start)
    v = vec.perp(vec.vfrom(line_start, line_end))
    d = vec.proj(r, v)
    dist = vec.mag(d)
    if float_equal(dist, radius):
        # Single intersection point, because the circle and line are tangent.
        point = vec.add(center, d)
        return [point]
    elif dist > radius:
        return []

    # Set up parametric equations for the line and the circle, and solve them.
    # Reference:
    # http://www.cs.cf.ac.uk/Dave/CM0268/PDF/circle_line_intersect_proof.pdf
    xc, yc = center
    x0, y0 = line_start
    x1, y1 = line_end
    line_x, line_y = (x1 - x0), (y1 - y0)  # f, g
    dx, dy = (x0 - xc), (y0 - yc)

    a = line_x**2 + line_y**2
    b = 2 * (line_x * dx + line_y * dy)
    c = dx**2 + dy**2 - radius**2
    t0, t1 = quadratic_formula(a, b, c)

    return [
        (
            x0 + line_x * t0,
            y0 + line_y * t0,
        ),
        (
            x0 + line_x * t1,
            y0 + line_y * t1,
        ),
    ]


def intersect_circles(center1, radius1, center2, radius2):
    radius1 = abs(radius1)
    radius2 = abs(radius2)

    if radius2 > radius1:
        return intersect_circles(center2, radius2, center1, radius1)

    transverse = vec.vfrom(center1, center2)
    dist = vec.mag(transverse)

    # Check for identical or concentric circles. These will have either
    # no points in common or all points in common, and in either case, we
    # return an empty list.
    if points_equal(center1, center2):
        return []

    # Check for exterior or interior tangent.
    radius_sum = radius1 + radius2
    radius_difference = abs(radius1 - radius2)
    if (
        float_equal(dist, radius_sum) or
        float_equal(dist, radius_difference)
    ):
        return [
            vec.add(
                center1,
                vec.norm(transverse, radius1)
            ),
        ]

    # Check for non intersecting circles.
    if dist > radius_sum or dist < radius_difference:
        return []

    # If we've reached this point, we know that the two circles intersect
    # in two distinct points.
    # Reference:
    # http://mathworld.wolfram.com/Circle-CircleIntersection.html

    # Pretend that the circles are arranged along the x-axis.
    # Find the x-value of the intersection points, which is the same for both
    # points. Then find the chord length "a" between the two intersection
    # points, and use vector math to find the points.
    dist2 = vec.mag2(transverse)
    x = (dist2 - radius2**2 + radius1**2) / (2 * dist)
    a = (
        (1 / dist) *
        sqrt(
            (-dist + radius1 - radius2) *
            (-dist - radius1 + radius2) *
            (-dist + radius1 + radius2) *
            (dist + radius1 + radius2)
        )
    )
    chord_middle = vec.add(
        center1,
        vec.norm(transverse, x),
    )
    perp = vec.perp(transverse)
    return [
        vec.add(chord_middle, vec.norm(perp, a / 2)),
        vec.add(chord_middle, vec.norm(perp, -a / 2)),
    ]


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ...

    >>> list(pairwise([1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def collinear(*points):
    """
    Determine whether the given points are collinear in the order they were
    passed in.
    """
    # Find vectors between successive points, in a chain.
    vectors = []
    for a, b in pairwise(points):
        vectors.append(vec.vfrom(a, b))
    # Find the angles between successive vectors in the chain. Actually we skip
    # the inverse cosine calculation required to find angle, and just use ratio
    # instead. The ratio is the cosine of the angle between the vectors.
    for u, v in pairwise(vectors):
        ratio = vec.dot(u, v) / (vec.mag(u) * vec.mag(v))
        if ratio < 1.0 - epsilon:
            return False
    return True


def find_point_pairs(points):
    """
    Collect pairs of points that are in the same spot, with no other
    points nearby.
    """

    # Construct an equality graph.
    # TODO: Optimize this using a grid hash, it's O(N^2) right now.
    # http://programmers.stackexchange.com/questions/129892
    graph = defaultdict(list)
    n = len(points)
    for i in range(n):
        a = points[i]
        for j in range(i + 1, n):
            b = points[j]
            if points_equal(a, b):
                graph[i].append(j)
                graph[j].append(i)

    # If two points are paired, then they will each only have one
    # neighbor, each other.
    pairs = []
    paired_indexes = set()
    for i in range(n):
        if i in paired_indexes:
            continue
        neighbors_i = graph[i]
        if len(neighbors_i) == 1:
            j = neighbors_i[0]
            neighbors_j = graph[j]
            if len(neighbors_j) == 1:
                pairs.append((i, j))
                paired_indexes.add(i)
                paired_indexes.add(j)

    return pairs
