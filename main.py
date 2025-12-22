import pygame
import random
from entity import Entity, Player, Goblin
from utils import *
from direction import Direction


pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

class Entities:
    def __init__(self, players, goblins):
        self.players = players
        self.goblins = goblins

class Game:
    def __init__(self, screen, entities):
        self.screen = screen
        self.entities = entities
        assets = {"goblin" : GOBLIN_ASSET, "village_map" : VILLAGE_MAP_ASSET, "player" : PLAYER_ASSET}

        self.assets = {k: pygame.image.load(v) for k, v in assets.items()}


    def run(self):
        running = True
        while running:
            self.event()
            self.draw()
            self.update()
        pygame.quit()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_background()
        self.draw_entities()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    def update(self):
        self.move()
        pygame.display.flip()

    def draw_image(self, img, x, y):
        self.screen.blit(self.assets[img], (x * PIXEL_SIZE, y * PIXEL_SIZE))

    def draw_background(self):
        self.draw_image("village_map", 0, 0)

    def draw_entities(self):
        for player in self.entities.players:
            self.draw_image("player", player.x, player.y)

        for goblin in self.entities.goblins:
            self.draw_image("goblin", goblin.x, goblin.y)

    def move(self):
        for player in self.entities.players:
            dir = random.choice(list(Direction))

            player.move(dir)

        for goblin in self.entities.goblins:
            goblin.move(self.entities.players)

            target = next((p for p in self.entities.players if p.x == goblin.x and p.y == goblin.y), None)

            if target is not None:
                self.entities.players.remove(target)


players = set([Player(i, i) for i in range(6)])
goblins = set([Goblin(i, i) for i in range(26, 30)])

game = Game(screen, Entities(players, goblins))

game.run()
