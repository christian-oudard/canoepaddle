import math
import re
import os.path

from nose.tools import assert_equal, assert_almost_equal

from canoepaddle.pen import Pen

sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)


def assert_points_equal(a, b):
    xa, ya = a
    xb, yb = b
    assert_almost_equal(xa, xb, places=12)
    assert_almost_equal(ya, yb, places=12)


def assert_segments_equal(s1, s2):
    a1, b1 = s1
    a2, b2 = s2
    assert_points_equal(a1, a2)
    assert_points_equal(b1, b2)


def _read_test_file(svg_filename):
    path = os.path.join(
        os.path.dirname(__file__),
        'files',
        svg_filename,
    )
    with open(path) as f:
        return f.read()


def _extract_path_data(pen_or_paper, precision):
    # Handle passing in a pen or paper object.
    if isinstance(pen_or_paper, Pen):
        pen = pen_or_paper
        paper = pen.paper
    else:
        paper = pen_or_paper

    elements = paper.svg_elements(precision)
    actual_path_data = []
    for element in elements:
        path_data = [
            m.group(1) for m in
            re.finditer(r'd="([^"]*)"', element)
        ]
        if len(path_data) == 0:
            raise AssertionError('Could not find path data in "{}"'.format(element))
        actual_path_data.extend(path_data)
    return actual_path_data


def assert_svg_file(pen_or_paper, precision, svg_filename):
    content = _read_test_file(svg_filename)
    for path_data in _extract_path_data(pen_or_paper, precision):
        assert path_data in content


def assert_path_data(pen_or_paper, precision, target_path_data):
    # Handle strings or lists of strings as target_path_data.
    if isinstance(target_path_data, str):
        target_path_data = [target_path_data]
    actual_path_data = _extract_path_data(pen_or_paper, precision)
    assert_equal(actual_path_data, target_path_data)
