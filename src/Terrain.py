import random
import pygame as pg
import os
import time

# Chargement des fichiers
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourceFileDir)

class Terrain:
    def __init__(self):
        self.largeur = 1280
        self.hauteur = 720
        self.positionPanier = self.genererPositionPanier()
        self.terrainAsset = pg.image.load("assets/terrain.png")
        self.balle = pg.image.load("assets/basketball.png")
        self.balle = pg.transform.scale(self.balle, (50, 50))
        self.panier = pg.image.load("assets/panier.png")
        self.panier = pg.transform.scale(self.panier, (250, 250))

        # Define assets
        self.assets = {
            "double_points": pg.image.load("assets/double_points.png"),
            "double_speed": pg.image.load("assets/double_speed.png"),
            "low_gravity": pg.image.load("assets/low_gravity.png")
        }
        self.asset_positions = {}
        self.asset_timers = {}

    def genererPositionPanier(self):
        return [random.randint(640, self.largeur - 100), random.randint(200, self.hauteur - 300)]

    def genererPositionAsset(self):
        return [random.randint(0, self.largeur - 50), random.randint(0, self.hauteur - 50)]

    def spawn_asset(self):
        asset_name = random.choice(list(self.assets.keys()))
        self.asset_positions[asset_name] = self.genererPositionAsset()
        self.asset_timers[asset_name] = time.time()

    def afficherTerrain(self, fenetre):
        fenetre.blit(self.terrainAsset, (0, 0))

    def afficherBalle(self, fenetre, position):
        fenetre.blit(self.balle, position)

    def afficherPanier(self, fenetre):
        fenetre.blit(self.panier, self.positionPanier)

    def afficherAssets(self, fenetre):
        current_time = time.time()
        for asset, position in list(self.asset_positions.items()):
            if current_time - self.asset_timers[asset] > 3:
                del self.asset_positions[asset]
                del self.asset_timers[asset]
            else:
                fenetre.blit(self.assets[asset], position)