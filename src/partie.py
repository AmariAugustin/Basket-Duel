import pygame as pg
import time
import random
import client
import serveur
import json

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
        self.is_online = False  # Mode en ligne
        self.is_server = False  # Mode serveur ou client    
        self.is_client = False  # Mode client
        self.waiting_for_server = False  # Attente de connexion au serveur
        self.serveur = None
        self.client = None
        self.connection_established = False  # Nouveau flag pour suivre l'état de la connexion

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

        # Creation des inputs
        self.input_ip_rect = pg.Rect(540, 310, 200, 50)
        self.input_port_rect = pg.Rect(540, 370, 200, 50)
        self.valid_button_rect = pg.Rect(540, 430, 200, 50)

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

        if self.game_started:
            if self.current_player == 0 or self.is_multiplayer:
                balle.handle_event(event, joueur.position)
            elif self.current_player == 1 and not self.is_multiplayer and not self.is_online:
                self.ia_take_turn(balle) # IA effectue son tir automatiquement
            elif self.is_online and self.connection_established:
                if self.is_server and self.current_player == 0:
                    balle.handle_event(event, joueur.position, self.serveur, self)
                elif self.is_client and self.current_player == 1:
                    balle.handle_event(event, joueur.position, self.client, self)
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

    def sync_game_state(self, joueur, balle, terrain):
        if self.is_online and self.connection_established:
            try:
                if self.is_server and self.current_player == 0:
                    # Server sends game state
                    game_state = {
                        'score': self.score,
                        'player_pos': joueur.position,
                        'ball_pos': balle.position,
                        'ball_velocity': [balle.velocity_x, balle.velocity_y],
                        'ball_flying': balle.flying,
                        'ball_shooting_mode': balle.shooting_mode,
                        'hoop_pos': terrain.positionPanier
                    }
                    self.serveur.send(str(game_state))
                elif self.is_client and self.current_player == 1:
                    # Client sends game state
                    game_state = {
                        'score': self.score,
                        'player_pos': joueur.position,
                        'ball_pos': balle.position,
                        'ball_velocity': [balle.velocity_x, balle.velocity_y],
                        'ball_flying': balle.flying,
                        'ball_shooting_mode': balle.shooting_mode,
                        'hoop_pos': terrain.positionPanier
                    }
                    self.client.send(str(game_state))
            except Exception as e:
                print(f"Erreur lors de la synchronisation: {e}")

    def receive_game_state(self, joueur, balle, terrain):
        if self.is_online and self.connection_established:
            try:
                if self.is_server and self.current_player == 1:
                    # Server receives game state from client
                    data = self.serveur.receive()
                    if data is None:
                        print("Connexion perdue avec le client")
                        self.connection_established = False
                        return
                    try:
                        game_state = eval(data)
                        self.score = game_state['score']
                        joueur.position = game_state['player_pos']
                        balle.position = game_state['ball_pos']
                        balle.velocity_x, balle.velocity_y = game_state['ball_velocity']
                        balle.flying = game_state['ball_flying']
                        balle.shooting_mode = game_state['ball_shooting_mode']
                        terrain.positionPanier = game_state['hoop_pos']
                    except (SyntaxError, KeyError) as e:
                        print(f"Erreur lors du parsing de l'état: {e}")
                elif self.is_client and self.current_player == 0:
                    # Client receives game state from server
                    data = self.client.receive()
                    if data is None:
                        print("Connexion perdue avec le serveur")
                        self.connection_established = False
                        return
                    try:
                        game_state = eval(data)
                        self.score = game_state['score']
                        joueur.position = game_state['player_pos']
                        balle.position = game_state['ball_pos']
                        balle.velocity_x, balle.velocity_y = game_state['ball_velocity']
                        balle.flying = game_state['ball_flying']
                        balle.shooting_mode = game_state['ball_shooting_mode']
                        terrain.positionPanier = game_state['hoop_pos']
                    except (SyntaxError, KeyError) as e:
                        print(f"Erreur lors du parsing de l'état: {e}")
            except Exception as e:
                print(f"Erreur lors de la réception de l'état: {e}")
                self.connection_established = False

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

                # Synchronisation de l'état du jeu
                if self.is_online and self.connection_established:
                    if self.current_player == 0 and self.is_server:
                        self.sync_game_state(joueur, balle, terrain)
                    elif self.current_player == 1 and self.is_client:
                        self.sync_game_state(joueur, balle, terrain)
                    else:
                        self.receive_game_state(joueur, balle, terrain)

                # Affichage du score et du temps restant
                self.draw_text(fenetre, f"Score: {self.score[0]} - {self.score[1]}", (640, 50), 36, (0, 0, 0))
                self.draw_text(fenetre, f"Temps: {int(remaining_time)}s", (640, 100), 36, (0, 0, 0))

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
                terrain.afficherPanier(fenetre)

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
    
    def check_panier_collision(self, terrain, balle):
        # Vérification des collisions avec le panier
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
        current_time = time.time()
        
        # Réinitialisation de la balle en mode shooting après un panier
        if self.check_collision(balle_rect, panier_rect) and (current_time - self.last_hoop_time) > self.cooldown:
            terrain.positionPanier = terrain.genererPositionPanier()
            self.last_hoop_time = current_time
            self.score[self.current_player] += 1
            
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
        
        if not self.is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
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
        # Réinitialiser la balle à la position du joueur et en mode shooting
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