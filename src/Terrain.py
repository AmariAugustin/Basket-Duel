import random
import pygame as pg 
import os 

#Chargement des fichiers
sourceFileDir=os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

class Terrain:
    def __init__(self):  
        self.largeur = 1000
        self.hauteur = 1000
        self.positionPanier = None  
        self.terrainAsset = pg.image.load("assets/terrain.png")

    def genererPositionPanier(self):  
        self.positionPanier = [random.randint(0, 200)]
        return self.positionPanier
    
    # def genererPositionJoueur(self):

    def afficherTerrain(self,fenetre):
        fenetre.blit(self.terrainAsset, (0, 0))

# Test
terrain = Terrain()
print(terrain.genererPositionPanier())  
