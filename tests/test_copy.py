from nose.tools import assert_equal, assert_raises
from util import assert_path_data
from canoepaddle import Pen, Paper, Bounds


def test_copy_log():
    p1 = Pen()
    p1.fill_mode()
    p1.move_to((0, 0))
    p1.turn_to(0)
    p1.line_forward(5)
    p2 = p1.copy()
    p2.line_forward(5)

    assert_equal(
        p1.log(),
        [
            'fill_mode()', 'move_to((0, 0))', 'turn_to(0)', 'line_forward(5)',
        ]
    )
    assert_path_data(
        p1, 0,
        'M0,0 L5,0'
    )
    assert_equal(
        p2.log(),
        [
            'fill_mode()', 'move_to((0, 0))', 'turn_to(0)', 'line_forward(5)',
            'line_forward(5)',
        ]
    )
    assert_path_data(
        p2, 0,
        'M0,0 L5,0 L10,0'
    )


def test_copy_arc():
    # Draw arcs with all four combinations of sweep and direction flags.
    p1 = Pen()
    p1.fill_mode()

    p1.move_to((0, 0))
    p1.turn_to(0)
    p1.arc_left(90, radius=5)

    p2 = p1.copy()
    p2.arc_left(90, radius=5)

    assert_path_data(
        p1, 0,
        'M0,0 A 5,5 0 0 0 5,-5'
    )
    assert_path_data(
        p2, 0,
        'M0,0 A 5,5 0 0 0 5,-5 A 5,5 0 0 0 0,-10'
    )


def test_copy_override_bounds():
    paper1 = Paper()
    paper1.override_bounds(0, 0, 1, 1)
    paper2 = paper1.copy()
    assert_equal(
        paper2.bounds(),
        Bounds(0, 0, 1, 1),
    )


def test_copy_no_mode():
    p = Pen()
    assert_raises(
        AttributeError,
        lambda: p.mode
    )
    p = p.copy()
    assert_raises(
        AttributeError,
        lambda: p.mode
    )


def test_copy_text():
    p = Pen()
    p.move_to((0, 0))
    p.text('abcd', 1, 'sans-serif')
    p = p.copy()
    svg_data = p.paper.format_svg(0)
    assert (
        '<text x="0" y="0" font-family="sans-serif" font-size="1" '
        'fill="#000000">abcd</text>'
    ) in svg_data
