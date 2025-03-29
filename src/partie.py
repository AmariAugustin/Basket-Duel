import pygame as pg
import time
import random
import client
import serveur
import json

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
        self.cooldown = 1  # cooldown entre chaque panier (en s)
        self.is_multiplayer = False  # Mode multijoueur ou IA
        self.is_online = False  # Mode en ligne
        self.is_server = False  # Mode serveur ou client    
        self.is_client = False  # Mode client
        self.waiting_for_server = False  # Attente de connexion au serveur
        self.serveur = None
        self.client = None
        self.connection_established = False  # Nouveau flag pour suivre l'état de la connexion
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
        self.online_button_rect = pg.Rect(540, 430, 200, 50)
        self.sever_button_rect = pg.Rect(540, 490, 200, 50)
        self.client_button_rect = pg.Rect(540, 550, 200, 50)
        self.cheats_button_rect = pg.Rect(540, 550, 200, 50)
        self.double_points_button_rect = pg.Rect(540, 310, 200, 50)
        self.double_speed_button_rect = pg.Rect(540, 370, 200, 50)
        self.low_gravity_button_rect = pg.Rect(540, 430, 200, 50)
        self.plus_one_button_rect = pg.Rect(540, 490, 200, 50)

        # Creation des inputs
        self.input_ip_rect = pg.Rect(540, 310, 200, 50)
        self.input_port_rect = pg.Rect(540, 370, 200, 50)
        self.valid_button_rect = pg.Rect(540, 430, 200, 50)

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
                elif self.online_button_rect.collidepoint(event.pos):
                    self.is_online = True
            
            if self.is_online and not self.selecting_game_mode:
                if self.sever_button_rect.collidepoint(event.pos):
                    self.is_server = True
                    print("Création du serveur")
                    self.waiting_for_server = True
                    self.serveur = self.createServer()
                    if self.serveur:
                        self.connection_established = True
                        self.waiting_for_server = False
                        self.selecting_game_mode = True
                elif self.client_button_rect.collidepoint(event.pos):
                    self.is_client = True
                    print("Création du client")
                    self.client = self.createClient()
                    if self.client and self.client.connected:
                        self.waiting_for_server = True
                        self.connection_established = True
                        self.selecting_game_mode = True

            elif self.selecting_game_mode:
                if self.game_mode_10s_button_rect.collidepoint(event.pos):
                    self.game_duration = 10
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
                    if self.is_online and self.is_server and self.serveur:
                        try:
                            self.serveur.send("10s")
                        except Exception as e:
                            print(f"Erreur lors de l'envoi de la durée: {e}")
                elif self.game_mode_30s_button_rect.collidepoint(event.pos):
                    self.game_duration = 30
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
                    if self.is_online and self.is_server and self.serveur:
                        try:
                            self.serveur.send("30s")
                        except Exception as e:
                            print(f"Erreur lors de l'envoi de la durée: {e}")
                elif self.game_mode_60s_button_rect.collidepoint(event.pos):
                    self.game_duration = 60
                    self.game_started = True
                    self.start_time = time.time()
                    self.selecting_game_mode = False
                    if self.is_online and self.is_server and self.serveur:
                        try:
                            self.serveur.send("60s")
                        except Exception as e:
                            print(f"Erreur lors de l'envoi de la durée: {e}")

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
            elif self.current_player == 1 and not self.is_multiplayer and not self.is_online:
                self.ia_take_turn(balle) # IA effectue son tir automatiquement
            elif self.is_online and self.connection_established:
                if self.is_server and self.current_player == 0:
                    balle.handle_event(event, joueur.position)
                    self.sync_game_state(joueur, balle, terrain)
                elif self.is_client and self.current_player == 1:
                    balle.handle_event(event, joueur.position)
                    self.sync_game_state(joueur, balle, terrain)
                else:
                    self.receive_game_state(joueur, balle, terrain)
            if event.type == pg.KEYDOWN: # si tu appuyes sur J, dessine les hitbox
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

    def sync_game_state(self, joueur, balle, terrain):
        if self.is_online and self.connection_established:
            try:
                game_state = {
                    'score': self.score,
                    'player_pos': joueur.position,
                    'ball_pos': balle.position,
                    'ball_velocity': [balle.velocity_x, balle.velocity_y],
                    'ball_flying': balle.flying,
                    'ball_shooting_mode': balle.shooting_mode,
                    'hoop_pos': terrain.positionPanier,
                    'current_player': self.current_player
                }
                game_state_json = json.dumps(game_state)
                
                if self.is_server and self.current_player == 0:
                    self.serveur.send(f"STATE:{game_state_json}")
                elif self.is_client and self.current_player == 1:
                    self.client.send(f"STATE:{game_state_json}")
            except Exception as e:
                print(f"Erreur lors de la synchronisation: {e}")
                self.connection_established = False

    def receive_game_state(self, joueur, balle, terrain):
        if self.is_online and self.connection_established:
            try:
                if self.is_server and self.current_player == 1:
                    data = self.serveur.receive()
                    if data is None:
                        print("Connexion perdue avec le client")
                        self.connection_established = False
                        return
                    
                    if isinstance(data, str) and data.startswith("STATE:"):
                        try:
                            game_state = json.loads(data[6:])
                            self.score = game_state['score']
                            joueur.position = game_state['player_pos']
                            balle.position = game_state['ball_pos']
                            balle.velocity_x, balle.velocity_y = game_state['ball_velocity']
                            balle.flying = game_state['ball_flying']
                            balle.shooting_mode = game_state['ball_shooting_mode']
                            terrain.positionPanier = game_state['hoop_pos']
                            self.current_player = game_state['current_player']
                        except json.JSONDecodeError as e:
                            print(f"Erreur lors du parsing JSON: {e}")
                            self.connection_established = False
                            
                elif self.is_client and self.current_player == 0:
                    data = self.client.receive()
                    if data is None:
                        print("Connexion perdue avec le serveur")
                        self.connection_established = False
                        return
                    
                    if isinstance(data, str) and data.startswith("STATE:"):
                        try:
                            game_state = json.loads(data[6:])
                            self.score = game_state['score']
                            joueur.position = game_state['player_pos']
                            balle.position = game_state['ball_pos']
                            balle.velocity_x, balle.velocity_y = game_state['ball_velocity']
                            balle.flying = game_state['ball_flying']
                            balle.shooting_mode = game_state['ball_shooting_mode']
                            terrain.positionPanier = game_state['hoop_pos']
                            self.current_player = game_state['current_player']
                        except json.JSONDecodeError as e:
                            print(f"Erreur lors du parsing JSON: {e}")
                            self.connection_established = False
            except Exception as e:
                print(f"Erreur lors de la réception de l'état: {e}")
                self.connection_established = False

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

                # Synchronisation de l'état du jeu
                if self.is_online and self.connection_established:
                    if self.current_player == 0 and self.is_server:
                        self.sync_game_state(joueur, balle, terrain)
                    elif self.current_player == 1 and self.is_client:
                        self.sync_game_state(joueur, balle, terrain)
                    else:
                        self.receive_game_state(joueur, balle, terrain)

                # Affichage du score et du temps restant
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (200, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (1080, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Temps: {int(remaining_time)}s", (640, 50), 50, (0, 0, 0))
                self.draw_text(fenetre, f"Tour: Joueur {self.current_player + 1}", (640, 80), 30, (0, 0, 0))

                # Affichage du tour en mode online
                if self.is_online:
                    if self.is_server:
                        if self.current_player == 0:
                            self.draw_text(fenetre, "C'est votre tour (Serveur)", (640, 150), 36, (0, 255, 0))
                        else:
                            self.draw_text(fenetre, "Tour du client", (640, 150), 36, (255, 0, 0))
                    else:  # Client
                        if self.current_player == 1:
                            self.draw_text(fenetre, "C'est votre tour (Client)", (640, 150), 36, (0, 255, 0))
                        else:
                            self.draw_text(fenetre, "Tour du serveur", (640, 150), 36, (255, 0, 0))

                # Affichage des commandes de tir
                if balle.shooting_mode and not balle.flying:
                    self.draw_text(fenetre, "Clic gauche pour tirer", (640, 200), 24, (0, 0, 0))
                    self.draw_text(fenetre, "Maintenez pour ajuster la puissance", (640, 230), 24, (0, 0, 0))

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
            elif self.is_multiplayer == False and self.is_online == False:
                self.draw_button(fenetre, "Single Player", self.single_player_button_rect, (0, 255, 0), (0, 200, 0))
                self.draw_button(fenetre, "Multiplayer", self.multiplayer_button_rect, (0, 0, 255), (0, 0, 200))
                self.draw_button(fenetre, "Online", self.online_button_rect, (255, 0, 0), (200, 0, 0))
            
            elif self.is_online and not self.is_server and not self.is_client:
                self.draw_button(fenetre, "Server", self.sever_button_rect, (255, 0, 0), (200, 0, 0))
                self.draw_button(fenetre, "Client", self.client_button_rect, (0, 255, 0), (0, 200, 0))
            
            elif self.waiting_for_server:
                if self.is_client:
                    # Check for game duration from server
                    data = self.client.receive()
                    if data:
                        try:
                            duration = data.decode()
                            if duration in ["60s", "30s", "10s"]:
                                self.game_duration = int(duration[:-1])
                                self.game_started = True
                                self.start_time = time.time()
                                self.selecting_game_mode = False
                                self.waiting_for_server = False
                        except Exception as e:
                            print(f"Erreur lors de la réception de la durée: {e}")
                self.draw_text(fenetre, "En attente de connexion...", (640, 360), 50, (0, 0, 0))

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
            
            # Synchroniser le score et la position du panier en mode online
            if self.is_online and self.connection_established:
                try:
                    if self.is_server and self.current_player == 0:
                        self.serveur.send(f"SCORE:{self.score[self.current_player]}")
                        self.serveur.send(f"HOOP:{terrain.positionPanier}")
                    elif self.is_client and self.current_player == 1:
                        self.client.send(f"SCORE:{self.score[self.current_player]}")
                        self.client.send(f"HOOP:{terrain.positionPanier}")
                except Exception as e:
                    print(f"Erreur lors de la synchronisation du score: {e}")
            
            balle.shooting_mode = True
            balle.flying = False
            self.switch_turn()
            self.one_position = [terrain.positionPanier[0] + 50, terrain.positionPanier[1]]
            self.one_display_time = current_time

        if self.check_collision(balle_rect, side_hitbox_left) or self.check_collision(balle_rect, side_hitbox_right):
            balle.velocity_x = -balle.velocity_x  # Bounce on the sides

        if not self.is_hitbox_within_terrain(panier_rect_full, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()
            # Synchroniser la nouvelle position du panier en mode online
            if self.is_online and self.connection_established:
                try:
                    if self.is_server:
                        self.serveur.send(f"HOOP:{terrain.positionPanier}")
                    elif self.is_client:
                        self.client.send(f"HOOP:{terrain.positionPanier}")
                except Exception as e:
                    print(f"Erreur lors de la synchronisation du panier: {e}")

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
        # Clean up network connections
        if self.serveur:
            self.serveur.cleanup()
            self.serveur = None
        if self.client:
            self.client.cleanup()
            self.client = None
        
        # Reset game state
        joueur.position = [640, 600]  # Position par défaut du joueur
        terrain.positionPanier = terrain.genererPositionPanier()
        balle.position = [joueur.position[0], joueur.position[1] - 30]
        balle.rect.topleft = balle.position
        balle.velocity_x = 0
        balle.velocity_y = 0
        balle.shooting_mode = True
        balle.flying = False
        self.reset()
        
        # Reset online state
        self.is_online = False
        self.is_server = False
        self.is_client = False
        self.connection_established = False

    def createServer(self):
        try:
            # Clean up any existing server
            if self.serveur:
                self.serveur.cleanup()
            
            s = serveur.Serveur()
            print("Serveur créé avec succès")
            # Start the server in a separate thread to avoid blocking
            import threading
            server_thread = threading.Thread(target=s.run)
            server_thread.daemon = True  # Thread will exit when main program exits
            server_thread.start()
            return s
        except Exception as e:
            print(f"Erreur lors de la création du serveur: {e}")
            return None
    
    def createClient(self):
        try:
            # Clean up any existing client
            if self.client:
                self.client.cleanup()
            
            c = client.Client()
            print("Client créé avec succès")
            if not c.connected:
                print("Impossible de se connecter au serveur")
                return None
            return c
        except Exception as e:
            print(f"Erreur lors de la création du client: {e}")
            return None

    def getPlayer(self):
        return self.current_player

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
