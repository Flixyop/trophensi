from direction import Direction
import random
from utils import *


class Entity:
    def __init__(self, x, y):
        self.img = "default"
        self.x = x
        self.y = y

    def move(self, dir: Direction):
        dir = dir.value
        self.x = (self.x + dir[0]) % BOARD_SIZE[0]
        self.y = (self.y + dir[1]) % BOARD_SIZE[1]


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)


class Goblin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

    def move(self, players):
        dir = random.choice(list(Direction))
        best_dist = 1000

        for p in players:
            left = (self.x - p.x) % BOARD_SIZE[0]
            right = BOARD_SIZE[0] - left

            down = (self.y - p.y) % BOARD_SIZE[1]
            up = BOARD_SIZE[1] - down

            dx = min(left, right)
            dy = min(up, down)

            dist = dx + dy
            if dist < best_dist and dist <= 10:
                best_dist = dist
                dir = choose_dir_from(left, right, down, up)

        return dir


def choose_dir_from(left, right, down, up):
    if min(left, right) > min(down, up):
        if left >= right:
            return Direction.Left
        else:
            return Direction.Right
    else:
        if down >= up:
            return Direction.Down
        else:
            return Direction.Up
