import socket
import time
import json

class Serveur:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientsocket = None
        self.address = None
        self.buffer = ""

    def run(self):
        print("Connexion...")
        try:
            # Try to bind to the port
            self.s.bind(("localhost", 1111))
            self.s.listen()
            print("Serveur en attente de connexion...")
            self.clientsocket, self.address = self.s.accept()
            print(f"Connection de {self.address} établie")
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print("Le port est déjà utilisé. Tentative de nettoyage...")
                self.cleanup()
                time.sleep(1)  # Wait a bit before retrying
                self.run()  # Retry the connection
            else:
                print(f"Erreur lors de la création du serveur: {e}")
                raise
    
    def send(self, msg):
        if self.clientsocket:
            try:
                # Ajout d'un marqueur de fin de message
                self.clientsocket.send(f"{msg}\n".encode())
            except Exception as e:
                print(f"Erreur lors de l'envoi du message: {e}")
    
    def receive(self):
        if self.clientsocket:
            try:
                # Réception des données
                data = self.clientsocket.recv(4096)
                if not data:
                    print("Connexion fermée par le client")
                    return None

                # Ajout des données au buffer
                self.buffer += data.decode()
                
                # Traitement des messages complets
                messages = self.buffer.split('\n')
                if len(messages) > 1:
                    # Garde le dernier message potentiellement incomplet dans le buffer
                    self.buffer = messages[-1]
                    
                    # Traite tous les messages complets
                    for msg in messages[:-1]:
                        if msg.startswith("STATE:"):
                            return msg
                        elif msg.startswith("SCORE:"):
                            return int(msg[6:])
                        elif msg.startswith("HOOP:"):
                            return eval(msg[5:])
                
                return None
            except Exception as e:
                print(f"Erreur lors de la réception du message: {e}")
                return None
        return None
    
    def cleanup(self):
        try:
            if self.clientsocket:
                self.clientsocket.close()
                self.clientsocket = None
            if self.s:
                self.s.close()
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.buffer = ""
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
    
    def close(self):
        self.cleanup()
  
s = Serveur()
"""
s.run()
while True:
   print(s.receive())
   msg = input("Entrez un message: ")
   s.send(msg)
   if msg == "exit":
       break
s.close()
"""