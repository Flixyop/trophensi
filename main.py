from utils import GRASS_TILESET_ASSET
from utils import PIXEL_SIZE
import pygame
import random
import math
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


        self.mapping = {
            0: 6,
            1: 6,
            2: 6,
            3: 6,
            4: 6,
            5: 6,
            6: 6,
            7: 6,
            8: 6,
            9: 6,
            10: 6,
            11: 6,
            12: 6,
            13: 6,
            14: 6,
            15: 6
        }
        self.assets["paths"] = {}

        for i in range(16):
            row = i // 4
            col = i % 4
            rect = pygame.Rect(col * tile_w, row * tile_h, tile_w, tile_h)
            img = tileset.subsurface(rect)
            self.assets["paths"][i] = self.format_asset(img)
       
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
        for i in range(WORLD_WIDTH):
            for j in range(WORLD_HEIGHT):
                v_start_x = self.village_pos_x // PIXEL_SIZE
                v_end_x = v_start_x + (self.assets["village_map"].get_width() // PIXEL_SIZE)
                
                v_start_y = self.village_pos_y // PIXEL_SIZE
                v_end_y = v_start_y + (self.assets["village_map"].get_height() // PIXEL_SIZE)
                if i >= v_start_x and i < v_end_x and j >= v_start_y and j < v_end_y:
                    self.map_data[i][j] = -1
        
        self.generate_world()


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
        self.draw_map()
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

    def draw_map(self):
        start_col = max(0, self.camera.x // PIXEL_SIZE)
        end_col = min(WORLD_WIDTH, (self.camera.x + SCREEN_SIZE[0]) // PIXEL_SIZE + 1)
        
        start_row = max(0, self.camera.y // PIXEL_SIZE)
        end_row = min(WORLD_HEIGHT, (self.camera.y + SCREEN_SIZE[1]) // PIXEL_SIZE + 1)

        for x in range(start_col, end_col):
            for y in range(start_row, end_row):
                tile = self.map_data[x][y]
                if tile == 0:
                    self.draw_image("grass", x, y)
                elif tile == 1:
                    score = 0
                    if y > 0 and self.map_data[x][y-1] != 0: score += 1
                    if x < WORLD_WIDTH-1 and self.map_data[x+1][y] != 0: score += 2
                    if y < WORLD_HEIGHT-1 and self.map_data[x][y+1] != 0: score += 4
                    if x > 0 and self.map_data[x-1][y] != 0: score += 8
                    
                    pos_x = (x * PIXEL_SIZE) - self.camera.x
                    pos_y = (y * PIXEL_SIZE) - self.camera.y
                    tile_index = self.mapping[score]
                    self.screen.blit(self.assets["paths"][tile_index], (pos_x, pos_y))
        
        bg_x = self.village_pos_x - self.camera.x
        bg_y = self.village_pos_y - self.camera.y
        self.screen.blit(self.assets["village_map"], (bg_x, bg_y))



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
    
    def generate_world(self):
        self.structure_pos = []
        antilag = 0

        while len(self.structure_pos) < 10 and antilag < 10000:
            antilag += 1
            x = random.randint(0, WORLD_WIDTH - 1)
            y = random.randint(0, WORLD_HEIGHT - 1)

            if self.map_data[x][y] == 0:
                can_place = True
                for structure in self.structure_pos:
                    if math.hypot(structure[0] - x, structure[1] - y) < 15:
                        can_place = False
                        break
                
                if can_place:
                    self.structure_pos.append((x, y))
                    self.map_data[x][y] = 2

        v_center_x = (self.village_pos_x // PIXEL_SIZE) + (self.assets["village_map"].get_width() // PIXEL_SIZE // 2)
        v_center_y = (self.village_pos_y // PIXEL_SIZE) + (self.assets["village_map"].get_height() // PIXEL_SIZE // 2)
        
        for poi in self.structure_pos:
            self.create_path(poi, (v_center_x, v_center_y))

    def create_path(self, start_pos, end_pos):
        curr_x, curr_y = start_pos
        target_x, target_y = end_pos
        
        while curr_x != target_x or curr_y != target_y:
            if random.random() < 0.5:
                if curr_x != target_x:
                    curr_x += 1 if target_x > curr_x else -1
                elif curr_y != target_y:
                    curr_y += 1 if target_y > curr_y else -1
            else:
                if curr_y != target_y:
                    curr_y += 1 if target_y > curr_y else -1
                elif curr_x != target_x:
                    curr_x += 1 if target_x > curr_x else -1
                
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = curr_x + dx, curr_y + dy
                    if 0 <= nx < WORLD_WIDTH and 0 <= ny < WORLD_HEIGHT:
                        if self.map_data[nx][ny] == 0:
                            self.map_data[nx][ny] = 1

#players = set([Player(i, i) for i in range(3)])
#goblins = set([Goblin(i, i) for i in range(4, 10)])

players = set() 
goblins = set() 

game = Game(screen, Entities(players, goblins))

game.run()
