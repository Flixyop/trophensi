from direction import Direction
from consts import BOARD_SIZE


class Entity:
    def __init__(self, x, y):
        self.img = "default"
        self.x = x
        self.y = y

    def move(self, dir: Direction):
        dir = dir.value
        self.x = min(max(0, self.x + dir[0]), BOARD_SIZE[0] - 1)
        self.y = min(max(0, self.y + dir[1]), BOARD_SIZE[1] - 1)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "player"


class Goblin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "goblin"
