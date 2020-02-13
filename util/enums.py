from enum import Enum


# Based on vector normal to bot front
class Direction(Enum):
    FORWARD = 0
    BACKWARD = 1
    LEFT = 2
    RIGHT = 3
    UP = 4
    DOWN = 5
    CLOCKWISE = 6
    COUNTER_CLOCKWISE = 7
    OPEN = 8
    CLOSED = 9
