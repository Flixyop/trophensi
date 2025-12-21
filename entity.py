from direction import Direction
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
        self.sprite_img = player_asset


class Goblin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite_img = gobelin_asset
