import pygame as pg
import random

class Joueur:
    """
    Classe représentant un joueur dans le jeu. 
    Le joueur est affiché à une position aléatoire ou spécifiée sur l'écran.
    """

    def __init__(self, position=None):
        """
        Initialise un joueur avec une image et une position.

        Args:
            position (list | tuple | None): La position initiale du joueur sous forme de liste [x, y].
                                            Si aucune position n'est fournie, une position aléatoire est générée.
        """
        self.joueur_image = pg.transform.scale(pg.image.load("assets/player.png"), (100, 100))  # Chargement et redimensionnement de l'image du joueur
        self.rect = self.joueur_image.get_rect()  # Obtient le rectangle de l'image pour la gestion des collisions
        if position is None:
            position = self.genererPositionJoueur()  # Génère une position aléatoire si aucune n'est fournie
        self.position = position
        self.rect.topleft = self.position  # Définit la position du rectangle

    def genererPositionJoueur(self):
        """
        Génère une position aléatoire pour le joueur.

        Returns:
            list: Une liste contenant les coordonnées [x, y] de la position aléatoire.
        """
        return [random.randint(0, 640), random.randint(536, 720 - self.rect.height)]  # Position aléatoire dans une zone définie

    def draw(self, fenetre):
        """
        Dessine le joueur sur la fenêtre du jeu.

        Args:
            fenetre (pygame.Surface): La surface de la fenêtre où le joueur sera dessiné.
        """
        fenetre.blit(self.joueur_image, self.position)  # Affiche l'image du joueur à sa position actuelle
