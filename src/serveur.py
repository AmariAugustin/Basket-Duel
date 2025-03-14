import socket

class Serveur:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        print("Connexion...")
        self.s.bind(("localhost", 1111))
        self.s.listen()
        self.clientsocket, address = self.s.accept()
        print(f"Connection de {address} établie")
    
    def send(self,msg):
        self.clientsocket.send(msg.encode())
    
    def receive(self):
        return self.clientsocket.recv(9999999)
    
    def close(self):
        self.clientsocket.close()
        self.s.close()

    def controleBalle(self, balle, joueur, msg):
        if (msg == "droite"):
            joueur.position[0] += 10
        elif (msg == "gauche"):
            joueur.position[0] -= 10
        elif (msg == "haut"):
            joueur.position[1] -= 10
        elif (msg == "bas"):
            joueur.position[1] += 10
        elif (msg == "tir"):   
            balle.shooting_mode = False
            balle.flying = True
            balle.velocity_x = 10
            balle.velocity_y = 10
            balle.position[0] = joueur.position[0]
            balle.position[1] = joueur.position[1] - 30
            balle.rect.topleft = balle.position
  
s = Serveur()

s.run()
while True:
   print(s.receive())
   msg = input("Entrez un message: ")
   s.send(msg)
   if msg == "exit":
       break
s.close()