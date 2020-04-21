from enum import Enum
from controller import Robot, Compass
import math
from itertools import repeat
import sys
import time
import json
from os import path


# Enums for direction
class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    RIGHT = 4
    LEFT = 5


# Enums for main loop movement state
class State(Enum):
    DECIDE = 0
    SEARCH = 1
    FINISH = 2


# Angles corresponding to directions
dir_angles = {
    Direction.NORTH: 1.57,
    Direction.EAST: -3.12,
    Direction.SOUTH: -1.57,
    Direction.WEST: 0
}


# Proximity sensor defs
PS_F_R = 0
PS_D_R = 1
PS_R = 2
PS_B_R = 3
PS_B_L = 4
PS_L = 5
PS_D_L = 6
PS_F_L = 7

# LED defs
LED_BODY = 8
LED_FRONT = 9

# Get the time step of the current world.
TIME_STEP = 64

# Variance of proximity output
PS_VARIANCE = 10

MAX_SPEED = 5
HALF_SPEED = MAX_SPEED / 2
FORWARD_SPEED = 0.8 * MAX_SPEED
CREEP_SPEED = 0.1 * MAX_SPEED
TRIM_INC = 0.007 * MAX_SPEED

# Sensor ranges
PS_FRONT_STOP = 110
PS_RIGHT_STOP = 60

PS_MIN = 77

PS_TRIM_MIN = 130
PS_TRIM_MAX = 150
PS_TRIM_TARGET = 150
PS_TRIM_RANGE = 60
PS_TRIM_INC = 0.025

COMPASS_TRIM_INC = 0.025

DIST_ALIGN = 1.5
DIST_ENTER = 3.5
DIST_REVERSE = 0.7
DIST_WALL_ALIGN = 0.3

LED_BLINK_TIME = 0.2
LOGGER_TIMEOUT = 2

TWO_PI = 2 * math.pi

# Samples to window for average
WINDOW_SIZE = 5


use_file = path.exists('data.json')

if not use_file:
    with open('data.json', 'w') as f:
        structure = {
            'run': 1,
            'best_path': []
        }
        json.dump(structure, f)

        run = 1
        last_best_path = []
else:
    with open('data.json', 'r') as f:
        data = json.load(f)
        run = data['run']
        last_best_path = data['best_path']


class PathLogger:
    def __init__(self, log=[]):
        self.log = log

        self.dir_to_char = {
            Direction.NORTH: 'N',
            Direction.EAST: 'E',
            Direction.SOUTH: 'S',
            Direction.WEST: 'W'
        }

        self.char_to_dir = {v: k for k, v in self.dir_to_char.items()}

        self.dir_contras = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST
        }

        self.timer_start = time.time()

    def load(self, data: str):
        self.log = [self.char_to_dir[x] for x in data]

    def add(self, direction: Direction):
        if self.log:
            if (time.time() - self.timer_start) < LOGGER_TIMEOUT:
                print('Rejected logging: timeout')
                return

            last = self.log[-1]
            print('Wants to log {}, last logged is {}'.format(direction, last))
            if self.dir_contras[last] == direction:
                self.log.pop()
                print('popped')
            else:
                self.log.append(direction)
                print('added')
            print(self.log)
            self.timer_start = time.time()
        else:
            self.log.append(direction)

    def chars(self):
        return [self.dir_to_char[x] for x in self.log]

    def __iter__(self):
        return iter(self.log)


class SuperRoomba:
    def __init__(self):
        print('Initializing robot...')

        # Create the Robot instance.
        self.robot = Robot()

        # distance sensors
        self.ps = []
        ps_names = [
            'ps0', 'ps1', 'ps2', 'ps3',
            'ps4', 'ps5', 'ps6', 'ps7'
        ]

        for i in range(8):
            self.ps.append(self.robot.getDistanceSensor(ps_names[i]))
            self.ps[i].enable(TIME_STEP)

        self.leds = []
        led_names = [
            'led0', 'led1', 'led2', 'led3', 'led4',
            'led5', 'led6', 'led7', 'led8', 'led9'
        ]

        for i in range(10):
            self.leds.append(self.robot.getLED(led_names[i]))

        self.compass = self.robot.getCompass('compass')
        self.compass.enable(TIME_STEP)

        self.leftMotor = self.robot.getMotor('left wheel motor')
        self.rightMotor = self.robot.getMotor('right wheel motor')
        self.left_encoder = self.robot.getPositionSensor('left wheel sensor')
        self.right_encoder = self.robot.getPositionSensor('right wheel sensor')
        self.left_encoder.enable(TIME_STEP)
        self.right_encoder.enable(TIME_STEP)
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)

        self.touch_sensor = self.robot.getTouchSensor('touch sensor')
        self.touch_sensor.enable(TIME_STEP)

        self.left_vel = None
        self.right_vel = None

        # Current absolute direction
        self.facing = None
        self.facing_angle = None
        self.turning = None

        # start values for encoder tracking
        self.left_pos_start = None
        self.right_pos_start = None

        # Led for search animation
        self.search_led = 0
        self.led_timer = 0

        self.initialize_sensors()

        # Current movement state
        self.state = None

        self.best_path = None
        self.path_logger = PathLogger()
        if use_file and run == 3:
            self.path_logger.load(last_best_path)
            self.best_path = iter(self.path_logger)

        # Load initial samples in each sensor window
        self.ps_windows = []
        for i in range(0, 8):
            self.ps_windows.append(list(repeat(self.ps[i].getValue(), WINDOW_SIZE)))

    def initialize_sensors(self):
        # Initialize sensors
        for i in range(3):
            if self.robot.step(TIME_STEP) == -1:
                break

            for x in range(8):
                self.ps[x].getValue()

            self.compass.getValues()

            self.left_encoder.getValue()
            self.right_encoder.getValue()

            self.touch_sensor.getValue()

    def write_motors(self):
        self.leftMotor.setVelocity(self.left_vel)
        self.rightMotor.setVelocity(self.right_vel)

    def stop_motors(self):
        self.left_vel = 0
        self.right_vel = 0
        self.write_motors()

    def full_forward(self):
        self.left_vel = FORWARD_SPEED
        self.right_vel = FORWARD_SPEED
        self.write_motors()

    def full_reverse(self):
        self.left_vel = -FORWARD_SPEED
        self.right_vel = -FORWARD_SPEED
        self.write_motors()

    @staticmethod
    def rot_dist(current, target):
        dist = abs(target - current)
        return min(dist, TWO_PI - dist)

    def in_range(self, value, target, variance, angle=False):
        if angle:
            return self.rot_dist(value, target) <= variance
        return target - variance <= value <= target + variance

    @staticmethod
    def get_turn_direction(current, target):
        target += math.pi
        current += math.pi
        right = (target - current) % TWO_PI
        left = (current - target) % TWO_PI
        if right < left:
            return Direction.RIGHT
        return Direction.LEFT

    def ps_refresh(self):
        for i in range(0, WINDOW_SIZE):
            if self.robot.step(TIME_STEP) == -1:
                break

            for x in range(8):
                window = self.ps_windows[x]
                window.insert(0, self.ps[x].getValue())
                window.pop()

    def get_compass(self):
        x, y, z = self.compass.getValues()
        return math.atan2(x, z)

    def capture_position(self):
        self.left_pos_start = self.left_encoder.getValue()
        self.right_pos_start = self.right_encoder.getValue()

    def move_distance_blocking(self, dist):
        self.capture_position()
        while self.robot.step(TIME_STEP) != -1:
            left_pos = self.left_encoder.getValue()
            right_pos = self.right_encoder.getValue()

            # print('Moving -> {}%'.format(int(abs(right_pos - self.right_pos_start) / dist * 100)))

            right_done = abs(right_pos - self.right_pos_start) > dist
            left_done = abs(left_pos - self.left_pos_start) > dist

            if right_done:
                self.right_vel = 0

            if left_done:
                self.left_vel = 0

            self.write_motors()

            if right_done and left_done:
                return True
        return False

    def turn_towards_blocking(self, target):
        if self.get_turn_direction(self.get_compass(), target) == Direction.RIGHT:
            self.left_vel = HALF_SPEED
            self.right_vel = -HALF_SPEED
            self.turning = Direction.RIGHT
        else:
            self.left_vel = -HALF_SPEED
            self.right_vel = HALF_SPEED
            self.turning = Direction.LEFT

        self.write_motors()

        start = self.get_compass()
        total_dist = self.rot_dist(start, target)

        while self.robot.step(TIME_STEP) != -1:
            angle = self.get_compass()

            # print('Turning -> {}%'.format(int(self.rot_dist(angle, target) / total_dist * 100)))

            if self.in_range(angle, target, 0.15, angle=True):
                self.left_vel = CREEP_SPEED if self.turning == Direction.RIGHT else -CREEP_SPEED
                self.right_vel = -CREEP_SPEED if self.turning == Direction.RIGHT else CREEP_SPEED
                self.write_motors()

            if self.in_range(angle, target, 0.02, angle=True):
                return True
        return False

    def intersection_align(self):
        self.full_forward()
        print('Aligning with intersection...')
        self.move_distance_blocking(DIST_ALIGN)
        print('Aligned.')
        self.ps_refresh()

    def enter_passage(self):
        self.full_forward()
        print('Entering passage...')
        self.move_distance_blocking(DIST_ENTER)
        print('Entered.')
        self.ps_refresh()

    def turn_around(self):
        print('Turning around')
        self.blink_reverse(LED_BLINK_TIME)

        # angle_mid = dir_angles[Direction((self.facing.value - 1) % 4)]
        # self.turn_towards_blocking(angle_mid)
        # self.full_forward()
        # self.move_distance_blocking(DIST_WALL_ALIGN)
        self.facing = Direction((self.facing.value - 2) % 4)
        self.turn_towards_blocking(dir_angles[self.facing])

    def async_delay(self, delay):
        time_start = time.time()
        while self.robot.step(TIME_STEP) != -1:
            if (time.time() - time_start) > delay:
                break

    def set_led_range(self, start, stop):
        for i in range(start, stop):
            self.leds[i].set(1)

    def clear_led_range(self, start, stop):
        for i in range(start, stop):
            self.leds[i].set(0)

    def blink_right(self, delay):
        self.set_led_range(1, 4)
        self.async_delay(delay)
        self.clear_led_range(1, 4)

    def blink_left(self, delay):
        self.set_led_range(5, 8)
        self.async_delay(delay)
        self.clear_led_range(5, 8)

    def blink_forward(self, delay):
        self.set_led_range(0, 2)
        self.leds[7].set(1)
        self.async_delay(delay)
        self.clear_led_range(0, 2)
        self.leds[7].set(0)

    def blink_reverse(self, delay):
        self.set_led_range(3, 6)
        self.async_delay(delay)
        self.clear_led_range(3, 6)

    def turn_right(self):
        print('Turning right')
        self.blink_right(LED_BLINK_TIME)
        self.facing = Direction((self.facing.value + 1) % 4)
        self.turn_towards_blocking(dir_angles[self.facing])

        self.enter_passage()

    def turn_left(self):
        print('Turning left')
        self.blink_left(LED_BLINK_TIME)
        self.facing = Direction((self.facing.value - 1) % 4)
        self.turn_towards_blocking(dir_angles[self.facing])

        self.enter_passage()

    def setup(self):
        # Turn for first decision
        self.facing = Direction.NORTH
        self.turn_towards_blocking(dir_angles[self.facing])

        self.led_timer = time.time()
        self.state = State.DECIDE

    def mainloop(self):
        while self.robot.step(TIME_STEP) != -1:

            # Window all the proximity sensors for moving averages
            ps_values = []
            for i in range(8):
                window = self.ps_windows[i]
                window.insert(0, self.ps[i].getValue())
                window.pop()
                ps_values.append(sum(window) / WINDOW_SIZE)

            # Pull front sensors un-windowed so no delay
            ps_front_left = self.ps[PS_F_L].getValue()
            ps_front_right = self.ps[PS_F_R].getValue()

            angle = self.get_compass()

            if self.state == State.DECIDE:
                self.stop_motors()
                # print(ps_values)

                # if (use_file and ps_values[PS_R] < PS_MIN) or (not use_file and ps_values[PS_L] < PS_MIN):
                #     # self.intersection_align()
                #     self.intersection_align()  # twice
                #     self.intersection_align()  # twice
                #
                #     if (use_file and ps_values[PS_L] < PS_MIN) or (not use_file and ps_values[PS_R] < PS_MIN):
                #         self.intersection_align()  # twice

                if use_file:

                    if run == 3:
                        next_dir = next(self.best_path)

                        if next_dir == self.facing:
                            print('Proceeding {}'.format(next_dir.name.title()))
                            self.enter_passage()
                        else:
                            print('Turning {}'.format(next_dir.name.title()))
                            self.facing = next_dir
                            self.turn_towards_blocking(dir_angles[self.facing])
                            self.enter_passage()
                    else:
                        # Give priority to left
                        if ps_values[PS_L] < PS_MIN:
                            self.turn_left()

                        else:
                            if ps_front_left < PS_FRONT_STOP and ps_front_right < PS_FRONT_STOP:
                                print('Going forward')
                                self.blink_forward(LED_BLINK_TIME)
                                self.enter_passage()
                            else:
                                if ps_values[PS_R] < PS_MIN:
                                    self.turn_right()
                                else:
                                    self.turn_around()
                        if run == 2:
                            self.path_logger.add(self.facing)

                else:
                    # Give priority to right
                    if ps_values[PS_R] < PS_MIN:
                        self.turn_right()

                    else:
                        # print('Not turning right because: {}'.format(ps_values[PS_R]))
                        # self.ps_refresh()
                        # print('After refreshing its {}'.format(ps_values[PS_R]))
                        if ps_front_left < PS_FRONT_STOP and ps_front_right < PS_FRONT_STOP:
                            print('Going forward')
                            self.blink_forward(LED_BLINK_TIME)
                            self.enter_passage()
                        else:
                            if ps_values[PS_L] < PS_MIN:
                                self.turn_left()
                            else:
                                self.turn_around()
                    if run == 2:
                        self.path_logger.add(self.facing)

                self.leds[LED_BODY].set(0)
                self.full_forward()
                self.state = State.SEARCH

            elif self.state == State.SEARCH:
                # print('L: {} R: {}'.format(self.ps[PS_F_L].getValue(), self.ps[PS_F_R].getValue()))

                if (time.time() - self.led_timer) > 0.1:
                    self.led_timer = time.time()
                    self.leds[self.search_led].set(0)
                    self.search_led = (self.search_led + 1) % 8
                    self.leds[self.search_led].set(1)

                if self.get_turn_direction(angle, dir_angles[self.facing]) == Direction.LEFT:
                    self.right_vel += 0.025
                    self.left_vel -= 0.025
                else:
                    self.left_vel += 0.025
                    self.right_vel -= 0.025

                self.write_motors()

                if self.touch_sensor.getValue():
                    self.leds[self.search_led].set(0)
                    self.state = State.FINISH

                front_hit = self.ps[PS_F_L].getValue() > PS_FRONT_STOP or self.ps[PS_F_R].getValue() > PS_FRONT_STOP

                if front_hit:
                    print('Encountered wall')
                    self.leds[LED_BODY].set(1)
                    self.stop_motors()
                    self.leds[self.search_led].set(0)
                    self.state = State.DECIDE
                    continue

                if use_file:
                    turn_found = ps_values[PS_L] < PS_MIN
                else:
                    turn_found = ps_values[PS_R] < PS_MIN

                # either_turn_found = ps_values[PS_L] < PS_MIN or ps_values[PS_R] < PS_MIN
                # both_turns_found = ps_values[PS_L] < PS_MIN and ps_values[PS_R] < PS_MIN

                # if use_file:
                #     soft_intersection = ps_values[PS_R] < PS_MIN
                # else:
                #     soft_intersection = ps_values[PS_L] < PS_MIN

                if turn_found:
                    print('Encountered turn')
                    self.leds[LED_BODY].set(1)

                    self.intersection_align()
                    self.leds[self.search_led].set(0)
                    self.state = State.DECIDE

                # if soft_intersection:
                #     self.path_logger.add(self.facing)

            elif self.state == State.FINISH:
                print('Finished.')
                print('Path log: {}'.format(self.path_logger.chars()))
                self.stop_motors()
                break

    def cleanup(self):
        with open('data.json', 'w') as f:
            data = {
                'run': run + 1,
                'best_path': self.path_logger.chars()
            }
            json.dump(data, f)

    def run(self):
        self.setup()
        self.mainloop()
        self.cleanup()


super_roomba = SuperRoomba()

super_roomba.run()

