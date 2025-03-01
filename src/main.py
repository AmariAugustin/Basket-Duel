import pygame as pg
import sys
from Joueur import Joueur
from Terrain import Terrain
from balle import Balle
from Partie import Partie
import os
import time
import random

pg.init()
clock = pg.time.Clock()

# Chargement des fichiers
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)
# ecran
pg.display.set_caption("Basket Duel")
fenetre = pg.display.set_mode((1280, 720))


background_image = pg.image.load("assets/levon.png")

#init du terrain,balle,joueur,partie
terrain = Terrain()
joueur = Joueur()
# Initialisez la balle avec le mode shooting activé par défaut
balle = Balle([joueur.position[0], joueur.position[1]], speed=2)
balle.shooting_mode = True  # Activez le mode shooting par défaut
partie = Partie()

#verifie les collisions pour les paniers
def check_collision(balle_rect, panier_rect):
    return balle_rect.colliderect(panier_rect)

#empeche de spawn en dehors de la map
def is_hitbox_within_terrain(hitbox, terrain_width, terrain_height):
    return (hitbox.left >= 0 and hitbox.right <= terrain_width and
            hitbox.top >= 0 and hitbox.bottom <= terrain_height)
    
#normalisation création bouton
def draw_button(surface, text, rect, color, hover_color):
    mouse_pos = pg.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pg.draw.rect(surface, hover_color, rect)
    else:
        pg.draw.rect(surface, color, rect)
    font = pg.font.Font(None, 36)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    
#normalisation création texte
def draw_text(surface, text, position, font_size, color):
    font = pg.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    surface.blit(text_surface, text_rect)

#redémarre la partie quand elle est finie
def reset_game():
    global joueur, terrain, balle, score, start_time, game_started, selecting_game_mode
    joueur = Joueur()
    terrain.positionPanier = terrain.genererPositionPanier()
    # Réinitialisez la balle à la position du joueur et en mode shooting
    balle = Balle([joueur.position[0], joueur.position[1]], speed=2)
    balle.shooting_mode = True
    score = 0
    start_time = time.time()
    game_started = False
    selecting_game_mode = False
    partie.reset()

#paramètres de base
show_hitboxes = False
last_hoop_time = 0
cooldown = 1  #cooldown entre chaque paniers (en s)
game_started = False
score = 0
start_time = time.time()
game_duration = 60  

# modes de jeu
single_player_button_rect = pg.Rect(540, 310, 200, 50)
multiplayer_button_rect = pg.Rect(540, 370, 200, 50)


game_mode_10s_button_rect = pg.Rect(540, 310, 200, 50)
game_mode_30s_button_rect = pg.Rect(540, 370, 200, 50)
game_mode_60s_button_rect = pg.Rect(540, 430, 200, 50)

go_back_button_rect = pg.Rect(540, 490, 200, 50)


selecting_game_mode = False
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:#ferme le jeu si fenetre fermée
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if not game_started and not selecting_game_mode:
                if single_player_button_rect.collidepoint(event.pos) or multiplayer_button_rect.collidepoint(event.pos):
                    selecting_game_mode = True
            elif selecting_game_mode:
                if game_mode_10s_button_rect.collidepoint(event.pos):
                    game_duration = 10
                    game_started = True
                    start_time = time.time()
                    selecting_game_mode = False
                elif game_mode_30s_button_rect.collidepoint(event.pos):
                    game_duration = 30
                    game_started = True
                    start_time = time.time()
                    selecting_game_mode = False
                elif game_mode_60s_button_rect.collidepoint(event.pos):
                    game_duration = 60
                    game_started = True
                    start_time = time.time()
                    selecting_game_mode = False
            elif game_started and remaining_time == 0:
                if go_back_button_rect.collidepoint(event.pos):
                    reset_game()
        if game_started:
            balle.handle_event(event, joueur.position)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_j:
                    show_hitboxes = not show_hitboxes
                # Supprimez la partie pour changer le mode de tir avec la touche 'u'
    
    fenetre.fill((255, 255, 255))
    
    if game_started:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, game_duration - elapsed_time)
        
        if remaining_time == 0:
            fenetre.blit(background_image, (0, 0))
            draw_text(fenetre, f"Score: {score}", (640, 360), 100, (255, 255, 255))
            draw_button(fenetre, "Menu Principal", go_back_button_rect, (255, 0, 0), (200, 0, 0))
        else:
            terrain.afficherTerrain(fenetre)
            
            # Si la balle est en mode shooting et n'est pas en train d'être traînée, attachez-la au joueur
            if balle.shooting_mode and not balle.dragging and not balle.flying:
                balle.position = [joueur.position[0], joueur.position[1] - 30]
                balle.rect.topleft = balle.position
            
            joueur.draw(fenetre)
            balle.update_position(fenetre.get_width(), fenetre.get_height())
            balle.draw(fenetre)
            
            draw_text(fenetre, f"Score: {score}", (640, 50), 50, (0, 0, 0))
            draw_text(fenetre, f"Temps: {int(remaining_time)}s", (1180, 50), 50, (0, 0, 0))
            
            if show_hitboxes:
                balle_rect = balle.rect
                panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
                hitbox_height = 50
                panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
                
                if not is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
                    terrain.positionPanier = terrain.genererPositionPanier()
                
                pg.draw.rect(fenetre, (255, 0, 0), balle_rect, 2)  
                pg.draw.rect(fenetre, (0, 255, 0), panier_rect, 2)  
            
            balle_rect = balle.rect
            panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
            hitbox_height = 50
            panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
            
            current_time = time.time()
            if check_collision(balle_rect, panier_rect) and (current_time - last_hoop_time) > cooldown:
                terrain.positionPanier = terrain.genererPositionPanier()
                last_hoop_time = current_time
                score += 1
                partie.score = score
                # Réinitialisez la balle en mode shooting après un panier
                balle.shooting_mode = True
                balle.flying = False
            
            if not is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
                terrain.positionPanier = terrain.genererPositionPanier()
            
            terrain.afficherPanier(fenetre)
    else:
        fenetre.blit(background_image, (0, 0))
        if selecting_game_mode:
            draw_button(fenetre, "10s", game_mode_10s_button_rect, (255, 0, 0), (200, 0, 0))
            draw_button(fenetre, "30s", game_mode_30s_button_rect, (255, 165, 0), (200, 130, 0))
            draw_button(fenetre, "60s", game_mode_60s_button_rect, (0, 255, 0), (0, 200, 0))
        else:
            draw_button(fenetre, "Single Player", single_player_button_rect, (0, 255, 0), (0, 200, 0))
            draw_button(fenetre, "Multiplayer", multiplayer_button_rect, (0, 0, 255), (0, 0, 200))
    
    pg.display.flip()
    clock.tick(60)