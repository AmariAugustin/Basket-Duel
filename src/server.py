import socket
import threading
import time
import json
import os

class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.connected = False
        self.buffer = ""
        self.config = self.load_config()
        self.bind()

    def load_config(self):
        config = {}
        try:
            with open('server_config.txt', 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    config[key] = value
            return config
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de configuration: {e}")
            return {"ip": "localhost", "port": 1111}

    def bind(self):
        try:
            self.s.bind((self.config["ip"], int(self.config["port"])))
            self.s.listen(5)
            self.connected = True
            print(f"Serveur démarré sur {self.config['ip']}:{self.config['port']}")
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")
            self.connected = False

    def run(self):
        while self.connected:
            try:
                client_socket, addr = self.s.accept()
                print(f"Connexion établie avec {addr}")
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except Exception as e:
                print(f"Erreur lors de la connexion: {e}")
                time.sleep(5)

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.buffer += data.decode('utf-8')
                if '\n' in self.buffer:
                    messages = self.buffer.split('\n')
                    self.buffer = messages[-1]
                    for message in messages[:-1]:
                        self.process_message(message)
            except Exception as e:
                print(f"Erreur lors de la réception des données: {e}")
                break

    def process_message(self, message):
        # Process the message
        pass

    def send_message(self, message):
        # Send a message to all clients
        for client in self.clients:
            client.sendall(message.encode('utf-8'))

    def stop(self):
        self.connected = False
        self.s.close()

if __name__ == "__main__":
    server = Server()
    server.run() 