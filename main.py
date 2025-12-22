import pygame
import random
from entity import Entity, Player, Goblin
from utils import *
from direction import Direction


pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

entities = []


class Game:
    def __init__(self, screen):
        self.screen = screen

    def run(self):
        running = True
        while running:
            self.MOVE_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(self.MOVE_EVENT, 100)

            self.event()
            self.draw()
            self.update()
        pygame.quit()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_background()
        self.draw_entities(entities)

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == self.MOVE_EVENT:
                move(players, goblins)

    def update(self):
        pygame.display.flip()

    def draw_image(self, img, x, y):
        self.screen.blit(img, (x * PIXEL_SIZE, y * PIXEL_SIZE))

    def draw_background(self):
        village_map = pygame.image.load(village_map_asset)
        self.draw_image(village_map, (0, 0))

    def draw_entities(self, entities):
        for entity in entities:
            self.draw_image(entity.x, entity.y)


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

game = Game(screen)

game.run()
