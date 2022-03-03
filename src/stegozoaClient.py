import libstegozoa

import os
import socket
import threading
import sys
import time
import signal

socketPath = "/tmp/stegozoa_client_socket"

def sigInt_handler(signum,frame):
    global socketPath
    os.remove(libstegozoa.encoderPipePath)
    os.remove(libstegozoa.decoderPipePath)
    os.remove(socketPath)
    exit(0)

def is_socket_closed(sock):
    try:
    # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except socket.error:
        return True # socket error
    except Exception as e:
        print("unexpected exception when checking if a socket is closed")
        return False
    return False


def newConnection():
    global mutex, server_socket
    mutex.acquire()
    if is_socket_closed(server_socket):
        server_socket, address = server.accept()
    mutex.release()


def send():
    global server_socket, myId

    while True:
        
        try:
            message = server_socket.recv(4096)
        except socket.error as e:
            newConnection()

        if message:
            libstegozoa.send(message, 15) #15 is the broadcast address
        else:
            newConnection()
        
        time.sleep(0.1)


def receive():
    global server_socket
    while True:
        message = libstegozoa.receive()

        try:
            server_socket.sendall(message)
        except socket.error as e:
            newConnection()




signal.signal(signal.SIGINT,sigInt_handler)
mutex = threading.Lock()

if len(sys.argv) > 1:
    myId = int(sys.argv[1])
else:
    myId = 1


server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    server.bind(socketPath)
except OSError as e:
    os.remove(socketPath)
    server.bind(socketPath)

server.listen(1)


libstegozoa.initialize(myId)
server_socket, address = server.accept()

thread = threading.Thread(target=send, args=())
thread.start()
thread = threading.Thread(target=receive, args=())
thread.start()
