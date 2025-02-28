import pygame as pg 
import os 

#Chargement des fichiers
sourceFileDir=os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

class Joueur:
    def __init__(self):
        self.assetJoueur = pg.image.load("assets/joueur.png")
    
    def afficherJoueur(self,fenetre):
        fenetre.blit(self.assetJoueur, (0, 0)) # a la place de 0, 0 crée une variable pour la position du joueur
