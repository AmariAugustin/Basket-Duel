import pygame as pg
import random
import time

class Terrain:
    """
    Classe représentant le terrain de jeu.
    Gère l'affichage des éléments du terrain, des assets, du panier et de la balle.
    """

    def __init__(self):
        """
        Initialise les dimensions du terrain, les positions des éléments
        et charge les assets nécessaires.
        """
        self.largeur = 1280  # Largeur du terrain
        self.hauteur = 720  # Hauteur du terrain
        self.positionPanier = self.genererPositionPanier()  # Position initiale du panier

        # Chargement des images du terrain et des éléments
        self.terrainAsset = pg.image.load("assets/terrain.png")
        self.balle = pg.image.load("assets/basketball.png")
        self.balle = pg.transform.scale(self.balle, (50, 50))  # Redimensionne la balle
        self.panier = pg.image.load("assets/panier.png")
        self.panier = pg.transform.scale(self.panier, (250, 250))  # Redimensionne le panier
        self.one_image = pg.image.load("assets/one.png")
        self.one_image = pg.transform.scale(self.one_image, (75, 75))  # Redimensionne l'image "one"

        # Chargement des assets spéciaux
        self.assets = {
            "double_points": pg.image.load("assets/double_points.png"),
            "double_speed": pg.image.load("assets/double_speed.png"),
            "low_gravity": pg.image.load("assets/low_gravity.png"),
            "plus_one": pg.image.load("assets/plus_one.png")
        }
        # Redimensionne tous les assets à une taille de 75x75 pixels
        for key in self.assets:
            self.assets[key] = pg.transform.scale(self.assets[key], (75, 75))

        # Dictionnaires pour stocker les positions et les timers des assets
        self.asset_positions = {}
        self.asset_timers = {}

    def genererPositionPanier(self):
        """
        Génère une position aléatoire pour le panier.

        Returns:
            list: Une liste contenant les coordonnées [x, y] du panier.
        """
        return [random.randint(640, self.largeur - 100), random.randint(200, self.hauteur - 300)]

    def genererPositionAsset(self):
        """
        Génère une position aléatoire pour un asset.

        Returns:
            list: Une liste contenant les coordonnées [x, y] de l'asset.
        """
        return [random.randint(0, self.largeur - 50), random.randint(0, self.hauteur - 50)]

    def spawn_asset(self):
        """
        Fait apparaître un asset aléatoire sur le terrain.
        Stocke sa position et le moment où il a été généré.
        """
        asset_name = random.choice(list(self.assets.keys()))  # Choisit un asset aléatoire
        self.asset_positions[asset_name] = self.genererPositionAsset()  # Génère sa position
        self.asset_timers[asset_name] = time.time()  # Enregistre le temps de spawn

    def afficherTerrain(self, fenetre):
        """
        Affiche le terrain sur la fenêtre.

        Args:
            fenetre (pygame.Surface): La surface où afficher le terrain.
        """
        fenetre.blit(self.terrainAsset, (0, 0))

    def afficherBalle(self, fenetre, position):
        """
        Affiche la balle à une position donnée.

        Args:
            fenetre (pygame.Surface): La surface où afficher la balle.
            position (tuple): Les coordonnées (x, y) de la balle.
        """
        fenetre.blit(self.balle, position)

    def afficherPanier(self, fenetre):
        """
        Affiche le panier à sa position actuelle.

        Args:
            fenetre (pygame.Surface): La surface où afficher le panier.
        """
        fenetre.blit(self.panier, self.positionPanier)

    def afficherAssets(self, fenetre):
        """
        Affiche les assets sur le terrain et les supprime après 3 secondes.

        Args:
            fenetre (pygame.Surface): La surface où afficher les assets.
        """
        current_time = time.time()  # Temps actuel
        for asset, position in list(self.asset_positions.items()):
            # Vérifie si l'asset est présent depuis plus de 3 secondes
            if current_time - self.asset_timers[asset] > 3:
                del self.asset_positions[asset]  # Supprime l'asset de la liste
                del self.asset_timers[asset]  # Supprime son timer
            else:
                fenetre.blit(self.assets[asset], position)  # Affiche l'asset

    def afficherOne(self, fenetre, position):
        """
        Affiche l'image "one" à une position donnée.

        Args:
            fenetre (pygame.Surface): La surface où afficher l'image.
            position (tuple): Les coordonnées (x, y) de l'image.
        """
        fenetre.blit(self.one_image, position)