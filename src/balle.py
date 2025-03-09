import pygame as pg
import math

class Balle:
    def __init__(self, position, speed=1, gravity=0.5, friction=0.99):
        # init de la balle
        self.position = position # Position de la balle sous la forme [x, y]
        self.speed = speed
        self.gravity = gravity
        self.friction = friction
        self.velocity_x = 0 # Vitesse horizontale
        self.velocity_y = 0 # Vitesse verticale
        self.dragging = False # Indique si la balle est en train d'être déplacée
        self.offset_x = 0 # Decalage de la position de la souris
        self.offset_y = 0
        self.start_drag_pos = None # Position de la souris au début du drag
        self.shooting_mode = True  # Mode shooting activé par défaut
        self.flying = False  # Indique si la balle est en vol (après un tir)
        self.prev_mouse_pos = None
        
        # init du sprite de la balle
        self.balle_image = pg.transform.scale(pg.image.load("assets/basketball.png"), (50, 50))
        self.rect = self.balle_image.get_rect(topleft=self.position)
        
        # Nouveau: attribut pour le tir au curseur
        self.console_shot_requested = False

    def update_position(self, window_width, window_height):
        # Si la balle est attachée au joueur, on ne met pas à jour sa position
        if self.shooting_mode and not self.dragging and not self.flying:
            return

        # Si la balle est en vol, applique la physique
        if self.flying or not self.shooting_mode:
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
                self.position[1] = window_height - self.rect.height # Empêche la balle de passer à travers le sol
                self.velocity_y = -self.velocity_y * 0.7 # Rebondit sur le sol
                
                # Si la balle touche le sol et a presque arrêté de rebondir, retourne en mode shooting
                if abs(self.velocity_y) < 0.5 and abs(self.velocity_x) < 0.5: # Test si la balle est presque immobile
                    self.shooting_mode = True
                    self.flying = False

        self.rect.topleft = self.position

    def handle_event(self, event, joueur_position):
        # Ajout de la gestion de la touche pour le tir au curseur (par exemple 'C')
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_c and self.shooting_mode and not self.flying:
                self.request_console_shot()
                return
                
        # Gestion du clic sur la balle uniquement en mode shooting
        if event.type == pg.MOUSEBUTTONDOWN:
            # Si la balle est en mode shooting et proche du joueur, permet de la saisir
            if self.shooting_mode and self.rect.collidepoint(event.pos):
                self.dragging = True
                self.start_drag_pos = event.pos # Enregistre la position de la souris au début du drag
                self.prev_mouse_pos = event.pos 
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
        
        # Gestion du relâchement du clic
        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            end_drag_pos = event.pos
            # Tir de la balle
            self.shoot_from_drag(self.start_drag_pos, end_drag_pos)
            self.flying = True  # La balle est maintenant en vol
            self.shooting_mode = False  # Désactive le mode shooting pendant le vol
        
        # Gestion du mouvement de la souris pendant le drag, met a jour la position de la balle
        elif event.type == pg.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.position = [mouse_x + self.offset_x, mouse_y + self.offset_y]
            self.rect.topleft = self.position
            self.prev_mouse_pos = event.pos

    def request_console_shot(self):
        # Demande l'angle et la puissance dans la console
        try:
            print("\n--- Tir au curseur ---")
            angle = float(input("Entrez l'angle de tir (en degrés, 0-360): "))
            strength = float(input("Entrez la puissance de tir (1-100): "))
            
            # Limiter les valeurs à des plages raisonnables
            angle = max(0, min(360, angle))
            strength = max(1, min(100, strength)) / 2
            
            print(f"Tir avec angle={angle}° et puissance={strength*2}")
            self.shoot(angle, strength)
            self.flying = True
            self.shooting_mode = False
            
        except ValueError:
            print("Erreur: Veuillez entrer des nombres valides.")
        except Exception as e:
            print(f"Erreur: {e}")

    def shoot_from_drag(self, start_pos, end_pos):
        # Calcul de la direction et de la force du tir
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]
        distance = math.hypot(dx, dy) # Distance entre les deux points 
        angle = math.degrees(math.atan2(dy, dx)) # Angle entre les deux points ahan 2 donne l'angle et degrees le convertit en degrés
        strength = distance / 10  
        self.shoot(angle, strength)

    def shoot(self, angle, strength):
        # Lancement de la balle
        radian_angle = math.radians(angle)
        self.velocity_x = strength * math.cos(radian_angle)
        self.velocity_y = -strength * math.sin(radian_angle)

    def draw(self, fenetre):
        # Affichage de la balle
        fenetre.blit(self.balle_image, self.position)