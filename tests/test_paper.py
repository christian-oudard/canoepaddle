from nose.tools import assert_equal, assert_raises

from util import (
    assert_path_data,
    sqrt2,
)
from canoepaddle.pen import Pen
from canoepaddle.paper import Paper
from canoepaddle.bounds import Bounds


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


def test_join_paths():
    # Join two paths starting from the same point.
    p = Pen()
    p.fill_mode()

    p.move_to((1, 0))
    p.line_to((0, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M0,0 L1,0 L2,0',
    )

    # Join two paths that end in the same point.
    p = Pen()
    p.fill_mode()

    p.move_to((1, 0))
    p.line_to((0, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((1, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M0,0 L1,0 L2,0',
    )

    # Join three paths going left in normal order.
    p = Pen()
    p.fill_mode()

    p.move_to((3, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((1, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((0, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M3,0 L2,0 L1,0 L0,0',
    )

    # Join three paths going right in normal order.
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.line_to((1, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((3, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M0,0 L1,0 L2,0 L3,0',
    )

    # Join three paths going left in reverse order.
    p = Pen()
    p.fill_mode()

    p.move_to((1, 0))
    p.line_to((0, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((1, 0))
    p.break_stroke()
    p.move_to((3, 0))
    p.line_to((2, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M0,0 L1,0 L2,0 L3,0',
    )

    # Join three paths going right in reverse order.
    p = Pen()
    p.fill_mode()

    p.move_to((2, 0))
    p.line_to((3, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((0, 0))
    p.line_to((1, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M3,0 L2,0 L1,0 L0,0',
    )

    # Join multiple paths together.
    p = Pen()
    p.fill_mode()

    p.move_to((1, 0))
    p.line_to((0, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((1, 1))
    p.break_stroke()
    p.move_to((1, 1))
    p.line_to((2, 1))
    p.break_stroke()
    p.move_to((2, 2))
    p.line_to((2, 1))
    p.break_stroke()

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M0,0 L1,0 L1,-1 L2,-1 L2,-2'
    )

    # Join three paths so one path must reverse multiple times.
    p = Pen()
    p.fill_mode()

    p.move_to((2, 0))
    p.line_to((1, 0))
    p.break_stroke()
    p.move_to((2, 0))
    p.line_to((3, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((0, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M3,0 L2,0 L1,0 L0,0',
    )


def test_join_paths_reference():
    # Join paths in such a way that a single path object must be
    # used as both the "left" and "right" path in different joins.
    p = Pen()
    p.fill_mode()

    p.move_to((3, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((0, 0))
    p.break_stroke()
    p.move_to((4, 0))
    p.line_to((3, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((4, 0))
    p.line_to((5, 0))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M5,0 L4,0 L3,0 L2,0 L1,0 L0,0'
    )


def test_join_paths_loop():
    # Already looped paths should not be affected by join_paths.
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.square(2)

    target = 'M-1,1 L1,1 L1,-1 L-1,-1 L-1,1 z'
    assert_path_data(p, 0, target)
    p.paper.join_paths()
    assert_path_data(p, 0, target)

    # Loops can also be created by joining paths.
    p = Pen()
    p.fill_mode()

    p.move_to((0, 0))
    p.line_to((1, 0))
    p.line_to((1, 1))
    p.break_stroke()
    p.line_to((0, 1))
    p.line_to((0, 0))

    p.paper.join_paths()
    assert_path_data(
        p, 0,
        'M1,-1 L1,0 L0,0 L0,-1 L1,-1 z'
    )

    # The joins can get complicated.
    p = Pen()
    p.fill_mode()

    p.move_to((3, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 2))
    p.break_stroke()
    p.move_to((4, 0))
    p.line_to((3, 0))
    p.break_stroke()
    p.move_to((1, 0))
    p.line_to((2, 0))
    p.break_stroke()
    p.move_to((4, 0))
    p.line_to((2, 2))

    p.paper.join_paths()

    assert_path_data(
        p, 0,
        'M1,0 L2,-2 L4,0 L3,0 L2,0 L1,0 z',
    )


def test_join_paths_thick():
    # Segments join together if possible when join_paths is called.
    p = Pen()
    p.stroke_mode(2.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)
    p.break_stroke()
    p.turn_left(90)
    p.line_forward(5)
    p.paper.join_paths()
    assert_path_data(
        p, 0,
        'M0,-1 L0,1 L6,1 L6,-5 L4,-5 L4,-1 L0,-1 z'
    )


def test_fuse_paths():
    # Create two halves of a stroke in the same direction.
    p = Pen()
    p.stroke_mode(sqrt2)

    p.move_to((-3, 3))
    p.turn_to(-45)
    p.line_forward(3 * sqrt2, start_slant=0)
    p.line_forward(3 * sqrt2, end_slant=0)

    p.paper.fuse_paths()

    assert_path_data(
        p, 1,
        ['M-2.0,-3.0 L-4.0,-3.0 L2.0,3.0 L4.0,3.0 L-2.0,-3.0 z']
    )


def test_join_and_fuse_simple():
    # Create two halves of a stroke in separate directions.
    p = Pen()
    p.stroke_mode(sqrt2)

    p.move_to((0, 0))
    p.turn_to(-45)
    p.line_forward(3 * sqrt2, end_slant=0)

    p.break_stroke()

    p.move_to((0, 0))
    p.turn_to(-45 + 180)
    p.line_forward(3 * sqrt2, end_slant=0)

    p.paper.join_paths()
    p.paper.fuse_paths()

    assert_path_data(
        p, 1,
        'M2.0,3.0 L4.0,3.0 L-2.0,-3.0 L-4.0,-3.0 L2.0,3.0 z'
    )


def test_fuse_with_joint():
    p = Pen()
    p.stroke_mode(2)

    p.move_to((0, 0))
    p.turn_to(180)
    p.line_forward(5)
    p.turn_left(90)
    p.line_forward(5)

    p.break_stroke()

    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(5)

    assert_path_data(
        p, 0,
        [
            'M0,1 L0,-1 L-6,-1 L-6,5 L-4,5 L-4,1 L0,1 z',
            'M0,-1 L0,1 L5,1 L5,-1 L0,-1 z',
        ]
    )

    p.paper.join_paths()
    p.paper.fuse_paths()

    assert_path_data(
        p, 0,
        'M-6,5 L-4,5 L-4,1 L5,1 L5,-1 L-6,-1 L-6,5 z'
    )


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
        p.stroke_mode(2)
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
