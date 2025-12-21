import pygame
import random
from entity import Entity, Player, Goblin
from consts import PIXEL_SIZE, BOARD_SIZE, SCREEN_SIZE
from direction import Direction


def load_asset():
    assets = {
        "goblin": None,
        "grass": None,
        "player": None,
    }

    for key in assets:
        img = pygame.image.load(key + ".png")
        assets[key] = pygame.transform.scale(img, (PIXEL_SIZE, PIXEL_SIZE))

    assets["goblin"].set_colorkey((255, 255, 255))
    return assets


def print_screen(screen, img, x, y):
    screen.blit(img, (x * PIXEL_SIZE, y * PIXEL_SIZE))


def print_grass(screen, assets):
    for i in range(BOARD_SIZE[0]):
        for j in range(BOARD_SIZE[1]):
            print_screen(screen, assets["grass"], i, j)


def print_entities(screen, entities: set[Entity], assets):
    for entity in entities:
        print_screen(screen, assets[entity.img], entity.x, entity.y)


def play_the_game(players: set[Player], goblins: set[Goblin]):
    assets = load_asset()

    running = True

    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 100)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOVE_EVENT:
                move(players, goblins)

        screen.fill((255, 255, 255))

        print_grass(screen, assets)
        print_entities(screen, players | goblins, assets)

        pygame.display.flip()

    pygame.quit()


def choose_dir_from(left, right, down, up):
    if min(left, right) > min(down, up) :
        if left >= right :
            return Direction.Left
        else :
            return Direction.Right
    else :
        if down >= up:
            return Direction.Down
        else :
            return Direction.Up


def move_goblin(goblin, players):
    dir = random.choice(list(Direction))
    best_dist = 1000

    for p in players:
        left = (goblin.x - p.x) % BOARD_SIZE[0]
        right = BOARD_SIZE[0] - left

        down = (goblin.y - p.y) % BOARD_SIZE[1]
        up = BOARD_SIZE[1] - down

        dx = min(left, right)
        dy = min(up, down)

        dist = dx + dy
        if dist < best_dist and dist <= 10:
            best_dist = dist
            dir = choose_dir_from(left, right, down, up)

    return dir


def move(players: set[Player], goblins: set[Goblin]):
    for entity in players:
        dir = random.choice(list(Direction))

        entity.move(dir)

    for goblin in goblins:
        goblin.move(move_goblin(goblin, players))

        target = next((p for p in players if p.x == goblin.x and p.y == goblin.y), None)

        if target is not None:
            players.remove(target)


players = set([Player(i, i) for i in range(6)])
goblins = set([Goblin(i, i) for i in range(26, 30)])

play_the_game(players, goblins)
