from nose.tools import assert_equal, assert_raises
from util import assert_path_data

from canoepaddle import Pen, Paper, Bounds


def test_format_empty_bounds():
    paper = Paper()
    svg_data = paper.format_svg()
    assert 'viewBox="-10 -10 20 20"' in svg_data


def test_override_bounds():
    # Test that the view box gets set correctly.
    paper = Paper()
    paper.override_bounds(0, 0, 8, 11)

    # The view box is transformed into svg coordinates by flipping the
    # Y-coordinate and adjusting for height.
    svg_data = paper.format_svg()
    assert 'viewBox="0 -11 8 11"' in svg_data

    paper.override_bounds(-10, -10, 10, 10)
    svg_data = paper.format_svg()
    assert 'viewBox="-10 -10 20 20"' in svg_data


def test_override_bounds_copy():
    # Get the bounds of a Paper, modify them, then set them back changed.
    paper = Paper()
    paper.override_bounds(0, 0, 1, 1)

    bounds = paper.bounds()
    bounds.right = 5

    assert_equal(paper.bounds(), Bounds(0, 0, 1, 1))
    paper.override_bounds(bounds)
    assert_equal(paper.bounds(), Bounds(0, 0, 5, 1))

    # This works on non-overridden Papers as well.
    paper = Paper()

    p = Pen()
    p.fill_mode()
    p.move_to((0.5, 0.5))
    p.circle(0.5)

    bounds = p.paper.bounds()
    bounds.right = 5

    assert_equal(p.paper.bounds(), Bounds(0, 0, 1, 1))
    p.paper.override_bounds(bounds)
    assert_equal(p.paper.bounds(), Bounds(0, 0, 5, 1))


def test_translate():
    p = Pen()
    p.stroke_mode(1.0)

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(3)
    p.arc_left(90, 3)
    p.turn_left(90)
    p.move_forward(3)
    p.fill_mode()
    p.circle(0.5)
    p.move_forward(3)
    p.square(1)

    p.paper.translate((1, 1))

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M1.0,-1.5 L1.0,-0.5 L4.0,-0.5 A 3.5,3.5 0 0 0 '
                '7.5,-4.0 L6.5,-4.0 A 2.5,2.5 0 0 1 4.0,-1.5 L1.0,-1.5 z" '
                'fill="#000000" />'
            ),
            (
                '<path d="M4.5,-4.0 A 0.5,0.5 0 0 0 3.5,-4.0 '
                'A 0.5,0.5 0 0 0 4.5,-4.0 z" fill="#000000" />'
            ),
            (
                '<path d="M0.5,-3.5 L1.5,-3.5 L1.5,-4.5 L0.5,-4.5 L0.5,-3.5 z" '
                'fill="#000000" />'
            ),
        ]
    )


def test_translate_override_bounds():
    # Translate a paper that has overridden bounds. The bounds update as well.
    paper = Paper()
    paper.override_bounds(0, 0, 1, 1)
    paper.translate((3, 4))
    assert_equal(
        paper.bounds(),
        Bounds(3, 4, 4, 5)
    )

    # When bounds=False is passed, then the bounds do not update.
    paper = Paper()
    paper.override_bounds(0, 0, 1, 1)
    paper.translate((3, 4), bounds=False)
    assert_equal(paper.bounds(), Bounds(0, 0, 1, 1))

    # This also works if the bounds are not overridden.
    p = Pen()
    p.fill_mode()
    p.move_to((0.5, 0.5))
    p.circle(0.5)
    assert_equal(p.paper.bounds(), Bounds(0, 0, 1, 1))

    p.paper.translate((3, 4), bounds=False)

    assert_equal(p.paper.bounds(), Bounds(0, 0, 1, 1))
    assert_equal(p.last_path().bounds(), Bounds(3, 4, 4, 5))


def test_center_on_xy():
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(4)

    p.move_to((2, 1))
    p.circle(1)

    p.paper.center_on_x(0)

    assert_equal(
        p.paper.svg_elements(0),
        [
            '<path d="M-2,-1 L-2,1 L2,1 L2,-1 L-2,-1 z" fill="#000000" />',
            '<path d="M2,-1 A 2,2 0 0 0 -2,-1 A 2,2 0 0 0 2,-1 z" fill="#000000" />',
        ]
    )

    p.paper.center_on_y(0)

    assert_equal(
        p.paper.svg_elements(1),
        [
            (
                '<path d="M-2.0,0.0 L-2.0,2.0 L2.0,2.0 L2.0,0.0 L-2.0,0.0 z" '
                'fill="#000000" />'
            ),
            (
                '<path d="M2.0,0.0 A 2.0,2.0 0 0 0 -2.0,0.0 '
                'A 2.0,2.0 0 0 0 2.0,0.0 z" fill="#000000" />'
            ),
        ]
    )


def test_paper_merge():
    # Merge two drawings together.
    paper = Paper()

    p = Pen()
    p.fill_mode()
    p.turn_to(0)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    p = Pen()
    p.fill_mode()
    p.turn_to(180)
    p.arc_left(180, 5)
    p.paper.center_on_x(0)
    paper.merge(p.paper)

    assert_path_data(
        paper, 1,
        [
            'M-2.5,0.0 A 5.0,5.0 0 0 0 -2.5,-10.0',
            'M2.5,0.0 A 5.0,5.0 0 0 0 2.5,10.0',
        ]
    )


def test_empty_bounds():
    assert_raises(ValueError, lambda: Paper().bounds())


def test_merge_bounds():
    def draw():
        p = Pen()
        p.fill_mode()
        p.move_to((0, 0))
        p.circle(2)
        paper1 = p.paper

        p = Pen()
        p.fill_mode()
        p.move_to((3, 0))
        p.circle(1)
        paper2 = p.paper

        return paper1, paper2

    # Empty papers, no overridden bounds.
    paper1 = Paper()
    paper2 = Paper()
    paper1.merge(paper2)
    assert_raises(ValueError, lambda: paper1.bounds())

    # Empty papers with overridden bounds on both sides.
    paper1 = Paper()
    paper1.override_bounds(0, 0, 1, 1)

    paper2 = Paper()
    paper2.override_bounds(1, 0, 2, 1)

    paper1.merge(paper2)
    assert_equal(paper1.bounds(), Bounds(0, 0, 2, 1))

    # No bounds overriding or merging.
    paper1, paper2 = draw()
    assert_equal(paper1.bounds(), Bounds(-2, -2, 2, 2))
    assert_equal(paper2.bounds(), Bounds(2, -1, 4, 1))

    # Merge with no overriding.
    paper1, paper2 = draw()
    paper1.merge(paper2)
    assert_equal(paper1.bounds(), Bounds(-2, -2, 4, 2))

    # Override the top one.
    paper1, paper2 = draw()
    paper2.override_bounds(-1, -1, 1, 1)
    paper1.merge(paper2)
    assert_equal(paper1.bounds(), Bounds(-2, -2, 2, 2))

    # Override the bottom one.
    paper1, paper2 = draw()
    bounds = paper1.bounds()
    bounds.top = 10
    paper1.override_bounds(bounds)
    paper1.merge(paper2)
    assert_equal(paper1.bounds(), Bounds(-2, -2, 4, 10))

    # Empty bounds on bottom page.
    paper1, paper2 = draw()
    paper1.override_bounds(-1, -1, 1, 1)
    paper3 = Paper()
    paper3.merge(paper1)
    assert_equal(paper3.bounds(), Bounds(-1, -1, 1, 1))

    # Empty bounds on top page.
    paper1, paper2 = draw()
    paper3 = Paper()
    paper1.override_bounds(-1, -1, 1, 1)
    paper1.merge(paper3)
    assert_equal(paper1.bounds(), Bounds(-1, -1, 1, 1))


def test_two_pens_one_paper():
    paper = Paper()
    p1 = Pen(paper)
    p2 = Pen(paper)
    p1.fill_mode()
    p2.fill_mode()
    p1.move_to((0, 0))
    p2.move_to((0, 0))
    p1.line_to((0, 1))
    p2.line_to((2, 0))

    assert_path_data(
        paper, 0,
        ['M0,0 L0,-1', 'M0,0 L2,0']
    )
