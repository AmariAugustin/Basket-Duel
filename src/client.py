import socket
import time
import json

class Client:
    """
    Classe Client pour gérer la connexion et la communication avec un serveur.
    """

    def __init__(self):
        """
        Initialise le client, charge la configuration et tente de se connecter au serveur.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket
        self.connected = False  # Indique si le client est connecté au serveur
        self.buffer = ""  # Tampon pour stocker les données reçues partiellement
        self.config = self.load_config()  # Chargement de la configuration
        self.connect()  # Connexion au serveur

    def load_config(self):
        """
        Charge la configuration du client à partir d'un fichier texte.

        Returns:
            dict: Un dictionnaire contenant l'adresse IP et le port du serveur.
        """
        config = {}
        try:
            # Lecture du fichier de configuration
            with open('client_config.txt', 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    config[key] = value
            return config
        except Exception as e:
            # En cas d'erreur, retourne une configuration par défaut
            print(f"Erreur lors de la lecture du fichier de configuration: {e}")
            return {"ip": "localhost", "port": 1111}

    def connect(self):
        """
        Tente de se connecter au serveur en utilisant les informations de configuration.
        """
        try:
            # Connexion au serveur
            self.s.connect((self.config["ip"], int(self.config["port"])))
            self.connected = True
            print(f"Connecté au serveur {self.config['ip']}:{self.config['port']}")
        except ConnectionRefusedError:
            # Si le serveur n'est pas disponible
            print("Serveur non disponible. Assurez-vous que le serveur est en cours d'exécution.")
            self.connected = False
        except Exception as e:
            # Gestion des autres erreurs de connexion
            print(f"Erreur de connexion au serveur: {e}")
            self.connected = False

    def send(self, msg):
        """
        Envoie un message au serveur.

        Args:
            msg (str): Le message à envoyer.

        Returns:
            bool: True si l'envoi a réussi, False sinon.
        """
        if not self.connected:
            print("Non connecté au serveur")
            return False
        try:
            # Envoi du message au serveur
            self.s.send(f"{msg}\n".encode())
            return True
        except Exception as e:
            # Gestion des erreurs d'envoi
            print(f"Erreur lors de l'envoi du message: {e}")
            self.connected = False
            return False

    def receive(self):
        """
        Reçoit un message du serveur.

        Returns:
            str | int | None: Le message reçu, ou None si aucune donnée n'est disponible.
        """
        if not self.connected:
            print("Non connecté au serveur")
            return None
        try:
            # Réception des données du serveur
            data = self.s.recv(4096)
            if not data:
                # Si la connexion est fermée par le serveur
                print("Connexion fermée par le serveur")
                self.connected = False
                return None

            self.buffer += data.decode()  # Ajout des données reçues au tampon
            
            # Découpage des messages dans le tampon
            messages = self.buffer.split('\n')
            if len(messages) > 1:
                self.buffer = messages[-1]  # Conserve les données incomplètes
                
                # Traitement des messages complets
                for msg in messages[:-1]:
                    if msg.startswith("STATE:"):
                        return msg
                    elif msg.startswith("SCORE:"):
                        return int(msg[6:])
                    elif msg.startswith("HOOP:"):
                        return eval(msg[5:])
            
            return None
        except Exception as e:
            # Gestion des erreurs de réception
            print(f"Erreur lors de la réception du message: {e}")
            self.connected = False
            return None
    
    def cleanup(self):
        """
        Nettoie les ressources utilisées par le client.
        """
        try:
            if self.s:
                self.s.close()  # Fermeture du socket
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Réinitialisation du socket
            self.buffer = ""  # Réinitialisation du tampon
        except Exception as e:
            # Gestion des erreurs de nettoyage
            print(f"Erreur lors du nettoyage: {e}")
    
    def close(self):
        """
        Ferme la connexion et nettoie les ressources.
        """
        self.cleanup()
        self.connected = False

