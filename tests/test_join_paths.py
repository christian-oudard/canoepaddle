from .util import assert_path_data, sqrt2

from canoepaddle import Pen


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
    p.stroke_mode(2.0)

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


def test_join_paths_turn_back_no_joint():
    p = Pen()
    p.stroke_mode(1.0)
    p.move_to((0, 0))
    p.turn_to(0)
    p.line_forward(10)
    p.turn_right(180)
    p.break_stroke()
    p.line_forward(5)
    p.paper.join_paths()

    line1, line2 = p.last_path().segments
    assert line1.end_joint_illegal
    assert line2.start_joint_illegal

    assert_path_data(
        p, 1,
        (
            'M0.0,-0.5 L0.0,0.5 L10.0,0.5 L10.0,-0.5 '
            'L5.0,-0.5 L5.0,0.5 L10.0,0.5 L10.0,-0.5 L0.0,-0.5 z'
        )
    )
