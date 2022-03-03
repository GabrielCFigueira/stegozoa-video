import socket
import time

socketPath = "/tmp/stegozoa_client_socket"

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socketPath)
    

while True:
    client.send(bytes("why are we still here... just to suffer?" * 100, 'ascii'))
