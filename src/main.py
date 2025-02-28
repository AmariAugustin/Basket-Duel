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

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    terrain.afficherTerrain(fenetre)
    pg.display.flip()
    clock.tick(60)


