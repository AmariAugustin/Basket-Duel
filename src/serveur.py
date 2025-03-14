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