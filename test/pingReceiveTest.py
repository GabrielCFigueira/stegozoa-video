import socket
import time



socketPath = "/tmp/stegozoa_client_socket"


client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socketPath)
    

for i in range(20):
    message = client.recv(1024)
    client.send(bytes("World", 'ascii'))
