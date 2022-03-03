import os
import time
import threading
import queue
import sys
import signal
import errno

import crccheck

decoderPipePath = "/tmp/stegozoa_decoder_pipe"
encoderPipePath = "/tmp/stegozoa_encoder_pipe"
fragmentQueue = queue.Queue()
messageQueue = queue.Queue()
peers = []
myId = 15


messageToSend = {}
messageToReceive = {}


globalMutex = threading.Lock()
sendMutex = threading.Lock()


def createCRC(message):
    crc = crccheck.crc.Crc32.calc(message)
    l1 = bytes([crc & 0xff])
    l2 = bytes([(crc & 0xff00) >> 8])
    l3 = bytes([(crc & 0xff0000) >> 16])
    l4 = bytes([(crc & 0xff000000) >> 24])
    return l1 + l2 + l3 + l4

def validateCRC(message, crc):
    return createCRC(message) == crc


def parse2byte(header): #header: string with two chars
    size = int(header[0]) + (int(header[1]) << 8)
    return size

def create2byte(number):
    l1 = bytes([number & 0xff])
    l2 = bytes([(number & 0xff00) >> 8])
    return l1 + l2


def createMessage(msgType, sender, receiver, frag = 0, syn = 0, byteArray = bytes(0), crc = False):

    flags = bytes([((msgType & 0x7) << 5) | ((frag & 0x1) << 4)])
    flags += bytes([((sender & 0xf) << 4) | (receiver & 0xf)])

    message = flags + create2byte(syn) + byteArray
    if crc:
        size = create2byte(len(message) + 4) # + 4 is the crc
        message = size + message
        message = message + createCRC(message)
    else:
        message = create2byte(len(message)) + message
    
    return message

def sendMessage(message):
    global encoderPipe, encoderPipePath

    try:
        encoderPipe.write(message)
        encoderPipe.flush()
    except Exception:
        encoderPipe = open(encoderPipePath, 'wb')


def processRetransmission(syn, retransmissions, message):
    global sendMutex
    while True:
       
        sendMutex.acquire()
        size = len(retransmissions)
        if syn in retransmissions:
            sendMessage(message)
        else:
            sendMutex.release()
            return

        sendMutex.release()

        time.sleep(110 - 100 * (0.995 ** size))



def addFragment(message, frag):
    global fragmentQueue, messageQueue


    if len(message) == 0:
        return

    if frag == 0:
        res = bytes(0)
        while not fragmentQueue.empty():
            res += fragmentQueue.get()
        res += message
        messageQueue.put(res)
    else:
        fragmentQueue.put(message)


class sendQueue:

    def __init__(self):
        self.queue = {}
        self.frag = {}
        self.syn = 65500
        self.mutex = threading.Lock() 

    def addMessage(self, message, frag):
        self.mutex.acquire()
        if len(self.queue) > 10000:
            del(self.queue[min(self.queue)])
            del(self.frag[min(self.frag)])

        self.queue[self.syn] = message
        self.frag[self.syn] = frag

        syn = self.syn & 0xffff
        self.syn += 1
        self.mutex.release()
        return syn

    def getMessage(self, syn):
        self.mutex.acquire()
        least = min(self.queue) // 65536
        most = max(self.queue) // 65536
        if self.queue.get(least * 65536 + syn):
            message = self.queue[least * 65536 + syn]
        elif self.queue.get(most * 65536 + syn):
            message = self.queue[most * 65536 + syn]
        else:
            message = bytes(0)
        self.mutex.release()
        return message
    
    def getFrag(self, syn):
        self.mutex.acquire()
        least = min(self.queue) // 65536
        most = max(self.queue) // 65536
        if self.frag.get(least * 65536 + syn):
            frag = self.frag[least * 65536 + syn]
        elif self.frag.get(most * 65536 + syn):
            frag = self.frag[most * 65536 + syn]
        else:
            frag = 0
        self.mutex.release()
        return frag


class recvQueue:

    def __init__(self):
        self.queue = {}
        self.frag = {}
        self.syn = 65500
        self.retransmissions = {}
        self.duplicates = 0
        self.mutex = threading.Lock()

    def addMessage(self, message, sender, receiver, frag, syn):
        global messageQueue, sendMutex
        
        self.mutex.acquire()
        print("Expected syn: " + str(self.syn))
        if syn > self.syn and abs(syn - self.syn) < 10000 or syn + 65536 - self.syn < 10000:


            if syn in self.queue:
                self.duplicates += 1
                print("Duplicates: " + str(self.duplicates))
            else:
                self.queue[syn] = message
                self.frag[syn] = frag

                if syn in self.retransmissions:
                    del(self.retransmissions[syn])

                print("Retransmission!")
                
                if syn < self.syn: #wrap around 65536
                    syn += 65536
                for i in range(self.syn, syn):
                    
                    actualSyn = i & 0xffff

                    if actualSyn in self.retransmissions or actualSyn in self.queue:
                        continue
                    else:
                        self.retransmissions[actualSyn] = actualSyn

                    response = createMessage(3, receiver, sender, 0, 0, create2byte(actualSyn), True)
                    
                    thread = threading.Thread(target=processRetransmission, args=(actualSyn, self.retransmissions, response), daemon=True)
                    thread.start() #have single thread doing this? TODO


        elif syn == self.syn:

            if syn in self.retransmissions:
                del(self.retransmissions[syn])

            addFragment(message, frag)
            
            self.syn = (self.syn + 1) & 0xffff

            first = list(filter(lambda x: x >= self.syn, self.queue.keys()))
            second = list(filter(lambda x: x < self.syn, self.queue.keys())) #in case of wrap around 65536

            for key in sorted(first):
                if key == self.syn:

                    addFragment(self.queue[key], self.frag[key])
                    del(self.queue[key])
                    del(self.frag[key])
                    self.syn = (self.syn + 1) & 0xffff

                else:
                    break
            
            for key in sorted(second):
                if key == self.syn:

                    addFragment(self.queue[key], self.frag[key])
                    del(self.queue[key])
                    del(self.frag[key])
                    self.syn = (self.syn + 1) & 0xffff

                else:
                    break

        else:
            self.duplicates += 1
            print("Duplicates: " + str(self.duplicates))

        self.mutex.release()



def broadcastKeepalive():
    global sendMutex, messageToSend
    
    while True:
        time.sleep(5)

        sendMutex.acquire()

        for receiver in messageToSend:
            syn = messageToSend[receiver].addMessage(bytes(0), 0)
            message = createMessage(2, myId, receiver, 0, syn, bytes(0), True)
            sendMessage(message)

        sendMutex.release()

def broadcastConnect():
    global sendMutex

    while True:
        time.sleep(10)

        sendMutex.acquire()

        message = createMessage(0, myId, 15) # 0xf = broadcast address
        sendMessage(message)
        
        sendMutex.release()


def retransmit(receiver, synBytes):
    global messageToSend, myId, encoderPipe, sendMutex

    syn = parse2byte(synBytes)
    print("Retransmission request! " + str(syn))

    sendMutex.acquire()
    
    message = messageToSend[receiver].getMessage(syn)
    frag = messageToSend[receiver].getFrag(syn)
    message = createMessage(4, myId, receiver, frag, syn, message, True)
    sendMessage(message)

    sendMutex.release()

def parseMessage(message):

    size = parse2byte(message[0:2])

    if size < 4:
        print("Unexpected message size")
        return None

    msgType = (message[2] & 0xe0) >> 5
    frag = (message[2] & 0x10) >> 4
    sender = (message[3] & 0xf0) >> 4
    receiver = (message[3] & 0xf)
    syn = parse2byte(message[4:6])

    if msgType == 0:
        payload = message[6:size + 2] # + 2 counting the size header
        crc = bytes(0)
    else:
        if size < 8:
            print("Unexpected message size")
            return None
        payload = message[6:size + 2 - 4] # + 2 counting the size header
        crc = message[size + 2 - 4:size + 2]

    return {'size': size, 'msgType' : msgType, 'frag' : frag, 'sender' : sender, 'receiver' : receiver, 'syn' : syn, 'payload' : payload, 'crc' : crc}



def receiveMessage():
    global messageToSend, decoderPipe, decoderPipePath, peers, globalMutex, sendMutex

    success = 0
    insuccess = 0
    
    while True:

        header = decoderPipe.read(2) #size header
        if(len(header) == 0):
            decoderPipe = open(decoderPipePath, 'rb')
            continue
        size = parse2byte(header)
        
        body = decoderPipe.read(size) #message body
        
        parsedMessage = parseMessage(header + body)
        
        if not parsedMessage:
            continue

        msgType = parsedMessage['msgType']
        frag = parsedMessage['frag']
        sender = parsedMessage['sender']
        receiver = parsedMessage['receiver']
        syn = parsedMessage['syn']
        payload = parsedMessage['payload']
        crc = parsedMessage['crc']

        print("Syn: " + str(syn))
        print("MsgType: " + str(msgType))

        if msgType == 0: #type 0 messages dont need crc, they should be small enough

            sendMutex.acquire()
            if sender not in messageToSend:
                messageToSend[sender] = sendQueue()
            
            message = createMessage(1, myId, sender, 0, 0, payload, True) #payload is the ssrc in this case, must be sent back
            sendMessage(message)
            sendMutex.release()
            continue
        
        success = success + 1
        
        if not validateCRC(header + body[:size - 4], crc): 
            print("Corrupted message!")
            #print(header + body)
            insuccess = insuccess + 1
            success = success - 1
            continue

        sendMutex.acquire()
        if sender not in messageToSend:
            messageToSend[sender] = sendQueue()
        sendMutex.release()

        globalMutex.acquire()
        key = sender
        if receiver == 15:
            key += 15
        if key not in messageToReceive:
            messageToReceive[key] = recvQueue()
        globalMutex.release()
        
    

        if msgType == 1:
            if receiver == myId and sender not in peers:
                peers += [sender]

        elif msgType == 2 or msgType == 4:
            if receiver == myId or receiver == 15: #15 is the broadcast address
                messageToReceive[key].addMessage(payload, sender, receiver, frag, syn)


        elif msgType == 3:
            if receiver == myId:
                retransmit(sender, payload)


        print("Ratio: " + str(success * 1.0 / (success + insuccess)))


def connect():
    global encoderPipe, myId

    msgType = 0
    message = createMessage(msgType, myId, 15) # 0xf = broadcast address

    sendMessage(message)

    thread = threading.Thread(target=broadcastKeepalive, args=(), daemon=True)
    thread.start()
    
    thread = threading.Thread(target=broadcastConnect, args=(), daemon=True)
    thread.start()
    

def sigInt_handler(signum,frame):
    global encoderPipePath, decoderPipePath
    os.remove(encoderPipePath)
    os.remove(decoderPipePath)
    exit(0)


#---------------------API begins here---------------------------------

def initialize(newId):

    global encoderPipe, decoderPipe, encoderPipePath, decoderPipePath, myId
    try:
        os.mkfifo(encoderPipePath)
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

    try:
        os.mkfifo(decoderPipePath)
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

    encoderPipe = open(encoderPipePath, 'wb')
    decoderPipe = open(decoderPipePath, 'rb')

    thread = threading.Thread(target=receiveMessage, args=(), daemon=True)
    thread.start()

    myId = newId
    connect()


def shutdown():
    global encoderPipePath, decoderPipePath
    os.remove(encoderPipePath)
    os.remove(decoderPipePath)



def send(byteArray, receiver):
    global encoderPipe, messageToSend, sendMutex
    
    if len(byteArray) == 0:
        raise "Message must have length bigger than 0"
    
    sendMutex.acquire()
    if receiver not in messageToSend:
        messageToSend[receiver] = sendQueue()

    array = bytes(0)
    for i in range(0, len(byteArray), 242):
        array = byteArray[i:i+242]

        frag = 1
        if i + 242 >= len(byteArray):
            frag = 0

        syn = messageToSend[receiver].addMessage(array, frag)

        message = createMessage(2, myId, receiver, frag, syn, array, True)

        sendMessage(message)

    sendMutex.release()


def receive():
    global messageQueue
    return messageQueue.get()


def getPeers():
    global peers
    return peers



if __name__ == "__main__":
    if len(sys.argv) > 1:
        myId = int(sys.argv[1])
    else:
        myId = 1
    signal.signal(signal.SIGINT,sigInt_handler)
    initialize(myId)
    #connect()
    #while len(getPeers()) < 1:
    #    time.sleep(0.5)
    message = "Why are we still here... just to suffer"
    #send(bytes(message, 'utf-8'), getPeers()[0])
    #print(receive())

