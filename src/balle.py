import pygame as pg
import math

class Balle:
    def __init__(self, position, speed=1, gravity=0.5, friction=0.99):
        # init de la balle
        self.position = position
        self.speed = speed
        self.gravity = gravity
        self.friction = friction
        self.velocity_x = 0
        self.velocity_y = 0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.start_drag_pos = None
        self.shooting_mode = False
        self.prev_mouse_pos = None  # Ajoutez cette ligne
        
        # init du sprite de la balle
        self.balle_image = pg.transform.scale(pg.image.load("assets/basketball.png"), (50, 50))
        self.rect = self.balle_image.get_rect(topleft=self.position)

    def update_position(self, window_width, window_height):
        # Mise à jour de la position de la balle
        if self.dragging or self.shooting_mode:
            return

        # gravité (tire vers le bas)
        self.velocity_y += self.gravity
        self.position[0] -= self.velocity_x
        self.position[1] += self.velocity_y

        # friction (ralentis avec le temps)
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # collisions avec la fenetre
        if self.position[0] <= 0 or self.position[0] + self.rect.width >= window_width:
            self.velocity_x = -self.velocity_x * 0.7
        if self.position[1] + self.rect.height >= window_height:
            self.position[1] = window_height - self.rect.height
            self.velocity_y = -self.velocity_y * 0.7

        self.rect.topleft = self.position

    def handle_event(self, event, joueur_position):
        # Gestion de la souris (drag ou shoot mode)
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            self.start_drag_pos = event.pos
            self.prev_mouse_pos = event.pos  # Ajoutez cette ligne
            mouse_x, mouse_y = event.pos
            self.offset_x = self.rect.x - mouse_x
            self.offset_y = self.rect.y - mouse_y
            self.velocity_x = 0
            self.velocity_y = 0
        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            if self.shooting_mode:
                end_drag_pos = event.pos
                self.shoot_from_drag(self.start_drag_pos, end_drag_pos)
            else:
                # Calculer la vitesse et l'angle en fonction du mouvement de la souris
                dx = event.pos[0] - self.prev_mouse_pos[0]
                dy = event.pos[1] - self.prev_mouse_pos[1]
                distance = math.hypot(dx, dy)
                angle = math.degrees(math.atan2(dy, dx))
                strength = distance / 10  # Ajustez la sensibilité si nécessaire
                self.shoot(angle, strength)
        elif event.type == pg.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.position = [mouse_x + self.offset_x, mouse_y + self.offset_y]
            self.rect.topleft = self.position
            self.prev_mouse_pos = event.pos  # Ajoutez cette ligne

    def shoot_from_drag(self, start_pos, end_pos):
        # calcul shoot mode
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]
        distance = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx))
        strength = distance / 10  # possible de scale la sensibilité du mode
        self.shoot(angle, strength)

    def shoot(self, angle, strength):
        # lancement de la balle
        radian_angle = math.radians(angle)
        self.velocity_x = strength * math.cos(radian_angle)
        self.velocity_y = -strength * math.sin(radian_angle)

    def draw(self, fenetre):
        # affichage balle
        fenetre.blit(self.balle_image, self.position)
