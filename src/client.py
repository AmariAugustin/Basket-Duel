import socket
import time
import json

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.buffer = ""
        self.connect()

    def connect(self):
        try:
            self.s.connect(("localhost", 1111))
            self.connected = True
            print("Connecté au serveur")
        except ConnectionRefusedError:
            print("Serveur non disponible. Assurez-vous que le serveur est en cours d'exécution.")
            self.connected = False
        except Exception as e:
            print(f"Erreur de connexion au serveur: {e}")
            self.connected = False

    def send(self, msg):
        if not self.connected:
            print("Non connecté au serveur")
            return False
        try:
            self.s.send(f"{msg}\n".encode())
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
            self.connected = False
            return False

    def receive(self):
        if not self.connected:
            print("Non connecté au serveur")
            return None
        try:
            data = self.s.recv(4096)
            if not data:
                print("Connexion fermée par le serveur")
                self.connected = False
                return None

            self.buffer += data.decode()
            
            messages = self.buffer.split('\n')
            if len(messages) > 1:
                self.buffer = messages[-1]
                
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
            self.connected = False
            return None
    
    def cleanup(self):
        try:
            if self.s:
                self.s.close()
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.buffer = ""
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
    
    def close(self):
        self.cleanup()
        self.connected = False

"""
# Test
client = Client()

while True:
    msgR = client.receive()
    msg = input(msgR.decode())
    client.send(msg)
    if msg == "exit":
        break"
"""

