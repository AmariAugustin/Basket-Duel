import pygame as pg
import sys
from Joueur import *
from Terrain import *
import os

pg.init()
clock = pg.time.Clock()

#Chargement des fichiers
sourceFileDir=os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)
#ecran
pg.display.set_caption("Basket Duel")
fenetre = pg.display.set_mode((1280, 720))

#importabtion des images
 
terrain = Terrain()
balle_position = (100, 100)

def check_collision(balle_rect,panier_rect):
    return balle_rect.colliderect(panier_rect)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    terrain.afficherTerrain(fenetre)
    terrain.afficherBalle(fenetre, balle_position)
    
    balle_rect = terrain.balle.get_rect(topleft=balle_position)
    panier_rect = terrain.panier.get_rect(topleft=terrain.positionPanier)
    
    if check_collision(balle_rect, panier_rect):
        terrain.positionPanier = terrain.genererPositionPanier() 
    
    terrain.afficherPanier(fenetre)
    pg.display.flip()
    clock.tick(60)


