import pygame as pg
import time
import random

class Partie:
    def __init__(self):
        # Initialisation des paramètres de la partie
        self.score = [0, 0]
        self.current_player = 0
        self.start_time = time.time()
        self.game_duration = 60
        self.game_started = False
        self.selecting_game_mode = False
        self.show_hitboxes = False
        self.last_hoop_time = 0
        self.cooldown = 1
        self.is_multiplayer = False
        self.last_asset_spawn_time = 0
        self.asset_spawn_interval = 3
        self.active_effects = {}
        self.show_cheats_menu = False
        self.one_position = None 
        self.one_display_time = 0 
        self.one_image = pg.transform.scale(pg.image.load("assets/one.png"), (50, 50)) 
        # Création des boutons
        self.single_player_button_rect = pg.Rect(540, 310, 200, 50)
        self.multiplayer_button_rect = pg.Rect(540, 370, 200, 50)
        self.game_mode_10s_button_rect = pg.Rect(540, 310, 200, 50)
        self.game_mode_30s_button_rect = pg.Rect(540, 370, 200, 50)
        self.game_mode_60s_button_rect = pg.Rect(540, 430, 200, 50)
        self.go_back_button_rect = pg.Rect(540, 490, 200, 50)
        self.cheats_button_rect = pg.Rect(540, 550, 200, 50)
        self.double_points_button_rect = pg.Rect(540, 310, 200, 50)
        self.double_speed_button_rect = pg.Rect(540, 370, 200, 50)
        self.low_gravity_button_rect = pg.Rect(540, 430, 200, 50)
        self.plus_one_button_rect = pg.Rect(540, 490, 200, 50)

    def reset(self):
        self.score = [0, 0]
        self.current_player = 0
        self.start_time = time.time()
        self.game_started = False
        self.selecting_game_mode = False
        self.active_effects = {}
        self.one_position = None
        self.one_display_time = 0

    def switch_turn(self):
        self.current_player = 1 - self.current_player

    def get_remaining_time(self):
        elapsed_time = time.time() - self.start_time
        return max(0, self.game_duration - elapsed_time)

    def check_collision(self, balle_rect, panier_rect):
        return balle_rect.colliderect(panier_rect)

    def is_hitbox_within_terrain(self, hitbox, terrain_width, terrain_height):
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
        if event.type == pg.MOUSEBUTTONDOWN:
            if not self.game_started and not self.selecting_game_mode:
                if self.single_player_button_rect.collidepoint(event.pos):
                    self.is_multiplayer = False
                    self.selecting_game_mode = True
                elif self.multiplayer_button_rect.collidepoint(event.pos):
                    self.is_multiplayer = True
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
            elif self.show_cheats_menu:
                if self.double_points_button_rect.collidepoint(event.pos):
                    self.toggle_cheat("double_points", balle)
                elif self.double_speed_button_rect.collidepoint(event.pos):
                    self.toggle_cheat("double_speed", balle)
                elif self.low_gravity_button_rect.collidepoint(event.pos):
                    self.toggle_cheat("low_gravity", balle)
                elif self.plus_one_button_rect.collidepoint(event.pos):
                    self.toggle_cheat("plus_one", balle)
                elif self.go_back_button_rect.collidepoint(event.pos):
                    self.show_cheats_menu = False

        if self.game_started:
            if self.current_player == 0 or self.is_multiplayer:
                balle.handle_event(event, joueur.position)
            elif self.current_player == 1 and not self.is_multiplayer:
                self.ia_take_turn(balle)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_j:
                    self.show_hitboxes = not self.show_hitboxes
                elif event.key == pg.K_f:
                    self.show_cheats_menu = not self.show_cheats_menu

    def ia_take_turn(self, balle):
        if balle.shooting_mode and not balle.flying:
            angle = random.randint(30, 60)
            strength = random.randint(30, 70)
            balle.shoot(angle, strength)
            balle.flying = True
            balle.shooting_mode = False
            self.switch_turn()

    def update(self, fenetre, background_image, joueur, terrain, balle):
        fenetre.fill((255, 255, 255))

        if self.game_started:
            remaining_time = self.get_remaining_time()

            if remaining_time == 0:
                fenetre.blit(background_image, (0, 0))
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (640, 300), 50, (255, 255, 255))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (640, 360), 50, (255, 255, 255))
                self.draw_button(fenetre, "Menu Principal", self.go_back_button_rect, (255, 0, 0), (200, 0, 0))
            else:
                terrain.afficherTerrain(fenetre)
                terrain.afficherAssets(fenetre)

                
                current_time = time.time()
                if current_time - self.last_asset_spawn_time > self.asset_spawn_interval:
                    terrain.spawn_asset()
                    self.last_asset_spawn_time = current_time

                if balle.shooting_mode and not balle.dragging and not balle.flying:
                    balle.position = [joueur.position[0], joueur.position[1] - 30]
                    balle.rect.topleft = balle.position

                joueur.draw(fenetre)
                balle.update_position(fenetre.get_width(), fenetre.get_height())
                balle.draw(fenetre)

                self.draw_text(fenetre, "Appuyez sur C pour tir manuel", (640, 105), 24, (0, 0, 0))
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (200, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (1080, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Temps: {int(remaining_time)}s", (640, 50), 50, (0, 0, 0))
                self.draw_text(fenetre, f"Tour: Joueur {self.current_player + 1}", (640, 80), 30, (0, 0, 0))

                self.check_panier_collision(terrain, balle)
                self.check_asset_collision(balle, terrain)  
                self.update_effects(balle)  
                terrain.afficherPanier(fenetre)

                if self.one_position and current_time - self.one_display_time < 1:
                    self.draw_one(fenetre)
                else:
                    self.one_position = None

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

        if self.show_cheats_menu:
            self.draw_cheats_menu(fenetre)

    def check_panier_collision(self, terrain, balle):
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        top_hitbox = pg.Rect(panier_rect_full.left, panier_rect_full.top, panier_rect_full.width, hitbox_height)
        side_hitbox_left = pg.Rect(panier_rect_full.left, panier_rect_full.top + hitbox_height, hitbox_height, panier_rect_full.height - hitbox_height)
        side_hitbox_right = pg.Rect(panier_rect_full.right - hitbox_height, panier_rect_full.top + hitbox_height, hitbox_height, panier_rect_full.height - hitbox_height)
        current_time = time.time()

        if self.check_collision(balle_rect, top_hitbox) and (current_time - self.last_hoop_time) > self.cooldown:
            terrain.positionPanier = terrain.genererPositionPanier()
            self.last_hoop_time = current_time
            points = 2 if "double_points" in self.active_effects else 1
            self.score[self.current_player] += points
            balle.shooting_mode = True
            balle.flying = False
            self.switch_turn()
            self.one_position = [terrain.positionPanier[0] + 50, terrain.positionPanier[1]]
            self.one_display_time = current_time

        if self.check_collision(balle_rect, side_hitbox_left) or self.check_collision(balle_rect, side_hitbox_right):
            balle.velocity_x = -balle.velocity_x  # Bounce on the sides

        if not self.is_hitbox_within_terrain(panier_rect_full, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()

    def check_asset_collision(self, balle, terrain):
        balle_rect = balle.rect
        for asset, position in list(terrain.asset_positions.items()):
            asset_rect = pg.Rect(position[0], position[1], 50, 50)
            if balle_rect.colliderect(asset_rect):
                self.apply_asset_effect(asset, balle)
                del terrain.asset_positions[asset]
                del terrain.asset_timers[asset]

    def apply_asset_effect(self, asset, balle):
        effect_duration = 10  # durée des power ups
        
        current_time = time.time()
        if asset == "double_points":
            self.active_effects["double_points"] = current_time + effect_duration
        elif asset == "double_speed":
            balle.speed *= 2  
            self.active_effects["double_speed"] = current_time + effect_duration
        elif asset == "low_gravity":
            balle.gravity /= 2  
            self.active_effects["low_gravity"] = current_time + effect_duration
        elif asset == "plus_one":
            self.score[self.current_player] += 1
            self.one_position = [balle.position[0], balle.position[1]] 
            self.one_display_time = time.time()

    def update_effects(self, balle):
        current_time = time.time()
        if "double_speed" in self.active_effects and current_time > self.active_effects["double_speed"]:
            balle.speed /= 2  #arrete l'effet vitesse
            del self.active_effects["double_speed"]
        if "low_gravity" in self.active_effects and current_time > self.active_effects["low_gravity"]:
            balle.gravity *= 2  #arrete l'effet gravité
            del self.active_effects["low_gravity"]

    def draw_hitboxes(self, fenetre, terrain, balle):
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)

        if not self.is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()

        pg.draw.rect(fenetre, (255, 0, 0), balle_rect, 2)
        pg.draw.rect(fenetre, (0, 255, 0), panier_rect, 2)

    def reset_game(self, joueur, terrain, balle):
        joueur.position = [640, 600]
        terrain.positionPanier = terrain.genererPositionPanier()
        balle.position = [joueur.position[0], joueur.position[1] - 30]
        balle.rect.topleft = balle.position
        balle.velocity_x = 0
        balle.velocity_y = 0
        balle.shooting_mode = True
        balle.flying = False
        self.reset()

    def set_asset_spawn_interval(self, interval):
        self.asset_spawn_interval = interval

    def draw_cheats_menu(self, fenetre):
        self.draw_button(fenetre, "Double Points", self.double_points_button_rect, (0, 255, 0), (0, 200, 0))
        self.draw_button(fenetre, "Double Speed", self.double_speed_button_rect, (0, 0, 255), (0, 0, 200))
        self.draw_button(fenetre, "Low Gravity", self.low_gravity_button_rect, (255, 165, 0), (200, 130, 0))
        self.draw_button(fenetre, "Plus One", self.plus_one_button_rect, (255, 0, 255), (200, 0, 200))

    def toggle_cheat(self, cheat, balle):
        current_time = time.time()
        effect_duration = 10  # durée des power ups
        if cheat == "double_points":
            if "double_points" in self.active_effects:
                del self.active_effects["double_points"]
            else:
                self.active_effects["double_points"] = current_time + effect_duration
        elif cheat == "double_speed":
            if "double_speed" in self.active_effects:
                balle.speed /= 2
                del self.active_effects["double_speed"]
            else:
                balle.speed *= 2
                self.active_effects["double_speed"] = current_time + effect_duration
        elif cheat == "low_gravity":
            if "low_gravity" in self.active_effects:
                balle.gravity *= 2
                del self.active_effects["low_gravity"]
            else:
                balle.gravity /= 2
                self.active_effects["low_gravity"] = current_time + effect_duration
        elif cheat == "plus_one":
            self.score[self.current_player] += 1

    def draw_one(self, fenetre):
        fenetre.blit(self.one_image, self.one_position)