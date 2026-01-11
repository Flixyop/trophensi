import pygame
from utils import PIXEL_SIZE, SCREEN_SIZE, WORLD_WIDTH, WORLD_HEIGHT


class Camera():
    def __init__(self):
        self.x = (WORLD_WIDTH * PIXEL_SIZE) // 2 - (SCREEN_SIZE[0] // 2) 
        self.y = (WORLD_HEIGHT * PIXEL_SIZE) // 2 - (SCREEN_SIZE[1] // 2) 
        self.size = 100
        self.pos = (self.x, self.y)
        self.speed = 5   
        self.marge = 100
        self.marge_corner = 150

    def update(self):
        if not pygame.mouse.get_focused():
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_w, screen_h = SCREEN_SIZE[0], SCREEN_SIZE[1]
        move_left = False
        move_right = False
        move_up = False
        move_down = False

        in_col_left = mouse_x < self.marge_corner
        in_col_right = mouse_x > screen_w - self.marge_corner
        in_row_top = mouse_y < self.marge_corner
        in_row_bottom = mouse_y > screen_h - self.marge_corner

        if in_col_left and in_row_top:
            move_left = True
            move_up = True

        elif in_col_right and in_row_top:
            move_right = True
            move_up = True

        elif in_col_left and in_row_bottom:
            move_left = True
            move_down = True

        elif in_col_right and in_row_bottom:
            move_right = True
            move_down = True
        

        else:
            if mouse_x < self.marge: move_left = True
            if mouse_x > screen_w - self.marge: move_right = True
            if mouse_y < self.marge: move_up = True
            if mouse_y > screen_h - self.marge: move_down = True

        if move_left: self.x -= self.speed
        if move_right: self.x += self.speed
        if move_up: self.y -= self.speed
        if move_down: self.y += self.speed
