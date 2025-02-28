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
        self.positionPanier = self.genererPositionPanier()  
        self.terrainAsset = pg.image.load("assets/terrain.png")
        self.balle = pg.image.load("assets/basketball.png") 
        self.balle = pg.transform.scale(self.balle, (50, 50))
        self.panier = pg.image.load("assets/panier.png")
        self.panier = pg.transform.scale(self.panier, (250,250))
        
    def genererPositionPanier(self):  
        return [random.randint(0, self.largeur - 100), random.randint(0, self.hauteur - 100)]
    
    # def genererPositionJoueur(self):

    def afficherTerrain(self,fenetre):
        fenetre.blit(self.terrainAsset, (0, 0))

    def afficherBalle(self, fenetre, position):
        fenetre.blit(self.balle, position)
        
    def afficherPanier(self, fenetre):
        fenetre.blit(self.panier, self.positionPanier)
# Test
terrain = Terrain()
print(terrain.genererPositionPanier())
