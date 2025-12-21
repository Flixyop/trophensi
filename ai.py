import random
import math
from entity import Player, Goblin
from direction import Direction

ALPHA = 0.1


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)


class Model:
    def __init__(self):
        self.weights = [0, 0]
        self.biais = 0

    def forward(self, inputs):
        self.last_input = inputs
        self.last_z = sum([w * x for w, x in zip(self.weights, inputs)]) + self.biais

        self.last = sigmoid(self.last_z)
        return self.last

    def backward(self, target):
        error = self.last - target

        dz = error * sigmoid_derivative(self.last_z)

        self.weights = [
            w - ALPHA * dz * las for w, las in zip(self.weights, self.last_input)
        ]
        self.biais -= ALPHA * dz


m = Model()

for _ in range(1000000):
    for i in range(2):
        for j in range(2):
            m.forward([i, j])
            m.backward((i + j) % 2)

print(m.forward([0, 0]))
print(m.forward([0, 1]))
print(m.forward([1, 0]))
print(m.forward([1, 1]))


def new_game():
    players = [Player(i, i) for i in range(25)]
    goblins = [Goblin(i, i) for i in range(26, 30)]

    print(len(players))
    for i in range(10000000):
        for entity in players:
            dir = random.choice(list(Direction))

            entity.move(dir)

        for goblin in goblins:
            dir = random.choice(list(Direction))
            goblin.move(dir)

            target = next(
                (p for p in players if p.x == goblin.x and p.y == goblin.y), None
            )

            if target is not None:
                players.remove(target)

    print(len(players))
