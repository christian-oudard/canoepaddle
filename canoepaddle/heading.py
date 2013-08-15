"""
There are two classes here, which are important not to confuse with each other.

A Heading is a compass direction, represented in degrees in the range [0, 360).

An Angle is a difference between headings. This is not bounded into a circular
range, e.g. +720 would be two full circles to the left.
"""

import math


class HeadingBase:

    @property
    def rad(self):
        return math.radians(self.theta)

    def __lt__(self, other):
        return not self >= other

    def __ge__(self, other):
        return self > other or self == other


class Angle(HeadingBase):

    def __init__(self, theta):
        if theta is None:
            raise ValueError('None is not a valid Angle')
        if isinstance(theta, Heading):
            raise ValueError('Angle required, not Heading')
        if isinstance(theta, Angle):
            theta = theta.theta
        self.theta = theta

    def __str__(self):
        return str(self.theta)

    def __repr__(self):
        return 'Angle({})'.format(self.theta)

    def __eq__(self, other):
        other = Angle(other)
        return self.theta == other.theta

    def __gt__(self, other):
        other = Angle(other)
        return self.theta > other.theta

    def __add__(self, other):
        other = Angle(other)
        return Angle(self.theta + other.theta)

    def __sub__(self, other):
        other = Angle(other)
        return Angle(self.theta - other.theta)

    def __neg__(self):
        return Angle(-self.theta)

    def __abs__(self):
        return Angle(abs(self.theta))

    def __mod__(self, other):
        return Angle(self.theta % other)


class Heading(HeadingBase):

    def __init__(self, theta):
        if theta is None:
            raise ValueError('None is not a valid Heading')
        if isinstance(theta, Angle):
            raise ValueError('Heading required, not Angle')
        if isinstance(theta, Heading):
            theta = theta.theta
        self.theta = theta % 360

    def __str__(self):
        return str(self.theta)

    def __repr__(self):
        return 'Heading({})'.format(self.theta)

    def __eq__(self, other):
        other = Heading(other)
        return self.theta == other.theta

    def __gt__(self, other):
        if self == other:
            return False
        diff = (self - other).theta
        return 0 < diff <= 180

    def __add__(self, other):
        other = Angle(other)
        return Heading(self.theta + other.theta)

    def __sub__(self, other):
        if isinstance(other, Heading):
            a = self.theta
            b = other.theta
            if a < b:
                a += 360
            return Angle(a - b)
        else:
            other = Angle(other)
            return Heading(self.theta - other.theta)

    def between(self, lo, hi):
        lo = Heading(lo).theta
        mid = self.theta
        hi = Heading(hi).theta
        if lo == hi or mid == lo or mid == hi:
            return False
        if mid < lo:
            mid += 360
            hi += 360
        if hi < mid:
            hi += 360
        return hi - lo < 360

    def flipped_x(self):
        return Heading(180 - self.theta)

    def flipped_y(self):
        return Heading(-self.theta)
