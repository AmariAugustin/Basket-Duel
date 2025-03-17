import pygame as pg
import math
from partie import Partie

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
        
        # Pour le tir au curseur
        self.console_shot_requested = False
        # État pour le sélecteur GUI de puissance/angle
        self.show_shot_selectors = False
        self.power_value = 50  # Valeur par défaut
        self.angle_value = 45  # Valeur par défaut

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
                # Empêche la balle de sortir de l'écran horizontalement
                if self.position[0] <= 0:
                    self.position[0] = 0
                elif self.position[0] + self.rect.width >= window_width:
                    self.position[0] = window_width - self.rect.width
                    
            if self.position[1] + self.rect.height >= window_height:
                self.position[1] = window_height - self.rect.height # Empêche la balle de passer à travers le sol
                self.velocity_y = -self.velocity_y * 0.7 # Rebondit sur le sol
                
                # Si la balle touche le sol et a presque arrêté de rebondir, retourne en mode shooting
                if abs(self.velocity_y) < 0.5 and abs(self.velocity_x) < 0.5: # Test si la balle est presque immobile
                    self.shooting_mode = True
                    self.flying = False

        self.rect.topleft = self.position

    def handle_event(self, event, joueur_position, Partie):
        # Gestion du mode sélecteur d'angle et de puissance
        if self.show_shot_selectors:
            if event.type == pg.MOUSEBUTTONDOWN:
                # Si l'utilisateur a cliqué, vérifier s'il a cliqué sur un sélecteur
                mouse_pos = pg.mouse.get_pos()
                # Coordonnées des sélecteurs définies dans draw_shot_selectors
                power_selector = pg.Rect(50, 100, 20, 200)
                angle_selector = pg.Rect(100, 50, 200, 20)
                
                if power_selector.collidepoint(mouse_pos):
                    # Calculer la puissance en fonction de la position de la souris
                    y_pos = mouse_pos[1]
                    self.power_value = 100 - ((y_pos - 100) * 100 / 200)
                    self.power_value = max(1, min(100, self.power_value))
                    
                elif angle_selector.collidepoint(mouse_pos):
                    # Calculer l'angle en fonction de la position de la souris
                    x_pos = mouse_pos[0]
                    self.angle_value = ((x_pos - 100) * 180 / 200)
                    self.angle_value = max(0, min(180, self.angle_value))
                    
                # Si l'utilisateur a cliqué ailleurs, effectuer le tir
                else:
                    self.show_shot_selectors = False
                    strength = self.power_value / 2  # Ajuster la puissance
                    self.shoot(self.angle_value, strength)
                    self.flying = True
                    self.shooting_mode = False
                    Partie.switch_turn()  # Passe au joueur suivant

                    
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                # Annuler le mode sélecteur avec la touche Échap
                self.show_shot_selectors = False
                
            return  # Ne pas traiter d'autres événements en mode sélecteur
            
        # Ajout de la gestion de la touche pour le tir au curseur
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_c and self.shooting_mode and not self.flying:
                # Activer le mode sélecteur plutôt que de demander des entrées console
                self.show_shot_selectors = True
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
        # Cette méthode est maintenant obsolète, remplacée par l'utilisation du mode sélecteur
        # Mais on la conserve pour compatibilité
        self.show_shot_selectors = True

    def shoot_from_drag(self, start_pos, end_pos):
        # Calcul de la direction et de la force du tir
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]
        distance = math.hypot(dx, dy) # Distance entre les deux points 
        angle = math.degrees(math.atan2(dy, dx)) # Angle entre les deux points atan2 donne l'angle et degrees le convertit en degrés
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
        
        # Affichage des sélecteurs de tir si nécessaire
        if self.show_shot_selectors:
            self.draw_shot_selectors(fenetre)
            
    def draw_shot_selectors(self, fenetre):
        # Dessiner les sélecteurs de puissance et d'angle
        
        # Sélecteur de puissance (vertical)
        power_selector = pg.Rect(50, 100, 20, 200)
        pg.draw.rect(fenetre, (200, 200, 200), power_selector)
        
        # Indicateur de puissance
        power_indicator_y = 100 + 200 - (self.power_value * 200 / 100)
        power_indicator = pg.Rect(45, power_indicator_y - 5, 30, 10)
        pg.draw.rect(fenetre, (255, 0, 0), power_indicator)
        
        # Sélecteur d'angle (horizontal)
        angle_selector = pg.Rect(100, 50, 200, 20)
        pg.draw.rect(fenetre, (200, 200, 200), angle_selector)
        
        # Indicateur d'angle
        angle_indicator_x = 100 + (self.angle_value * 200 / 180)
        angle_indicator = pg.Rect(angle_indicator_x - 5, 45, 10, 30)
        pg.draw.rect(fenetre, (0, 255, 0), angle_indicator)
        
        # Afficher les valeurs
        font = pg.font.SysFont(None, 24)
        power_text = font.render(f"Puissance: {int(self.power_value)}", True, (255, 255, 255))
        angle_text = font.render(f"Angle: {int(self.angle_value)}°", True, (255, 255, 255))
        fenetre.blit(power_text, (10, 310))
        fenetre.blit(angle_text, (10, 340))
        
        # Instructions
        instruction_text = font.render("Cliquez sur les curseurs pour ajuster, ailleurs pour tirer", True, (255, 255, 255))
        fenetre.blit(instruction_text, (10, 370))
        
        # Dessiner un indicateur de direction de tir basé sur l'angle et la puissance actuels
        start_x = self.position[0] + 25
        start_y = self.position[1] + 25
            
        # Convertir l'angle en radians pour les calculs
        radian_angle = math.radians(self.angle_value)
        
        # Calculer le point d'arrivée en fonction de l'angle et de la puissance
        indicator_length = self.power_value * 1.5
        end_x = start_x - indicator_length * math.cos(radian_angle)
        end_y = start_y - indicator_length * math.sin(radian_angle)
        
        # Dessiner la ligne d'indication
        pg.draw.line(fenetre, (255, 0, 0), (start_x, start_y), (end_x, end_y), 10)
        pg.draw.circle(fenetre, (255, 0, 0), (int(end_x), int(end_y)), 10)
        
        