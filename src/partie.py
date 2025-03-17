import pygame as pg
import time
import random

class Partie:
    def __init__(self):
        # Initialisation des paramètres de la partie
        self.score = [0, 0]  # Score du joueur 1 et du joueur 2/IA
        self.current_player = 0  # 0 pour joueur 1, 1 pour joueur 2/IA
        self.start_time = time.time()
        self.game_duration = 60
        self.game_started = False
        self.selecting_game_mode = False
        self.show_hitboxes = False
        self.last_hoop_time = 0
        self.cooldown = 1  # cooldown entre chaque panier (en s)
        self.is_multiplayer = False  # Mode multijoueur ou IA

        # Création des boutons
        self.single_player_button_rect = pg.Rect(540, 310, 200, 50)
        self.multiplayer_button_rect = pg.Rect(540, 370, 200, 50)
        self.game_mode_10s_button_rect = pg.Rect(540, 310, 200, 50)
        self.game_mode_30s_button_rect = pg.Rect(540, 370, 200, 50)
        self.game_mode_60s_button_rect = pg.Rect(540, 430, 200, 50)
        self.go_back_button_rect = pg.Rect(540, 490, 200, 50)

    def reset(self):
        # Réinitialisation de la partie
        self.score = [0, 0]
        self.current_player = 0 # on commence avec le joueur 1
        self.start_time = time.time()
        self.game_started = False
        self.selecting_game_mode = False

    def switch_turn(self):
        # Changement de tour
        self.current_player = 1 - self.current_player  # Alterne entre 0(joueur 1) et 1(joueur 2/IA)

    def get_remaining_time(self):
        # Calcul du temps restant
        elapsed_time = time.time() - self.start_time
        return max(0, self.game_duration - elapsed_time)
    
    def check_collision(self, balle_rect, panier_rect):
        # Vérifie les collisions pour les paniers
        return balle_rect.colliderect(panier_rect)
    
    def is_hitbox_within_terrain(self, hitbox, terrain_width, terrain_height):
        # Empêche de spawn en dehors de la map
        return (hitbox.left >= 0 and hitbox.right <= terrain_width and
                hitbox.top >= 0 and hitbox.bottom <= terrain_height)
    
    def draw_button(self, surface, text, rect, color, hover_color):
        mouse_pos = pg.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pg.draw.rect(surface, hover_color, rect)
        else:
            pg.draw.rect(surface, color, rect)
        font = pg.font.Font(None, 36)
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
    
    def draw_text(self, surface, text, position, font_size, color):
        font = pg.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event, joueur, terrain, balle):
        # Gestion des événements de la partie
        if event.type == pg.MOUSEBUTTONDOWN:
            if not self.game_started and not self.selecting_game_mode:
                if self.single_player_button_rect.collidepoint(event.pos):
                    self.is_multiplayer = False # Mode solo
                    self.selecting_game_mode = True
                elif self.multiplayer_button_rect.collidepoint(event.pos):
                    self.is_multiplayer = True # Mode multijoueur
                    self.selecting_game_mode = True
            elif self.selecting_game_mode:
                if self.game_mode_10s_button_rect.collidepoint(event.pos):
                    self.game_duration = 10
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
                elif self.game_mode_30s_button_rect.collidepoint(event.pos):
                    self.game_duration = 30
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
                elif self.game_mode_60s_button_rect.collidepoint(event.pos):
                    self.game_duration = 60
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
            elif self.game_started and self.get_remaining_time() == 0:
                if self.go_back_button_rect.collidepoint(event.pos):
                    self.reset_game(joueur, terrain, balle)

        if self.game_started:
            if self.current_player == 0 or self.is_multiplayer:
                balle.handle_event(event, joueur.position, self)
            elif self.current_player == 1 and not self.is_multiplayer:
                self.ia_take_turn(balle) # IA effectue son tir automatiquement
            if event.type == pg.KEYDOWN: # si tu appuyes sur J, dessine les hitbox
                if event.key == pg.K_j:
                    self.show_hitboxes = not self.show_hitboxes

    def ia_take_turn(self, balle):
        # Logique pour que l'IA effectue un tir
        if balle.shooting_mode and not balle.flying:
            angle = random.randint(30, 60)  # Angle aléatoire
            strength = random.randint(30, 70)  # Puissance aléatoire
            balle.shoot(angle, strength)
            balle.flying = True
            balle.shooting_mode = False
            self.switch_turn()

    def update(self, fenetre, background_image, joueur, terrain, balle):
        # Mise à jour et rendu de la partie
        fenetre.fill((255, 255, 255))

        if self.game_started:
            remaining_time = self.get_remaining_time()

            if remaining_time == 0: #affiche écran de fin quand plus de temps
                fenetre.blit(background_image, (0, 0))
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (640, 300), 50, (255, 255, 255))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (640, 360), 50, (255, 255, 255))
                self.draw_button(fenetre, "Menu Principal", self.go_back_button_rect, (255, 0, 0), (200, 0, 0))
            else:
                terrain.afficherTerrain(fenetre)

                # Si la balle est en mode shooting et n'est pas en train d'être traînée, la balle se met sur le joueur
                if balle.shooting_mode and not balle.dragging and not balle.flying:
                    balle.position = [joueur.position[0], joueur.position[1] - 30]
                    balle.rect.topleft = balle.position

                joueur.draw(fenetre)
                balle.update_position(fenetre.get_width(), fenetre.get_height())
                balle.draw(fenetre)

                # Ajout d'une instruction pour le tir manuel
                self.draw_text(fenetre, "Appuyez sur C pour tir manuel", (640, 105), 24, (0,0,0))
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (200, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (1080, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Temps: {int(remaining_time)}s", (640, 50), 50, (0, 0, 0))
                self.draw_text(fenetre, f"Tour: Joueur {self.current_player + 1}", (640, 80), 30, (0, 0, 0))

                self.check_panier_collision(terrain, balle)
                terrain.afficherPanier(fenetre)

                if self.show_hitboxes:
                    self.draw_hitboxes(fenetre, terrain, balle)
        else:
            fenetre.blit(background_image, (0, 0))
            if self.selecting_game_mode:
                self.draw_button(fenetre, "10s", self.game_mode_10s_button_rect, (255, 0, 0), (200, 0, 0))
                self.draw_button(fenetre, "30s", self.game_mode_30s_button_rect, (255, 165, 0), (200, 130, 0))
                self.draw_button(fenetre, "60s", self.game_mode_60s_button_rect, (0, 255, 0), (0, 200, 0))
            else:
                self.draw_button(fenetre, "Single Player", self.single_player_button_rect, (0, 255, 0), (0, 200, 0))
                self.draw_button(fenetre, "Multiplayer", self.multiplayer_button_rect, (0, 0, 255), (0, 0, 200))
    
    def check_panier_collision(self, terrain, balle):
        # Vérification des collisions avec le panier
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
        current_time = time.time()
        # Réinitialisation de la balle en mode shooting après un panier
        if self.check_collision(balle_rect, panier_rect) and (current_time - self.last_hoop_time) > self.cooldown: # si collision + pas de ccooldown
            terrain.positionPanier = terrain.genererPositionPanier() # bouge le panier
            self.last_hoop_time = current_time # reset cooldown
            self.score[1-self.current_player] += 1 #comme on change de joueur au moment du tir, on ajoute le point au joueur précédent
            balle.shooting_mode = True # réinitialision de la balle en mode shooting après un panier
            balle.flying = False
        
        if not self.is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()
    
    def draw_hitboxes(self, fenetre, terrain, balle):
        # Affichage des hitboxes pour le débogage
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
        
        if not self.is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()
        
        pg.draw.rect(fenetre, (255, 0, 0), balle_rect, 2)  
        pg.draw.rect(fenetre, (0, 255, 0), panier_rect, 2)  
    
    def reset_game(self, joueur, terrain, balle):
        # Redémarrage de la partie quand elle est finie
        joueur.position = [640, 600]  # Position par défaut du joueur
        terrain.positionPanier = terrain.genererPositionPanier()
        # Réinitialiser la balle à la position du joueur et en mode shooting
        balle.position = [joueur.position[0], joueur.position[1] - 30]
        balle.rect.topleft = balle.position
        balle.velocity_x = 0
        balle.velocity_y = 0
        balle.shooting_mode = True
        balle.flying = False
        self.reset()