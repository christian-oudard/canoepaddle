from nose.tools import assert_equal, assert_raises
from .util import assert_path_data
from canoepaddle import Pen, Paper, Bounds


def test_copy_no_paper():
    p1 = Pen()
    p1.fill_mode()
    p1.move_to((0, 0))
    p1.turn_to(0)
    p1.line_forward(5)
    p2 = p1.copy()
    p2.line_forward(5)

    assert_path_data(
        p1, 0,
        'M0,0 L5,0'
    )
    assert_path_data(
        p2, 0,
        'M5,0 L10,0'
    )


def test_copy_log():
    p1 = Pen()
    p1.fill_mode()
    p1.move_to((0, 0))
    p1.turn_to(0)
    p1.line_forward(5)
    p2 = p1.copy(paper=True)
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
    p1 = Pen()
    p1.fill_mode()

    p1.move_to((0, 0))
    p1.turn_to(0)
    p1.arc_left(90, radius=5)

    p2 = p1.copy(paper=True)
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
    p = p.copy(paper=True)
    svg_data = p.paper.format_svg(0)
    assert (
        '<text x="0" y="0" font-family="sans-serif" font-size="1" '
        'fill="#000000">abcd</text>'
    ) in svg_data


def test_copy_custom_cap():
    # Regression test for a bug where doing pen.copy() in a cap function would
    # break outline drawing.
    p = Pen()
    p.stroke_mode(2.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

    def copy_cap(pen, end):
        pen.copy()
        pen.line_to(end)

    p.last_segment().end_cap = copy_cap

    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L6,1 L6,-5 L4,-5 L4,-1 L0,-1 z'
    )
