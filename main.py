from utils import GRASS_TILESET_ASSET
from utils import PIXEL_SIZE
import pygame
import random
from entity import Entity, Player, Goblin
from utils import *
from direction import Direction
from camera import Camera


pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)


class Entities:
    def __init__(self, players, goblins):
        self.players = players
        self.goblins = goblins


class Game:
    def __init__(self, screen, entities):
        self.screen = screen
        self.entities = entities

        self.camera = Camera()

        raw_assets = {
            "goblin": pygame.image.load(GOBLIN_ASSET),
            "player": pygame.image.load(PLAYER_ASSET),
            "village": pygame.image.load(VILLAGE_MAP_ASSET), 
            "tileset": pygame.image.load(GRASS_TILESET_ASSET),
        }
        
        self.assets = {}
 
        self.assets["player"]  = self.format_asset(raw_assets["player"])
        self.assets["goblin"]  = self.format_asset(raw_assets["goblin"])
        self.assets["village_map"] = self.format_asset(raw_assets["village"])

        tileset = raw_assets["tileset"]
        ts_w, ts_h = tileset.get_size()
        tile_w = ts_w // 4 
        tile_h = ts_h // 4 
        

        grass_rect = pygame.Rect(0 * tile_w, 3 * tile_h, tile_w, tile_h)
        grass_img_raw = tileset.subsurface(grass_rect)
        

        self.assets["grass"] = self.format_asset(grass_img_raw)
       
        village_size_x = self.assets["village_map"].get_width()
        village_size_y = self.assets["village_map"].get_height()

        world_center_x = (WORLD_WIDTH * PIXEL_SIZE) // 2
        world_center_y = (WORLD_HEIGHT * PIXEL_SIZE) // 2


        self.village_pos_x = world_center_x - (village_size_x // 2)
        self.village_pos_y = world_center_y - (village_size_y // 2)
        self.clock = pygame.time.Clock()
        self.running = False
        self.MOVE_EVENT = pygame.USEREVENT + 1

        # Partie Zone Selection

        self.selection_start_point = (0, 0)
        self.is_user_selecting = False

        # Partie Zone map

        self.map_data = [[0 for y in range(WORLD_HEIGHT)] for x in range(WORLD_WIDTH)]

    def run(self):
        self.running = True
        pygame.time.set_timer(self.MOVE_EVENT, 1000)

        while self.running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_background()
        self.draw_entities()
        self.draw_screen_selection()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == self.MOVE_EVENT:
                self.move()
            elif event.type == pygame.VIDEORESIZE:
                global SCREEN_SIZE 
                SCREEN_SIZE[0] = event.w
                SCREEN_SIZE[1] = event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.selection_start_point = pygame.mouse.get_pos()
                    self.is_user_selecting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.selection_start_point = (0, 0)
                    self.is_user_selecting = False
        

    def update(self):

        self.camera.update()
        pygame.display.flip()


    def draw_image(self, img, x, y):
        pos_screen_x = (x * PIXEL_SIZE) - self.camera.x
        pos_screen_y = (y * PIXEL_SIZE) - self.camera.y
        self.screen.blit(self.assets[img], (pos_screen_x, pos_screen_y))


    def draw_background(self):

        start_col = max(0, self.camera.x // PIXEL_SIZE)
        end_col = min(WORLD_WIDTH, (self.camera.x + SCREEN_SIZE[0]) // PIXEL_SIZE + 1)
        
        start_row = max(0, self.camera.y // PIXEL_SIZE)
        end_row = min(WORLD_HEIGHT, (self.camera.y + SCREEN_SIZE[1]) // PIXEL_SIZE + 1)

        for x in range(start_col, end_col):
            for y in range(start_row, end_row):
                self.draw_image("grass", x, y)


        bg_x = self.village_pos_x - self.camera.x
        bg_y = self.village_pos_y - self.camera.y
        self.screen.blit(self.assets["village_map"], (bg_x, bg_y))

    def draw_entities(self):
        for player in self.entities.players:
            self.draw_image("player", player.x, player.y)

        for goblin in self.entities.goblins:
            self.draw_image("goblin", goblin.x, goblin.y)

    def draw_screen_selection(self):
        if self.is_user_selecting:
            area = self.make_selection_area()
            area_element = area[0]
            top_left_corner = area[1]
            self.screen.blit(area_element, top_left_corner)



    def move(self):
        for player in self.entities.players:
            dir = random.choice(list(Direction))

            player.move(dir)

        for goblin in self.entities.goblins:
            goblin.move(self.entities.players)

            target = next(
                (
                    p
                    for p in self.entities.players
                    if p.x == goblin.x and p.y == goblin.y
                ),
                None,
            )

            if target is not None:
                self.entities.players.remove(target)

    def format_asset(self, image):
        width = image.get_width()
        height = image.get_height()
        new_size = (width * ZOOM_LEVEL, height * ZOOM_LEVEL)
        return pygame.transform.scale(image, new_size)
    
    def make_selection_area(self):
        weight = abs(self.selection_start_point[0] - pygame.mouse.get_pos()[0])
        height = abs(self.selection_start_point[1] - pygame.mouse.get_pos()[1])
        top_left_corner = (min(pygame.mouse.get_pos()[0], self.selection_start_point[0]), min(pygame.mouse.get_pos()[1], self.selection_start_point[1]))
        area_zone = pygame.Surface((weight, height), pygame.SRCALPHA)
        area_zone.fill((0, 120, 215, 100))
        return area_zone, top_left_corner

#players = set([Player(i, i) for i in range(3)])
#goblins = set([Goblin(i, i) for i in range(4, 10)])

players = set() 
goblins = set() 

game = Game(screen, Entities(players, goblins))

game.run()
