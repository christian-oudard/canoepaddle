from nose.tools import assert_equal

from util import (
    assert_path_data,
    sqrt2,
)

from canoepaddle import Pen, Paper, Bounds


def test_mirror_lines():

    def stroke(p):
        p.fill_mode()
        p.move_to((0, 0))
        p.turn_to(180)
        p.move_forward(6)
        p.turn_to(0)
        p.line_forward(6)
        p.turn_right(60)
        p.line_forward(6)

    p = Pen()
    stroke(p)
    assert_path_data(
        p, 2,
        'M-6.00,0.00 L0.00,0.00 L3.00,5.20'
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_x(0)
    assert_path_data(
        p, 2,
        'M6.00,0.00 L0.00,0.00 L-3.00,5.20'
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_x(1)
    assert_path_data(
        p, 2,
        'M8.00,0.00 L2.00,0.00 L-1.00,5.20'
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_y(0)
    assert_path_data(
        p, 2,
        'M-6.00,0.00 L0.00,0.00 L3.00,-5.20'
    )


def test_mirror_arcs():

    def stroke(p):
        p.fill_mode()
        p.move_to((0, 0))
        p.turn_to(0)
        p.arc_left(90, 3)
        p.arc_right(90, 3)

    p = Pen()
    stroke(p)
    assert_path_data(
        p, 1,
        (
            'M0.0,0.0 A 3.0,3.0 0 0 0 3.0,-3.0 '
            'A 3.0,3.0 0 0 1 6.0,-6.0'
        )
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_x(0)
    assert_path_data(
        p, 1,
        (
            'M0.0,0.0 A 3.0,3.0 0 0 1 -3.0,-3.0 '
            'A 3.0,3.0 0 0 0 -6.0,-6.0'
        )
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_y(0)
    assert_path_data(
        p, 1,
        (
            'M0.0,0.0 A 3.0,3.0 0 0 1 3.0,3.0 '
            'A 3.0,3.0 0 0 0 6.0,6.0'
        )
    )


def test_mirror_lines_thick():

    def stroke(p):
        p.stroke_mode(sqrt2)
        p.move_to((0, 0))
        p.turn_to(45)
        p.line_forward(3 * sqrt2)

    p = Pen()
    stroke(p)
    assert_path_data(
        p, 1,
        ['M-0.5,-0.5 L0.5,0.5 L3.5,-2.5 L2.5,-3.5 L-0.5,-0.5 z']
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_x(0)
    assert_path_data(
        p, 1,
        ['M-0.5,0.5 L0.5,-0.5 L-2.5,-3.5 L-3.5,-2.5 L-0.5,0.5 z']
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_y(0)
    assert_path_data(
        p, 1,
        ['M0.5,-0.5 L-0.5,0.5 L2.5,3.5 L3.5,2.5 L0.5,-0.5 z']
    )


def test_mirror_arcs_thick():

    def stroke(p):
        p.stroke_mode(2.0)
        p.move_to((0, 0))
        p.turn_to(0)
        p.arc_left(90, 5)

    p = Pen()
    stroke(p)
    assert_path_data(
        p, 1,
        (
            'M0.0,-1.0 L0.0,1.0 A 6.0,6.0 0 0 0 6.0,-5.0 '
            'L4.0,-5.0 A 4.0,4.0 0 0 1 0.0,-1.0 z'
        )
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_x(0)
    assert_path_data(
        p, 1,
        (
            'M0.0,1.0 L0.0,-1.0 A 4.0,4.0 0 0 1 -4.0,-5.0 '
            'L-6.0,-5.0 A 6.0,6.0 0 0 0 0.0,1.0 z'
        )
    )

    p = Pen()
    stroke(p)
    p.paper.mirror_y(0)
    assert_path_data(
        p, 1,
        (
            'M0.0,-1.0 L0.0,1.0 A 4.0,4.0 0 0 1 4.0,5.0 '
            'L6.0,5.0 A 6.0,6.0 0 0 0 0.0,-1.0 z'
        )
    )


def test_mirror_end_slant():
    paper = Paper()

    p = Pen()
    p.stroke_mode(sqrt2)
    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(5 * sqrt2, end_slant=45)
    p.paper.mirror_x(0)
    paper.merge(p.paper)

    p = Pen()
    p.stroke_mode(sqrt2)
    p.move_to((0, 0))
    p.turn_to(45)
    p.line_forward(5 * sqrt2)
    paper.merge(p.paper)

    paper.join_paths()
    paper.fuse_paths()

    assert_path_data(
        paper, 1,
        'M-5.5,4.5 L-4.5,5.5 L5.5,-4.5 L4.5,-5.5 L-5.5,4.5 z'
    )


def test_mirror_bounds():
    paper = Paper()
    paper.override_bounds(0, 0, 1, 1)
    paper.mirror_x(2)
    assert_equal(
        paper.bounds(),
        Bounds(3, 0, 4, 1)
    )
    paper.mirror_y(-1)
    assert_equal(
        paper.bounds(),
        Bounds(3, -3, 4, -2)
    )
