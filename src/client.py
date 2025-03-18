import socket

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self,ip,port):
        self.s.connect((ip,port))

    def send(self,msg):
        self.s.send(msg.encode())

    def receive(self):
        return self.s.recv(9999999)
    
    def close(self):
        self.s.close()

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

