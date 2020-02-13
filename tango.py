"""
MIT License

Copyright (c) 2020 Sierra MacLeod and Conner Cross

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import maestro
from util.enums import Direction
from util import util, servoports

from config import *


class TangoBot:
    def __init__(self):
        self.controller = maestro.Controller()

        # Motor accel is servo speed as motor speed is servo target
        self.controller.set_speed(servoports.DRIVE, MOTOR_ACCEL)
        self.controller.set_speed(servoports.STEER, STEER_ACCEL)

        self.controller.set_accel(servoports.HEAD_SWIVEL, HEAD_ACCEL)
        self.controller.set_accel(servoports.HEAD_TILT, HEAD_ACCEL)
        self.controller.set_accel(servoports.WAIST, WAIST_ACCEL)

        self.controller.set_accel(servoports.RIGHT_SHOULDER, ARM_ACCEL)
        self.controller.set_accel(servoports.RIGHT_FLAP, ARM_ACCEL)
        self.controller.set_accel(servoports.RIGHT_ELBOW, ARM_ACCEL)
        self.controller.set_accel(servoports.RIGHT_WRIST, ARM_ACCEL)
        self.controller.set_accel(servoports.RIGHT_TWIST, ARM_ACCEL)
        self.controller.set_accel(servoports.RIGHT_GRIP, ARM_ACCEL)

    def __del__(self):
        self.controller.close()

    def _set(self, channel, position):
        position = self.bind_normalized(position)
        target = self.get_target(position)
        self.controller.set_target(channel, target)

    # Normalized input power
    def drive_direction(self, direction: Direction, power: float):
        if direction == Direction.FORWARD:
            target = 6000 + power * 3000
        elif direction == Direction.BACKWARD:
            target = 6000 - power * 3000
        else:
            raise Exception('Direction Exception')

        self.controller.set_target(servoports.DRIVE, target)

    # Normalized from -1 to 1
    # Let's be real this is more useful than directions
    def drive(self, velocity: float):
        self._set(servoports.DRIVE, velocity)

    # Direction makes more sense for steering
    # we might need to flip these
    def steer(self, direction: Direction, power: float):
        if direction == Direction.LEFT:
            target = 6000 + int(power * 3000)
        elif direction == Direction.RIGHT:
            target = 6000 - int(power * 3000)
        else:
            raise Exception('Direction Exception')

        self.controller.set_target(servoports.STEER, target)

    # Normalized from -1 to 1
    def turn_waist(self, position: float):
        self._set(servoports.WAIST, position)

    def swivel_head(self, position: float):
        self._set(servoports.HEAD_SWIVEL, position)

    def tilt_head(self, position: float):
        self._set(servoports.HEAD_TILT, position)

    def turn_right_shoulder(self, position: float):
        self._set(servoports.RIGHT_SHOULDER, position)

    def turn_right_flap(self, position: float):
        self._set(servoports.RIGHT_FLAP, position)

    def bend_right_elbow(self, position: float):
        self._set(servoports.RIGHT_ELBOW, position)

    def bend_right_wrist(self, position: float):
        self._set(servoports.RIGHT_WRIST, position)

    def twist_right_wrist(self, position: float):
        self._set(servoports.RIGHT_TWIST, position)

    def grip_right(self, position: float):
        self._set(servoports.RIGHT_GRIP, position)

    def turn_left_shoulder(self, position: float):
        self._set(servoports.LEFT_SHOULDER, position)

    def turn_left_flap(self, position: float):
        self._set(servoports.LEFT_FLAP, position)

    def bend_left_elbow(self, position: float):
        self._set(servoports.LEFT_ELBOW, position)

    def bend_left_wrist(self, position: float):
        self._set(servoports.LEFT_WRIST, position)

    def twist_left_wrist(self, position: float):
        self._set(servoports.LEFT_TWIST, position)

    def grip_left(self, position: float):
        self._set(servoports.LEFT_GRIP, position)

    @staticmethod
    def get_target(position: float):
        return int(util.scale(position, -1, 1, SERVO_MIN, SERVO_MAX))

    @staticmethod
    def bind_normalized(position: float):
        if position < -1:
            position = -1
        elif position > 1:
            position = 1

        return position
