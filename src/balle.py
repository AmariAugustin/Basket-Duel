import pygame as pg
import math
import serveur
import client
import time

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
        """
        Fonction pour mettre à jour la position de la balle en fonction de sa vitesse et de la gravité.
        Cette fonction est appelée à chaque frame pour mettre à jour la position de la balle.
        Elle gère également les collisions avec les bords de la fenêtre.

        Args:
            window_width (int): Largeur de la fenêtre.
            window_height (int): Hauteur de la fenêtre.
        """
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

    def handle_event(self, event, player_position, online_player=None, partie=None):
        """
        Gère les événements de la balle, y compris le tir, le drag et les interactions avec la souris.
        Ajoute également la gestion des événements pour le mode sélecteur d'angle et de puissance.
        
        Args:
            event (pygame.event.Event): L'événement à traiter.
            player_position (list): La position du joueur sous la forme [x, y].
            online_player (object, optional): L'objet de communication en ligne. Par défaut None.
            partie (object, optional): L'objet représentant la partie en cours. Par défaut None.
        """
        # Gestion du mode sélecteur d'angle et de puissance
        if self.shooting_mode and not self.flying:
            self.show_shot_selectors = True
            
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
                    
                    # Envoi des données de tir en mode online
                    if partie and partie.is_online:
                        if partie.is_server and partie.current_player == 0:
                            # Envoyer l'état complet du tir
                            shot_data = {
                                'angle': self.angle_value,
                                'strength': strength,
                                'position': self.position,
                                'velocity': [self.velocity_x, self.velocity_y]
                            }
                            online_player.send(str(shot_data))
                        elif partie.is_client and partie.current_player == 1:
                            # Envoyer l'état complet du tir
                            shot_data = {
                                'angle': self.angle_value,
                                'strength': strength,
                                'position': self.position,
                                'velocity': [self.velocity_x, self.velocity_y]
                            }
                            online_player.send(str(shot_data))
                    
                    self.flying = True
                    self.shooting_mode = False
                    
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                # Annuler le mode sélecteur avec la touche Échap
                self.show_shot_selectors = False
                
            return
            
        # Réception des données de tir en mode online
        if partie and partie.is_online:
            try:
                if partie.is_server and partie.current_player == 1:
                    # Le serveur reçoit les données du client
                    shot_data = eval(online_player.receive().decode())
                    self.angle_value = shot_data['angle']
                    self.shoot(self.angle_value, shot_data['strength'])
                    self.position = shot_data['position']
                    self.velocity_x, self.velocity_y = shot_data['velocity']
                    self.flying = True
                    self.shooting_mode = False
                elif partie.is_client and partie.current_player == 0:
                    # Le client reçoit les données du serveur
                    shot_data = eval(online_player.receive().decode())
                    self.angle_value = shot_data['angle']
                    self.shoot(self.angle_value, shot_data['strength'])
                    self.position = shot_data['position']
                    self.velocity_x, self.velocity_y = shot_data['velocity']
                    self.flying = True
                    self.shooting_mode = False
            except:
                pass  # Ignorer les erreurs de réception si pas de données disponibles
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_z and self.shooting_mode and not self.flying:
                c = client.Client()
                c.send("90")
                time.sleep(1)
                c.send("50")
                
        # Gestion du clic sur la balle uniquement en mode shooting
        if event.type == pg.MOUSEBUTTONDOWN and self.shooting_mode and not self.flying:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.start_drag_pos = event.pos
                self.offset_x = event.pos[0] - self.position[0]
                self.offset_y = event.pos[1] - self.position[1]
                self.shooting_mode = False
        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            self.shooting_mode = True
        elif event.type == pg.MOUSEMOTION and self.dragging:
            # Mise à jour de la position de la balle en fonction du mouvement de la souris
            new_x = event.pos[0] - self.offset_x
            new_y = event.pos[1] - self.offset_y
            # Limiter le mouvement à la position du joueur
            self.position = [new_x, new_y]
            self.rect.topleft = self.position

    def request_console_shot(self):
        # Cette méthode est maintenant obsolète, remplacée par l'utilisation du mode sélecteur
        # Mais on la conserve pour compatibilité
        self.show_shot_selectors = True

    def shoot_from_drag(self, start_pos, end_pos):
        """
        Fonction pour tirer la balle en fonction de la position de départ et d'arrivée du drag.
        Cette fonction calcule la direction et la force du tir en fonction de la distance entre les deux points.
        
        Args:
            start_pos (tuple): La position de départ du drag sous la forme (x, y).
            end_pos (tuple): La position d'arrivée du drag sous la forme (x, y).
        """
        # Calcul de la direction et de la force du tir
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]
        distance = math.hypot(dx, dy) # Distance entre les deux points 
        angle = math.degrees(math.atan2(dy, dx)) # Angle entre les deux points atan2 donne l'angle et degrees le convertit en degrés
        strength = distance / 10  
        self.shoot(angle, strength)

    def shoot(self, angle, strength):
        """
        Fonction pour tirer la balle en fonction de l'angle et de la force spécifiés.
        Cette fonction met à jour la vitesse de la balle en fonction de l'angle et de la force du tir.
        
        Args:
            angle (float): L'angle du tir en degrés.
            strength (float): La force du tir.
        """
        # Lancement de la balle
        radian_angle = math.radians(angle)
        self.velocity_x = strength * math.cos(radian_angle)
        self.velocity_y = -strength * math.sin(radian_angle)

    def draw(self, fenetre):
        """
        Fonction pour dessiner la balle sur la fenêtre.
        Cette fonction est appelée à chaque frame pour afficher la balle à sa position actuelle.

        Args:
            fenetre (pygame.Surface): La fenêtre sur laquelle dessiner la balle.
        """
        # Affichage de la balle
        fenetre.blit(self.balle_image, self.position)
        
        # Affichage des sélecteurs de tir si nécessaire
        if self.show_shot_selectors:
            self.draw_shot_selectors(fenetre)
            
    def draw_shot_selectors(self, fenetre):
        """
        Fonction pour dessiner les sélecteurs de puissance et d'angle sur la fenêtre.
        Cette fonction est appelée lorsque le mode sélecteur est activé.

        Args:
            fenetre (pygame.Surface): La fenêtre sur laquelle dessiner les sélecteurs.
        """
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
        
        