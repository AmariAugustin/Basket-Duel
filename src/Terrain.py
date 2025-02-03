import random

class Terrain:
    def __init__(self):  
        self.largeur = 1000
        self.hauteur = 1000
        self.positionPanier = None  

    def genererPositionPanier(self):  
        self.positionPanier = [random.randint(0, 200)]
        return self.positionPanier
    
    # def genererPositionJoueur(self):

# Test
terrain = Terrain()
print(terrain.genererPositionPanier())  
