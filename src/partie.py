import pygame as pg
import time
import random
import client
import serveur
import json
import threading

class Partie:
    """
    Classe principale gérant la logique du jeu de basketball.
    
    Attributs:
        score (list): Scores des joueurs [joueur1, joueur2]
        current_player (int): Index du joueur actuel (0 ou 1)
        start_time (float): Temps de début de la partie
        game_duration (int): Durée totale de la partie en secondes
        game_started (bool): Si la partie a commencé
        selecting_game_mode (bool): Si le mode de jeu est en sélection
        show_hitboxes (bool): Afficher les hitboxes pour le débogage
        last_hoop_time (float): Dernier temps où un panier a été marqué
        cooldown (float): Temps entre chaque panier possible
        is_multiplayer (bool): Mode multijoueur local activé
        is_online (bool): Mode en ligne activé
        is_server (bool): Le jeu est serveur en mode online
        is_client (bool): Le jeu est client en mode online
        waiting_for_server (bool): En attente de connexion au serveur
        serveur (Serveur): Instance du serveur
        client (Client): Instance du client
        connection_established (bool): Connexion réseau établie
        last_asset_spawn_time (float): Dernier spawn d'asset
        asset_spawn_interval (float): Intervalle entre les spawns d'assets
        active_effects (dict): Effets actifs et leur temps d'expiration
        show_cheats_menu (bool): Afficher le menu de triche
        one_position (list): Position de l'affichage "+1"
        one_display_time (float): Temps d'affichage du "+1"
        one_image (Surface): Image pour l'affichage "+1"
    """
    
    def __init__(self):
        """Initialise les paramètres de la partie."""
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

        # Création des rectangles pour les boutons
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

        # Création des rectangles pour les inputs
        self.input_ip_rect = pg.Rect(540, 310, 200, 50)
        self.input_port_rect = pg.Rect(540, 370, 200, 50)
        self.valid_button_rect = pg.Rect(540, 430, 200, 50)

    def reset(self):
        """Réinitialise les paramètres de la partie sans changer le mode de jeu."""
        self.score = [0, 0]
        self.current_player = 0
        self.start_time = time.time()
        self.game_started = False
        self.selecting_game_mode = False
        self.active_effects = {}
        self.one_position = None
        self.one_display_time = 0

    def switch_turn(self):
        """Change le tour du joueur actuel."""
        self.current_player = 1 - self.current_player

    def get_remaining_time(self):
        """
        Calcule le temps restant dans la partie.
        
        Returns:
            float: Temps restant en secondes
        """
        elapsed_time = time.time() - self.start_time
        return max(0, self.game_duration - elapsed_time)

    def check_collision(self, balle_rect, panier_rect):
        """
        Vérifie la collision entre deux rectangles.
        
        Args:
            balle_rect (Rect): Rectangle de la balle
            panier_rect (Rect): Rectangle du panier
            
        Returns:
            bool: True si collision, False sinon
        """
        return balle_rect.colliderect(panier_rect)

    def is_hitbox_within_terrain(self, hitbox, terrain_width, terrain_height):
        """
        Vérifie si une hitbox est entièrement dans le terrain.
        
        Args:
            hitbox (Rect): Rectangle à vérifier
            terrain_width (int): Largeur du terrain
            terrain_height (int): Hauteur du terrain
            
        Returns:
            bool: True si la hitbox est dans le terrain
        """
        return (hitbox.left >= 0 and hitbox.right <= terrain_width and
                hitbox.top >= 0 and hitbox.bottom <= terrain_height)

    def draw_button(self, surface, text, rect, color, hover_color):
        """
        Dessine un bouton avec effet de survol.
        
        Args:
            surface (Surface): Surface où dessiner
            text (str): Texte du bouton
            rect (Rect): Rectangle du bouton
            color (tuple): Couleur normale
            hover_color (tuple): Couleur au survol
        """
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
        """
        Dessine du texte centré à une position.
        
        Args:
            surface (Surface): Surface où dessiner
            text (str): Texte à afficher
            position (tuple): Position (x,y) du centre
            font_size (int): Taille de police
            color (tuple): Couleur du texte
        """
        font = pg.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event, fenetre, joueur, terrain, balle):
        """
        Gère les événements du jeu.
        
        Args:
            event (Event): Événement pygame à traiter
            fenetre (Surface): Fenêtre du jeu
            joueur (Joueur): Instance du joueur
            terrain (Terrain): Instance du terrain
            balle (Balle): Instance de la balle
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                if not self.game_started:
                    # Gestion des menus avant le début du jeu
                    if self.selecting_game_mode:
                        # Sélection du mode de jeu
                        if self.game_mode_10s_button_rect.collidepoint(event.pos):
                            self.game_duration = 10
                            self.game_started = True
                            self.start_time = time.time()
                            self.selecting_game_mode = False
                            if self.is_online and self.is_server:
                                self.serveur.send(str(self.game_duration).encode())
                        elif self.game_mode_30s_button_rect.collidepoint(event.pos):
                            self.game_duration = 30
                            self.game_started = True
                            self.start_time = time.time()
                            self.selecting_game_mode = False
                            if self.is_online and self.is_server:
                                self.serveur.send(str(self.game_duration).encode())
                        elif self.game_mode_60s_button_rect.collidepoint(event.pos):
                            self.game_duration = 60
                            self.game_started = True
                            self.start_time = time.time()
                            self.selecting_game_mode = False
                            if self.is_online and self.is_server:
                                self.serveur.send(str(self.game_duration).encode())
                        elif self.go_back_button_rect.collidepoint(event.pos):
                            self.selecting_game_mode = False
                            self.is_online = False
                            self.is_server = False
                            self.is_client = False
                            self.waiting_for_server = False
                            self.connection_established = False
                    elif self.is_multiplayer == False and self.is_online == False:
                        # Menu principal hors ligne
                        if self.single_player_button_rect.collidepoint(event.pos):
                            self.selecting_game_mode = True
                        elif self.multiplayer_button_rect.collidepoint(event.pos):
                            self.is_multiplayer = True
                            self.selecting_game_mode = True
                        elif self.online_button_rect.collidepoint(event.pos):
                            self.is_online = True
                            self.selecting_game_mode = False
                    elif self.is_online and not self.is_server and not self.is_client:
                        # Menu choix serveur/client
                        if self.sever_button_rect.collidepoint(event.pos):
                            self.is_server = True
                            self.createServer()
                            self.selecting_game_mode = True
                        elif self.client_button_rect.collidepoint(event.pos):
                            self.is_client = True
                            self.createClient()
                            self.selecting_game_mode = True
                elif self.game_started and self.get_remaining_time() == 0:
                    # Fin de partie - bouton retour
                    if self.go_back_button_rect.collidepoint(event.pos):
                        self.reset_game(joueur, terrain, balle)
                elif self.show_cheats_menu:
                    # Menu des triches
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
            # Gestion des tirs pendant la partie
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
            
            # Touches de débogage
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_j:  # Afficher les hitboxes
                    self.show_hitboxes = not self.show_hitboxes
                elif event.key == pg.K_f:  # Afficher le menu de triche
                    self.show_cheats_menu = not self.show_cheats_menu

    def ia_take_turn(self, balle):
        """
        Fait jouer l'IA en mode solo.
        
        Args:
            balle (Balle): Instance de la balle
        """
        if balle.shooting_mode and not balle.flying:
            angle = random.randint(90, 150)
            strength = random.randint(30, 70)
            balle.shoot(angle, strength)
            balle.flying = True
            balle.shooting_mode = False
            self.switch_turn()

    def sync_game_state(self, joueur, balle, terrain):
        """
        Synchronise l'état du jeu entre client et serveur.
        
        Args:
            joueur (Joueur): Instance du joueur
            balle (Balle): Instance de la balle
            terrain (Terrain): Instance du terrain
        """
        if self.is_online and self.connection_established:
            try:
                # Création du dictionnaire d'état
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
                
                # Envoi selon le rôle
                if self.is_server and self.current_player == 0:
                    self.serveur.send(f"STATE:{game_state_json}")
                elif self.is_client and self.current_player == 1:
                    self.client.send(f"STATE:{game_state_json}")
            except Exception as e:
                print(f"Erreur lors de la synchronisation: {e}")
                self.connection_established = False

    def receive_game_state(self, joueur, balle, terrain):
        """
        Reçoit et applique l'état du jeu depuis le réseau.
        
        Args:
            joueur (Joueur): Instance du joueur
            balle (Balle): Instance de la balle
            terrain (Terrain): Instance du terrain
        """
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
        """
        Met à jour l'affichage et la logique du jeu.
        
        Args:
            fenetre (Surface): Fenêtre du jeu
            background_image (Surface): Image de fond
            joueur (Joueur): Instance du joueur
            terrain (Terrain): Instance du terrain
            balle (Balle): Instance de la balle
        """
        fenetre.fill((255, 255, 255))

        if self.game_started:
            remaining_time = self.get_remaining_time()

            if remaining_time == 0:  # Partie terminée
                fenetre.blit(background_image, (0, 0))
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (640, 300), 50, (255, 255, 255))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (640, 360), 50, (255, 255, 255))
                self.draw_button(fenetre, "Menu Principal", self.go_back_button_rect, (255, 0, 0), (200, 0, 0))
            else:  # Partie en cours
                terrain.afficherTerrain(fenetre)
                terrain.afficherAssets(fenetre)

                # Gestion du spawn des assets
                current_time = time.time()
                if current_time - self.last_asset_spawn_time > self.asset_spawn_interval:
                    terrain.spawn_asset()
                    self.last_asset_spawn_time = current_time

                # Positionnement de la balle avant tir
                if balle.shooting_mode and not balle.dragging and not balle.flying:
                    balle.position = [joueur.position[0], joueur.position[1] - 30]
                    balle.rect.topleft = balle.position

                # Affichage des éléments
                joueur.draw(fenetre)
                balle.update_position(fenetre.get_width(), fenetre.get_height())
                balle.draw(fenetre)

                # Synchronisation réseau
                if self.is_online and self.connection_established:
                    if self.current_player == 0 and self.is_server:
                        self.sync_game_state(joueur, balle, terrain)
                    elif self.current_player == 1 and self.is_client:
                        self.sync_game_state(joueur, balle, terrain)
                    else:
                        self.receive_game_state(joueur, balle, terrain)

                # Affichage des informations
                self.draw_text(fenetre, f"Score Joueur 1: {self.score[0]}", (200, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Score Joueur 2: {self.score[1]}", (1080, 40), 30, (0, 0, 0))
                self.draw_text(fenetre, f"Temps: {int(remaining_time)}s", (640, 50), 50, (0, 0, 0))
                self.draw_text(fenetre, f"Tour: Joueur {self.current_player + 1}", (640, 80), 30, (0, 0, 0))

                # Affichage spécifique en ligne
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

                # Instructions de tir
                if balle.shooting_mode and not balle.flying:
                    self.draw_text(fenetre, "Clic gauche pour tirer", (640, 200), 24, (0, 0, 0))
                    self.draw_text(fenetre, "Maintenez pour ajuster la puissance", (640, 230), 24, (0, 0, 0))

                # Gestion des collisions et effets
                self.check_panier_collision(terrain, balle)
                self.check_asset_collision(balle, terrain)  
                self.update_effects(balle)  
                terrain.afficherPanier(fenetre)

                # Affichage du "+1" si nécessaire
                if self.one_position and current_time - self.one_display_time < 1:
                    self.draw_one(fenetre)
                else:
                    self.one_position = None

                # Affichage des hitboxes en mode debug
                if self.show_hitboxes:
                    self.draw_hitboxes(fenetre, terrain, balle)
        else:  # Menus avant le jeu
            fenetre.blit(background_image, (0, 0))
            if self.selecting_game_mode:
                # Menu sélection durée
                self.draw_button(fenetre, "10s", self.game_mode_10s_button_rect, (255, 0, 0), (200, 0, 0))
                self.draw_button(fenetre, "30s", self.game_mode_30s_button_rect, (255, 165, 0), (200, 130, 0))
                self.draw_button(fenetre, "60s", self.game_mode_60s_button_rect, (0, 255, 0), (0, 200, 0))
                self.draw_button(fenetre, "Retour", self.go_back_button_rect, (0, 0, 255), (0, 0, 200))
            elif self.is_multiplayer == False and self.is_online == False:
                # Menu principal hors ligne
                self.draw_button(fenetre, "Single Player", self.single_player_button_rect, (0, 255, 0), (0, 200, 0))
                self.draw_button(fenetre, "Multiplayer", self.multiplayer_button_rect, (0, 0, 255), (0, 0, 200))
                self.draw_button(fenetre, "Online", self.online_button_rect, (255, 0, 0), (200, 0, 0))
            elif self.is_online and not self.is_server and not self.is_client:
                # Menu choix serveur/client
                self.draw_button(fenetre, "Server", self.sever_button_rect, (255, 0, 0), (200, 0, 0))
                self.draw_button(fenetre, "Client", self.client_button_rect, (0, 255, 0), (0, 200, 0))
            elif self.waiting_for_server and not self.selecting_game_mode:
                # Attente de connexion
                if self.is_client:
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

        # Affichage du menu de triche si activé
        if self.show_cheats_menu:
            self.draw_cheats_menu(fenetre)

    def check_panier_collision(self, terrain, balle):
        """
        Vérifie les collisions avec le panier et gère les scores.
        
        Args:
            terrain (Terrain): Instance du terrain
            balle (Balle): Instance de la balle
        """
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        top_hitbox = pg.Rect(panier_rect_full.left, panier_rect_full.top, panier_rect_full.width, hitbox_height)
        side_hitbox_left = pg.Rect(panier_rect_full.left, panier_rect_full.top + hitbox_height, hitbox_height, panier_rect_full.height - hitbox_height)
        side_hitbox_right = pg.Rect(panier_rect_full.right - hitbox_height, panier_rect_full.top + hitbox_height, hitbox_height, panier_rect_full.height - hitbox_height)
        current_time = time.time()

        # Collision avec le haut du panier
        if self.check_collision(balle_rect, top_hitbox) and (current_time - self.last_hoop_time) > self.cooldown:
            terrain.positionPanier = terrain.genererPositionPanier()
            self.last_hoop_time = current_time
            points = 2 if "double_points" in self.active_effects else 1
            self.score[self.current_player] += points
            
            # Synchronisation en ligne
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

        # Collision avec les côtés du panier
        if self.check_collision(balle_rect, side_hitbox_left) or self.check_collision(balle_rect, side_hitbox_right):
            balle.velocity_x = -balle.velocity_x  # Rebond

        # Vérification que le panier est dans le terrain
        if not self.is_hitbox_within_terrain(panier_rect_full, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()
            if self.is_online and self.connection_established:
                try:
                    if self.is_server:
                        self.serveur.send(f"HOOP:{terrain.positionPanier}")
                    elif self.is_client:
                        self.client.send(f"HOOP:{terrain.positionPanier}")
                except Exception as e:
                    print(f"Erreur lors de la synchronisation du panier: {e}")

    def check_asset_collision(self, balle, terrain):
        """
        Vérifie les collisions avec les assets et applique leurs effets.
        
        Args:
            balle (Balle): Instance de la balle
            terrain (Terrain): Instance du terrain
        """
        balle_rect = balle.rect
        for asset, position in list(terrain.asset_positions.items()):
            asset_rect = pg.Rect(position[0], position[1], 50, 50)
            if balle_rect.colliderect(asset_rect):
                self.apply_asset_effect(asset, balle)
                del terrain.asset_positions[asset]
                del terrain.asset_timers[asset]

    def apply_asset_effect(self, asset, balle):
        """
        Applique l'effet d'un asset.
        
        Args:
            asset (str): Type d'asset ("double_points", "double_speed", etc.)
            balle (Balle): Instance de la balle
        """
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
        """
        Met à jour les effets actifs et les désactive si expirés.
        
        Args:
            balle (Balle): Instance de la balle
        """
        current_time = time.time()
        if "double_speed" in self.active_effects and current_time > self.active_effects["double_speed"]:
            balle.speed /= 2  # Retour à la vitesse normale
            del self.active_effects["double_speed"]
        if "low_gravity" in self.active_effects and current_time > self.active_effects["low_gravity"]:
            balle.gravity *= 2  # Retour à la gravité normale
            del self.active_effects["low_gravity"]

    def draw_hitboxes(self, fenetre, terrain, balle):
        """
        Dessine les hitboxes pour le débogage.
        
        Args:
            fenetre (Surface): Fenêtre du jeu
            terrain (Terrain): Instance du terrain
            balle (Balle): Instance de la balle
        """
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)

        if not self.is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()

        pg.draw.rect(fenetre, (255, 0, 0), balle_rect, 2)  # Rouge pour la balle
        pg.draw.rect(fenetre, (0, 255, 0), panier_rect, 2)  # Vert pour le panier

    def reset_game(self, joueur, terrain, balle):
        """
        Réinitialise complètement le jeu et nettoie les connexions.
        
        Args:
            joueur (Joueur): Instance du joueur
            terrain (Terrain): Instance du terrain
            balle (Balle): Instance de la balle
        """
        # Nettoyage des connexions réseau
        if self.serveur:
            self.serveur.cleanup()
            self.serveur = None
        if self.client:
            self.client.cleanup()
            self.client = None
        
        # Réinitialisation de l'état du jeu
        joueur.position = [640, 600]  # Position par défaut du joueur
        terrain.positionPanier = terrain.genererPositionPanier()
        balle.position = [joueur.position[0], joueur.position[1] - 30]
        balle.rect.topleft = balle.position
        balle.velocity_x = 0
        balle.velocity_y = 0
        balle.shooting_mode = True
        balle.flying = False
        self.reset()
        
        # Réinitialisation de l'état réseau
        self.is_online = False
        self.is_server = False
        self.is_client = False
        self.connection_established = False

    def createServer(self):
        """
        Crée et démarre un serveur pour le mode en ligne.
        
        Returns:
            Serveur: Instance du serveur créé ou None en cas d'erreur
        """
        try:
            # Nettoyage d'un éventuel serveur existant
            if self.serveur:
                self.serveur.cleanup()
            
            self.serveur = serveur.Serveur()
            print("Serveur créé avec succès")
            # Lancement dans un thread séparé
            server_thread = threading.Thread(target=self.serveur.run)
            server_thread.daemon = True  # Le thread s'arrête avec le programme
            server_thread.start()
            self.connection_established = True
            self.waiting_for_server = False
            self.selecting_game_mode = True
            return self.serveur
        except Exception as e:
            print(f"Erreur lors de la création du serveur: {e}")
            self.connection_established = False
            return None
    
    def createClient(self):
        """
        Crée et connecte un client pour le mode en ligne.
        
        Returns:
            Client: Instance du client créé ou None en cas d'erreur
        """
        try:
            # Nettoyage d'un éventuel client existant
            if self.client:
                self.client.cleanup()
            
            self.client = client.Client()
            print("Client créé avec succès")
            if not self.client.connected:
                print("Impossible de se connecter au serveur")
                self.connection_established = False
                return None
            self.connection_established = True
            self.waiting_for_server = False
            self.selecting_game_mode = True
            return self.client
        except Exception as e:
            print(f"Erreur lors de la création du client: {e}")
            self.connection_established = False
            return None

    def getPlayer(self):
        """
        Retourne le joueur actuel.
        
        Returns:
            int: Index du joueur actuel (0 ou 1)
        """
        return self.current_player

    def set_asset_spawn_interval(self, interval):
        """
        Définit l'intervalle de spawn des assets.
        
        Args:
            interval (float): Intervalle en secondes
        """
        self.asset_spawn_interval = interval

    def draw_cheats_menu(self, fenetre):
        """
        Dessine le menu des triches.
        
        Args:
            fenetre (Surface): Fenêtre du jeu
        """
        self.draw_button(fenetre, "Double Points", self.double_points_button_rect, (0, 255, 0), (0, 200, 0))
        self.draw_button(fenetre, "Double Speed", self.double_speed_button_rect, (0, 0, 255), (0, 0, 200))
        self.draw_button(fenetre, "Low Gravity", self.low_gravity_button_rect, (255, 165, 0), (200, 130, 0))
        self.draw_button(fenetre, "Plus One", self.plus_one_button_rect, (255, 0, 255), (200, 0, 200))

    def toggle_cheat(self, cheat, balle):
        """
        Active/désactive une triche.
        
        Args:
            cheat (str): Nom de la triche
            balle (Balle): Instance de la balle
        """
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
        """
        Dessine l'effet "+1" à l'écran.
        
        Args:
            fenetre (Surface): Fenêtre du jeu
        """
        fenetre.blit(self.one_image, self.one_position)