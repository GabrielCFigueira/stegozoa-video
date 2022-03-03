import socket
import time
import signal

def sigInt_handler(signum,frame):
    global rtt

    total = 0
    for r in rtt:
        total += r
        print("RTT: " + str(r))


    print("Average RTT: " + str(total / len(rtt)))
    exit(0)

socketPath = "/tmp/stegozoa_client_socket"
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socketPath)

signal.signal(signal.SIGINT,sigInt_handler)

rtt = []
for i in range(20):
    start = time.time()
    client.send(bytes("Hello", 'ascii'))
    message = client.recv(1024)
    end = time.time()
    rtt += [end - start]

while True:
    time.sleep(10)

