from math import sqrt, sin, radians, degrees

import vec
from .point import epsilon, points_equal


def calc_joint_angle(last_segment, new_segment):
    v1_heading = last_segment.end_heading
    v2_heading = new_segment.start_heading

    # Special case for equal widths, more numerically stable around
    # straight joints.
    if abs(last_segment.width - new_segment.width) < epsilon:
        return ((v1_heading + v2_heading) / 2 + 90) % 180

    # Solve the parallelogram created by the previous stroke intersecting
    # with the next stroke. The diagonal of this parallelogram is at the
    # correct joint angle.
    v1 = vec.vfrom(last_segment.a, last_segment.b)
    v2 = vec.vfrom(new_segment.a, new_segment.b)
    theta = (v2_heading - v1_heading) % 180
    sin_theta = sin(radians(theta))
    width1 = last_segment.width
    width2 = new_segment.width
    v1 = vec.norm(v1, width2 * sin_theta)
    v2 = vec.norm(v2, width1 * sin_theta)
    return degrees(vec.heading(vec.vfrom(v1, v2))) % 180


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
    if abs(u_perp_dot_v) < epsilon:
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
            d / 2*a,
            2*c / d,
        )
    else:
        d = -b + sqrt(b**2 - 4*a*c)
        return (
            2*c / d,
            d / 2*a,
        )


def intersect_circle_line(center, radius, line_start, line_end):
    """
    Find the intersection of a circle with a line.
    """
    # Reference:
    # http://www.cs.cf.ac.uk/Dave/CM0268/PDF/circle_line_intersect_proof.pdf
    xc, yc = center
    x0, y0 = line_start
    x1, y1 = line_end
    line_x, line_y = (x1 - x0), (y1 - y0) # f g
    dx, dy = (x0 - xc), (y0 - yc)

    a = line_x**2 + line_y**2
    b = 2 * (line_x * dx + line_y * dy)
    c = dx**2 + dy**2 - radius**2
    t0, t1 = quadratic_formula(a, b, c)

    return (
        (
            x0 + line_x * t0,
            y0 + line_y * t0,
        ),
        (
            x0 + line_x * t1,
            y0 + line_y * t1,
        ),
    )
