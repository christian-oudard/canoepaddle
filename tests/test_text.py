from canoepaddle import Pen, Paper


def test_text():
    p = Pen()
    p.move_to((0, 0))
    p.text('abcd', 1, 'sans-serif')
    svg_data = p.paper.format_svg(0)
    assert (
        '<text x="0" y="0" font-family="sans-serif" font-size="1" '
        'fill="#000000">abcd</text>'
    ) in svg_data


def test_text_centered():
    p = Pen()
    p.move_to((0, 0))
    p.text('abcd', 1, 'sans-serif', centered=True)
    svg_data = p.paper.format_svg(0)
    assert (
        '<text x="0" y="0" font-family="sans-serif" font-size="1" '
        'fill="#000000" text-anchor="middle">abcd</text>'
    ) in svg_data


def test_text_merge():
    p = Pen()
    p.move_to((0, 0))
    p.text('abcd', 1)
    paper1 = p.paper
    assert '<text' in paper1.format_svg(0)

    paper2 = Paper()
    paper2.merge(paper1)
    assert '<text' in paper2.format_svg(0)

    paper3 = Paper()
    paper3.merge_under(paper1)
    assert '<text' in paper3.format_svg(0)


def test_text_translate():
    p = Pen()
    p.move_to((0, 0))
    p.text('abcd', 1)
    paper = p.paper

    paper.translate((2, 3))
    svg_data = paper.format_svg(0)
    assert (
        '<text x="2" y="-3" font-family="sans-serif" font-size="1" '
        'fill="#000000">abcd</text>'
    ) in svg_data
