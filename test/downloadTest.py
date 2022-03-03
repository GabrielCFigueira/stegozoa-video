import socket
import time
import signal

def sigInt_handler(signum,frame):
    global start, data
    end = time.time()
    print("data(bits): " + str(data) + " time: " + str(end - start))
    print("Throughput(bits/s): " + str(data / (end - start)))
    exit(0)



socketPath = "/tmp/stegozoa_client_socket"

signal.signal(signal.SIGINT,sigInt_handler)

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socketPath)
    
start = time.time()
data = 0

while True:
    message = client.recv(4096)
    data += len(message) * 8
    client.send(bytes("Hello" * 1000, 'ascii')) #so both endpoints are sending
