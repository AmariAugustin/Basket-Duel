import pygame as pg
import random

class Joueur:
    def __init__(self, position=None):#affiche joueur
        self.joueur_image = pg.transform.scale(pg.image.load("assets/player.png"), (100, 100))
        self.rect = self.joueur_image.get_rect()
        if position is None:
            position = self.genererPositionJoueur()
        self.position = position
        self.rect.topleft = self.position

    def genererPositionJoueur(self): #crée position joueur (comme panier)
        return [random.randint(0, 640), random.randint(536, 720 - self.rect.height)]

    def draw(self, fenetre): #dessine joueur
        fenetre.blit(self.joueur_image, self.position)
