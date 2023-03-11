# from utils.brick import Motor
import math


def sgn(x):
    """Returns +1 if value is positive or 0.
    Returns -1 if value is strictly less the 0.
    """
    if x >= 0:
        return +1
    else:
        return -1


class Driver:
    _INHERIT_MOTOR_FUNCTIONS = ['set_power', 'set_dps', 'set_limits', 'set_position', 'set_position_relative',
                                'float_motor', 'get_position', 'get_power', 'get_speed', 'offset_encoder', 'reset_position']

    def __init__(self, motor_left, motor_right, axle_width, wheel_width):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.set_axle_width(axle_width)
        self.set_wheel_width(wheel_width)

        for name in self._INHERIT_MOTOR_FUNCTIONS:
            if hasattr(self.motor_left, name) and hasattr(self.motor_right, name):
                setattr(self, name, self._apply_both(name))

    def _turn_to_wheels(self, turn_radius, value):
        """Returns the (closest,farthest) wheel values, whether they are velocities or degrees.

        turn_radius is positive towards the left of the wheels, negative to the right.

        value > 0 : both positive outputs (forwards)
        value < 0 : both negative outputs (backwards)

        turn_radius >= 0 : positive value is clockwise
        turn_radius <  0 : negative value is anti-clockwise

        >>> d = Driver(None, None, 1, 1)
        >>> d._turn_to_wheels(0, 90)
        (-90.0, 90.0)
        >>> d._turn_to_wheels(0, -90)
        (90.0, -90.0)
        >>> d._turn_to_wheels(0.5, 90)
        (0.0, 180.0)
        >>> d._turn_to_wheels(1, 90)
        (90.0, 270.0)
        >>> d._turn_to_wheels(-0.5, 90)
        (180.0, -0.0)
        >>> d._turn_to_wheels(-1, 90)
        (270.0, 90.0)
        """
        d = sgn(turn_radius)
        v1 = d * value * (turn_radius - self.axle_radius) / self.wheel_radius
        v2 = d * value * (turn_radius + self.axle_radius) / self.wheel_radius
        return v1, v2

    def _apply_both(self, func_name):
        f1 = getattr(self.motor_left, func_name)
        f2 = getattr(self.motor_right, func_name)

        def inner(*args, **kwargs):
            return f1(*args, **kwargs), f2(*args, **kwargs)
        return inner

    def set_axle_width(self, value):
        self.axle_radius = value / 2

    def set_wheel_width(self, value):
        self.wheel_radius = value / 2

    def set_turn_power(self, turn_radius, power):
        p1, p2 = self._turn_to_wheels(turn_radius, power)
        self.motor_left.set_power(p1)
        self.motor_right.set_power(p2)

    def set_turn_dps(self, turn_radius, dps):
        d1, d2 = self._turn_to_wheels(turn_radius, dps)
        self.motor_left.set_dps(d1)
        self.motor_right.set_dps(d2)

    def set_turn_limits(self, turn_radius, power=None, dps=None):
        if power is not None:
            p1, p2 = self._turn_to_wheels(turn_radius, power)
        else:
            p1, p2 = None, None
        if dps is not None:
            d1, d2 = self._turn_to_wheels(turn_radius, dps)
        else:
            d1, d2 = None, None
        self.motor_left.set_limits(power=p1, dps=d1)
        self.motor_right.set_limits(power=p2, dps=d2)

    def set_turn_position_relative(self, turn_radius, turn_degrees):
        d1, d2 = self._turn_to_wheels(turn_radius, turn_degrees)
        self.motor_left.set_position_relative(d1)
        self.motor_right.set_position_relative(d2)

    def travel_position(self, distance):
        """Distance in the units of the wheel_width of this Driver"""
        self.motor_left.set_position(math.degrees(distance/self.wheel_radius))
        self.motor_right.set_position(math.degrees(distance/self.wheel_radius))

    def travel_position_relative(self, distance):
        """Distance in the units of the wheel_width of this Driver"""
        self.motor_left.set_position_relative(
            math.degrees(distance/self.wheel_radius))
        self.motor_right.set_position_relative(
            math.degrees(distance/self.wheel_radius))

    def travel_speed(self, speed):
        """Speed in the units of the wheel_width/seconds of this Driver"""
        self.motor_left.set_speed(math.degrees(speed/self.wheel_radius))
        self.motor_right.set_speed(math.degrees(speed/self.wheel_radius))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
