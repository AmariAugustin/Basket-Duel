import socket
import threading
import time
import json
import os

class Server:
    """
    Classe représentant un serveur TCP simple.
    Permet de gérer les connexions des clients, de recevoir et d'envoyer des messages.
    """

    def __init__(self):
        """
        Initialise le serveur en configurant le socket, les variables nécessaires
        et en chargeant la configuration.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket
        self.clients = []  # Liste des clients connectés
        self.connected = False  # État de connexion du serveur
        self.buffer = ""  # Tampon pour les données reçues
        self.config = self.load_config()  # Chargement de la configuration
        self.bind()  # Liaison du serveur à l'adresse et au port

    def load_config(self):
        """
        Charge la configuration du serveur à partir d'un fichier texte.

        Returns:
            dict: Un dictionnaire contenant l'adresse IP et le port du serveur.
        """
        config = {}
        try:
            with open('server_config.txt', 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    config[key] = value
            return config
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de configuration: {e}")
            # Valeurs par défaut en cas d'erreur
            return {"ip": "localhost", "port": 1111}

    def bind(self):
        """
        Lie le serveur à l'adresse IP et au port spécifiés dans la configuration.
        Démarre l'écoute des connexions entrantes.
        """
        try:
            self.s.bind((self.config["ip"], int(self.config["port"])))
            self.s.listen(5)  # Le serveur peut gérer jusqu'à 5 connexions en attente
            self.connected = True
            print(f"Serveur démarré sur {self.config['ip']}:{self.config['port']}")
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")
            self.connected = False

    def run(self):
        """
        Boucle principale du serveur. Accepte les connexions des clients
        et démarre un thread pour gérer chaque client.
        """
        while self.connected:
            try:
                client_socket, addr = self.s.accept()  # Accepte une connexion entrante
                print(f"Connexion établie avec {addr}")
                self.clients.append(client_socket)  # Ajoute le client à la liste
                # Démarre un thread pour gérer le client
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except Exception as e:
                print(f"Erreur lors de la connexion: {e}")
                time.sleep(5)  # Attente avant de réessayer

    def handle_client(self, client_socket):
        """
        Gère la communication avec un client spécifique.

        Args:
            client_socket (socket): Le socket du client connecté.
        """
        while True:
            try:
                data = client_socket.recv(1024)  # Reçoit des données du client
                if not data:
                    break  # Si aucune donnée n'est reçue, on quitte la boucle
                self.buffer += data.decode('utf-8')  # Ajoute les données au tampon
                if '\n' in self.buffer:  # Vérifie si un message complet est reçu
                    messages = self.buffer.split('\n')
                    self.buffer = messages[-1]  # Conserve les données incomplètes
                    for message in messages[:-1]:
                        self.process_message(message)  # Traite chaque message
            except Exception as e:
                print(f"Erreur lors de la réception des données: {e}")
                break

    def process_message(self, message):
        """
        Traite un message reçu d'un client.

        Args:
            message (str): Le message reçu.
        """
        # Logique de traitement du message (à implémenter)
        pass

    def send_message(self, message):
        """
        Envoie un message à tous les clients connectés.

        Args:
            message (str): Le message à envoyer.
        """
        for client in self.clients:
            try:
                client.sendall(message.encode('utf-8'))  # Envoie le message
            except Exception as e:
                print(f"Erreur lors de l'envoi du message: {e}")

    def stop(self):
        """
        Arrête le serveur en fermant toutes les connexions et le socket principal.
        """
        self.connected = False
        self.s.close()  # Ferme le socket principal

if __name__ == "__main__":
    # Point d'entrée principal du programme
    server = Server()  # Instancie le serveur
    server.run()  # Démarre le serveur