from nose.tools import assert_raises

import math

from canoepaddle.heading import Heading, Angle


def test_init_error():
    # Make sure that we catch errors in algorithms early.
    # Don't allow None to be treated as an Angle.
    assert_raises(
        ValueError,
        lambda: Angle(None)
    )
    assert_raises(
        ValueError,
        lambda: Heading(None)
    )
    # Don't allow Headings and Angles to be conflated. They are conceptually different.
    assert_raises(
        TypeError,
        lambda: Angle(Heading(45)),
    )
    assert_raises(
        TypeError,
        lambda: Heading(Angle(45)),
    )


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


def test_angle_arithmetic():
    assert Angle(10) + Angle(20) == Angle(30)
    assert Angle(350) + Angle(20) == Angle(370)

    assert Angle(30) - Angle(10) == Angle(20)
    assert Angle(10) - Angle(30) == Angle(-20)
    assert Angle(10) - Angle(-10) == Angle(20)
    assert Angle(-10) - Angle(10) == Angle(-20)

    assert Angle(45) * 4 == Angle(180)
    assert Angle(180) / 4 == Angle(45)


def test_subtract_heading():
    assert Heading(30) - Heading(10) == Angle(20)
    assert Heading(10) - Heading(30) == Angle(340)
    assert Heading(10) - Heading(-10) == Angle(20)
    assert Heading(-10) - Heading(10) == Angle(340)


def test_radians():
    assert Heading(90).rad == math.pi / 2
    assert Angle(90).rad == math.pi / 2
    assert Heading.from_rad(math.pi / 2) == 90
    assert Angle.from_rad(math.pi / 2) == 90


def test_angle_to():
    assert Heading(0).angle_to(170) == Angle(170)
    assert Heading(170).angle_to(0) == Angle(-170)
    assert Heading(0).angle_to(190) == Angle(-170)
    assert Heading(190).angle_to(0) == Angle(170)
    assert Heading(45).angle_to(-45) == Angle(-90)
    assert Heading(-45).angle_to(45) == Angle(90)

    assert Heading(90).angle_to(-90) == Angle(180)
    assert Heading(-90).angle_to(90) == Angle(180)

    assert_raises(
        TypeError,
        lambda: Heading(0).angle_to(Angle(90))
    )


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
