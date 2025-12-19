import random
from direction import Direction
from consts import BOARD_SIZE


class Entity:
    def __init__(self, x, y):
        self.img = "default"
        self.x = x
        self.y = y


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "player"


class Goblin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "goblin"


def maybe_eating(entity: Entity, x, y, entities: [Entity]):
    target = next((e for e in entities if e.x == x and e.y == y), None)

    if isinstance(entity, Goblin) and isinstance(target, Player):
        entities.remove(target)
        entity.x, entity.y = x, y

    elif target is None:
        entity.x, entity.y = x, y


def move(entities: [Entity]):
    random.shuffle(entities)
    for entity in entities:
        dir = random.choice(list(Direction)).value

        x = min(max(0, entity.x + dir[0]), BOARD_SIZE[0] - 1)
        y = min(max(0, entity.y + dir[1]), BOARD_SIZE[1] - 1)

        maybe_eating(entity, x, y, entities)
