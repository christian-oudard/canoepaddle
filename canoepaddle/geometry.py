import vec
from .point import epsilon


def intersect_lines(a, b, c, d):
    """
    Find the intersection of lines a-b and c-d.
    """
    # Reference: http://geomalgorithms.com/a05-_intersect-1.html
    u = vec.vfrom(a, b)
    v = vec.vfrom(c, d)
    w = vec.vfrom(c, a)
    u_perp_dot_v = vec.dot(vec.perp(u), v)
    if abs(u_perp_dot_v) < epsilon:
        raise ValueError('No intersection point.')
    v_perp_dot_w = vec.dot(vec.perp(v), w)
    s = v_perp_dot_w / u_perp_dot_v
    return vec.add(a, vec.mul(u, s))
