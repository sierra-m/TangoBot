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
import re
import time
from util.commands import command, compile_commands

from config import *


@compile_commands
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
        
        self.controller.set_target(servoports.DRIVE, SERVO_CENTER)
        self.controller.set_target(servoports.STEER, SERVO_CENTER)

        # self.init_channels(17)

    def init_channels(self, limit):
        for channel in range(limit + 1):
            self.controller.set_target(channel, SERVO_CENTER)

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
    @command('DR', servoports.DRIVE)
    def drive(self, velocity: float):
        velocity = -velocity
        self.controller.set_target(servoports.STEER, SERVO_CENTER)
        self._set(servoports.DRIVE, velocity)

    # Direction makes more sense for steering
    # we might need to flip these
    def steer(self, direction: Direction, power: float):
        if direction == Direction.LEFT:
            target = 6000 + int(power * 1900)
        elif direction == Direction.RIGHT:
            target = 6000 - int(power * 1900)
        else:
            raise Exception('Direction Exception')

        self.controller.set_target(servoports.DRIVE, SERVO_CENTER)
        self.controller.set_target(servoports.STEER, target)
        
    @command('ST', servoports.STEER)
    def steer_direct(self, velocity: float):
        self.controller.set_target(servoports.DRIVE, SERVO_CENTER)
        self._set(servoports.STEER, velocity)

    # Normalized from -1 to 1
    @command('WT', servoports.WAIST)
    def turn_waist(self, position: float):
        self._set(servoports.WAIST, position)

    @command('HS', servoports.HEAD_SWIVEL)
    def swivel_head(self, position: float):
        self._set(servoports.HEAD_SWIVEL, position)

    @command('HT', servoports.HEAD_TILT)
    def tilt_head(self, position: float):
        self._set(servoports.HEAD_TILT, position)

    @command('RSH', servoports.RIGHT_SHOULDER)
    def turn_right_shoulder(self, position: float):
        self._set(servoports.RIGHT_SHOULDER, position)

    @command('RFP', servoports.RIGHT_FLAP)
    def turn_right_flap(self, position: float):
        self._set(servoports.RIGHT_FLAP, position)

    @command('REB', servoports.RIGHT_ELBOW)
    def bend_right_elbow(self, position: float):
        self._set(servoports.RIGHT_ELBOW, position)

    @command('RWR', servoports.RIGHT_WRIST)
    def bend_right_wrist(self, position: float):
        self._set(servoports.RIGHT_WRIST, position)

    @command('RTW', servoports.RIGHT_TWIST)
    def twist_right_wrist(self, position: float):
        self._set(servoports.RIGHT_TWIST, position)

    @command('RGR', servoports.RIGHT_GRIP)
    def grip_right(self, position: float):
        self._set(servoports.RIGHT_GRIP, position)

    @command('LSH', servoports.LEFT_SHOULDER)
    def turn_left_shoulder(self, position: float):
        self._set(servoports.LEFT_SHOULDER, position)

    @command('LFP', servoports.LEFT_FLAP)
    def turn_left_flap(self, position: float):
        self._set(servoports.LEFT_FLAP, position)

    @command('LEB', servoports.LEFT_ELBOW)
    def bend_left_elbow(self, position: float):
        self._set(servoports.LEFT_ELBOW, position)

    @command('LWR', servoports.LEFT_WRIST)
    def bend_left_wrist(self, position: float):
        self._set(servoports.LEFT_WRIST, position)

    @command('LTW', servoports.LEFT_TWIST)
    def twist_left_wrist(self, position: float):
        self._set(servoports.LEFT_TWIST, position)

    @command('LGR', servoports.LEFT_GRIP)
    def grip_left(self, position: float):
        self._set(servoports.LEFT_GRIP, position)

    def execute(self, instructions: str):
        """Executes a series of minimized commands

        Parameters
        ----------
        instructions : str
            string of packed commands in <command>[value](,speed/accel) format

        Commands are defined in decorators. These have range [-1000, 1000].
        "DLY" is delay in ms, range [0, large_number).
        `speed/accel` arg has range [0, 1000] and is optional

        >Example: Swivel and tilt head - "HS1000,500HT-1000"

        This is a prototype and should not be trusted completely lol
        """

        instructions = instructions.replace(' ', '')
        command_pattern = re.compile(r'([A-Z]+)(-?[0-9]+)(?:,)?([0-9]+)?')

        while instructions:
            match = re.match(command_pattern, instructions)

            if match:
                instructions = instructions[len(match.group(0)):]  # shift out match
                cmd, value = match.group(1), float(match.group(2)) / 1000
                speed = util.scale(float(match.group(3)), 0, 1000, SERVO_MIN, SERVO_MAX) if match.group(3) else None
                self._parse(cmd, value, speed)
            else:
                break

    def _parse(self, cmd: str, value: float, speed: float = None):
        """Parse a movement command - internal method

        Parameters
        ----------
            cmd : str
                the command string
            value : float
                the raw value
            speed : float
                optional speed parameter
        """

        if cmd == 'DLY':
            # Delay can also be normalized as `sleep` takes secs, not ms
            # Convenient coincidence.
            time.sleep(value)
        else:
            method = self.commands[cmd]
            if speed:
                self.controller.set_speed(method.__channel__, speed / 1000)
            method(self, value)

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
