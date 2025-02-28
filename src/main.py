import pygame as pg
import sys
from Joueur import *
from Terrain import *
from balle import Balle
import os

pg.init()
clock = pg.time.Clock()

#Chargement des fichiers
sourceFileDir=os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)
#ecran
pg.display.set_caption("Basket Duel")
fenetre = pg.display.set_mode((1280, 720))

terrain = Terrain()
balle = Balle([100, 100], speed=2)

def check_collision(balle_rect, panier_rect):
    return balle_rect.colliderect(panier_rect)

def is_hitbox_within_terrain(hitbox, terrain_width, terrain_height):
    return (hitbox.left >= 0 and hitbox.right <= terrain_width and
            hitbox.top >= 0 and hitbox.bottom <= terrain_height)

show_hitboxes = False

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        balle.handle_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_j:
                show_hitboxes = not show_hitboxes
    
    terrain.afficherTerrain(fenetre)
    balle.update_position(fenetre.get_width(), fenetre.get_height())
    balle.draw(fenetre)
    
    # possibilité de montrer les hitbox
    if show_hitboxes:
        balle_rect = balle.rect
        panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
        # modification de l'hitbox panier
        hitbox_height = 50
        panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
        
        # si panier pas dans le terrain, le replace
        if not is_hitbox_within_terrain(panier_rect, terrain.largeur, terrain.hauteur):
            terrain.positionPanier = terrain.genererPositionPanier()
        #affichage hitbox
        pg.draw.rect(fenetre, (255, 0, 0), balle_rect, 2)  
        pg.draw.rect(fenetre, (0, 255, 0), panier_rect, 2)  
    
    # check les collisions
    balle_rect = balle.rect
    panier_rect_full = terrain.panier.get_rect(topleft=terrain.positionPanier)
    hitbox_height = 50
    panier_rect = pg.Rect(panier_rect_full.left, panier_rect_full.top + 10, panier_rect_full.width, hitbox_height)
    
    if check_collision(balle_rect, panier_rect):
        terrain.positionPanier = terrain.genererPositionPanier()
    
    terrain.afficherPanier(fenetre)
    pg.display.flip()
    clock.tick(60)
