import pygame as pg
import sys
from Joueur import Joueur
from Terrain import Terrain
from balle import Balle
from partie import Partie
import os

pg.init()
clock = pg.time.Clock()

# Chargement des fichiers
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

# Écran
pg.display.set_caption("Basket Duel")
fenetre = pg.display.set_mode((1280, 720))

# Chargement des ressources
background_image = pg.image.load("assets/levon.png")

# Initialisation des objets du jeu
terrain = Terrain()
joueur = Joueur()
partie = Partie()

# Initialisation de la balle en mode shooting
balle = Balle([joueur.position[0], joueur.position[1] - 30], speed=2)
balle.shooting_mode = True
balle.flying = False

# Importation d'image
logo = pg.image.load("assets/logo.png")
pg.display.set_icon(logo)

# Boucle principale du jeu
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:  # ferme le jeu si fenêtre fermée
            pg.quit()
            sys.exit()
        
        partie.handle_event(event, joueur, terrain, balle)
    
    # Mise à jour et affichage du jeu
    partie.update(fenetre, background_image, joueur, terrain, balle)
    
    # Mise à jour de l'écran
    pg.display.flip()
    clock.tick(60)