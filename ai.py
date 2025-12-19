from entity import Player, Goblin, move

entities = [Player(i, i) for i in range(25)] + [Goblin(i, i) for i in range(26, 30)]


def training(entities):
    print(len(entities))
    for i in range(1000):
        move(entities)
    print(len(entities))


training(entities)
