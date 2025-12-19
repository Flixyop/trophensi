import pygame
from entity import Entity, Player, Goblin, move
from consts import PIXEL_SIZE, BOARD_SIZE, SCREEN_SIZE


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


def print_entities(screen, assets):
    for entity in entities:
        print_screen(screen, assets[entity.img], entity.x, entity.y)


def play_the_game(entities: [Entity]):
    assets = load_asset()

    running = True

    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 1000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOVE_EVENT:
                move(entities)

        screen.fill((255, 255, 255))

        print_grass(screen, assets)
        print_entities(screen, assets)

        pygame.display.flip()

    pygame.quit()


entities = [Player(i, i) for i in range(25)] + [Goblin(i, i) for i in range(26, 30)]

play_the_game(entities)
