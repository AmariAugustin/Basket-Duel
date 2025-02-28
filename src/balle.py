import pygame as pg

class Balle:
    def __init__(self, position, speed=1, gravity=0.5):
        self.position = position
        self.speed = speed
        self.gravity = gravity
        self.velocity_y = 0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.balle_image = pg.transform.scale(pg.image.load("assets/basketball.png"), (50, 50))
        self.rect = self.balle_image.get_rect(topleft=self.position)

    def update_position(self, window_width, window_height):
        if self.dragging:
            return

        self.velocity_y += self.gravity
        self.position[1] += self.velocity_y

        if self.position[0] <= 0 or self.position[0] + self.rect.width >= window_width:
            self.speed = -self.speed
        if self.position[1] + self.rect.height >= window_height:
            self.position[1] = window_height - self.rect.height
            self.velocity_y = -self.velocity_y * 0.7  

        self.rect.topleft = self.position

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            mouse_x, mouse_y = event.pos
            self.offset_x = self.rect.x - mouse_x
            self.offset_y = self.rect.y - mouse_y
            self.velocity_y = 0  
        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
        elif event.type == pg.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.position = [mouse_x + self.offset_x, mouse_y + self.offset_y]
            self.rect.topleft = self.position

    def draw(self, fenetre):
        fenetre.blit(self.balle_image, self.position)