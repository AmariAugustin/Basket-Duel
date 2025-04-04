import socket
import time
import json

class Serveur:
    """
    Classe représentant un serveur TCP simple.
    Permet de gérer les connexions avec un client, d'envoyer et de recevoir des messages.
    """

    def __init__(self):
        """
        Initialise le serveur en configurant le socket et les variables nécessaires.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Réutilisation de l'adresse
        self.clientsocket = None  # Socket du client connecté
        self.address = None  # Adresse du client connecté
        self.buffer = ""  # Tampon pour les données reçues

    def run(self):
        """
        Démarre le serveur, attend une connexion client et l'accepte.
        En cas d'erreur, tente de nettoyer et de redémarrer.
        """
        print("Connexion...")
        try:
            # Liaison du serveur à l'adresse et au port
            self.s.bind(("localhost", 1111))
            self.s.listen()  # Le serveur écoute les connexions entrantes
            print("Serveur en attente de connexion...")
            self.clientsocket, self.address = self.s.accept()  # Accepte une connexion
            print(f"Connexion de {self.address} établie")
        except OSError as e:
            if e.errno == 48:  # Adresse déjà utilisée
                print("Le port est déjà utilisé. Tentative de nettoyage...")
                self.cleanup()  # Nettoyage des ressources
                time.sleep(1)  # Attente avant de réessayer
                self.run()  # Relance le serveur
            else:
                print(f"Erreur lors de la création du serveur: {e}")
                raise

    def send(self, msg):
        """
        Envoie un message au client connecté.

        Args:
            msg (str): Le message à envoyer.
        """
        if self.clientsocket:
            try:
                # Ajout d'un marqueur de fin de message pour délimiter les messages
                self.clientsocket.send(f"{msg}\n".encode())
            except Exception as e:
                print(f"Erreur lors de l'envoi du message: {e}")

    def receive(self):
        """
        Reçoit des messages du client connecté.

        Returns:
            str | int | None: Le message reçu ou une valeur extraite du message,
                              ou None si la connexion est fermée ou en cas d'erreur.
        """
        if self.clientsocket:
            try:
                # Réception des données du client
                data = self.clientsocket.recv(4096)
                if not data:
                    print("Connexion fermée par le client")
                    return None

                # Ajout des données reçues au tampon
                self.buffer += data.decode()

                # Découpage des messages complets dans le tampon
                messages = self.buffer.split('\n')
                if len(messages) > 1:
                    # Garde le dernier message incomplet dans le tampon
                    self.buffer = messages[-1]

                    # Traite tous les messages complets
                    for msg in messages[:-1]:
                        if msg.startswith("STATE:"):
                            return msg  # Retourne l'état sous forme de chaîne
                        elif msg.startswith("SCORE:"):
                            return int(msg[6:])  # Retourne le score sous forme d'entier
                        elif msg.startswith("HOOP:"):
                            return eval(msg[5:])  # Retourne une structure Python évaluée

                return None
            except Exception as e:
                print(f"Erreur lors de la réception du message: {e}")
                return None
        return None

    def cleanup(self):
        """
        Nettoie les ressources du serveur en fermant les connexions et en réinitialisant le socket.
        """
        try:
            if self.clientsocket:
                self.clientsocket.close()  # Ferme la connexion client
                self.clientsocket = None
            if self.s:
                self.s.close()  # Ferme le socket principal
                # Réinitialise le socket pour une nouvelle utilisation
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.buffer = ""  # Réinitialise le tampon
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")

    def close(self):
        """
        Ferme le serveur en nettoyant toutes les ressources.
        """
        self.cleanup()


# Exemple d'utilisation du serveur (commenté pour éviter une exécution directe)
s = Serveur()
"""
s.run()
while True:
   print(s.receive())  # Affiche les messages reçus
   msg = input("Entrez un message: ")  # Demande un message à envoyer
   s.send(msg)  # Envoie le message au client
   if msg == "exit":  # Quitte la boucle si le message est "exit"
       break
s.close()  # Ferme le serveur
"""