from enum import Enum


class Direction(Enum):
    Up = (0, -1)
    Down = (0, 1)
    Left = (1, 0)
    Right = (-1, 0)
