import math

from canoepaddle.heading import Heading, Angle


def test_eq():
    assert Heading(10) == Heading(10)
    assert not Heading(10) != Heading(10)
    assert Heading(10) != Heading(20)
    assert not Heading(10) == Heading(20)


def test_compare_heading():
    assert Heading(45) > Heading(0)
    assert Heading(45) >= Heading(0)
    assert Heading(0) < Heading(45)
    assert Heading(0) <= Heading(45)
    assert Heading(-135) > Heading(135)
    assert Heading(-135) >= Heading(135)
    assert Heading(135) < Heading(-135)
    assert Heading(135) <= Heading(-135)
    assert Heading(10) > Heading(-10)
    assert Heading(10) >= Heading(-10)
    assert Heading(-10) < Heading(10)
    assert Heading(-10) <= Heading(10)

    assert not Heading(42) > Heading(42)
    assert not Heading(42) < Heading(42)
    assert Heading(42) >= Heading(42)
    assert Heading(42) <= Heading(42)

    # Opposing headings count as greater than each other.
    assert Heading(180) > Heading(0)
    assert Heading(0) > Heading(180)
    assert Heading(90) > Heading(270)
    assert Heading(270) > Heading(90)


def test_add_angle():
    assert Angle(10) + Angle(20) == Angle(30)
    assert Angle(350) + Angle(20) == Angle(370)


def test_subtract_angle():
    assert Angle(30) - Angle(10) == Angle(20)
    assert Angle(10) - Angle(30) == Angle(-20)
    assert Angle(10) - Angle(-10) == Angle(20)
    assert Angle(-10) - Angle(10) == Angle(-20)


def test_subtract_heading():
    assert Heading(30) - Heading(10) == Angle(20)
    assert Heading(10) - Heading(30) == Angle(340)
    assert Heading(10) - Heading(-10) == Angle(20)
    assert Heading(-10) - Heading(10) == Angle(340)


def test_radians():
    assert Heading(90).rad == math.pi / 2


def test_between():
    assert not Heading(0).between(10, 30)
    assert not Heading(10).between(10, 30)
    assert Heading(20).between(10, 30)
    assert not Heading(30).between(10, 30)
    assert not Heading(40).between(10, 30)

    assert not Heading(-20).between(-10, 10)
    assert not Heading(-10).between(-10, 10)
    assert Heading(0).between(-10, 10)
    assert not Heading(10).between(-10, 10)
    assert not Heading(20).between(-10, 10)


def test_neg():
    assert -Angle(30) == Angle(-30)


def test_abs():
    assert abs(Angle(-30)) == Angle(30)


def test_mod():
    assert Angle(450) % 360 == Angle(90)
