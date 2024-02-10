import socket
import threading

from constants import *
from packet import Packet

class Sender:
    def __init__(self, ne_host, ne_port, bind_port):
        self.ne_host = ne_host
        self.ne_port = ne_port
        self.bind_port = bind_port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.send_file = open(SEND_FILENAME, 'r')
    # end __init__

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()

        self.send_file.close()
    # end __del__

    def sendData(self):
        seqnum = 0
        while True:
            # Get message
            msg = self.send_file.read(PACKET_MAX_DATA_SIZE)
            if msg == '':
                msg = "EOF"

            # Send message
            type = 2 if msg == "EOF" else 1
            packet = Packet(type, seqnum, len(msg), msg)
            self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
            print(f"Packet {seqnum} sent")

            seqnum += 1
            if msg == "EOF":
                break
    # end sendData
        
    def recvData(self):
        while True:
            # Receive acknowledgement
            bytes = self.recv_sock.recv(RECV_BUFSIZE)
            type, seqnum, _, msg = Packet.decode(bytes).extract()
            print(f"Packet {seqnum} received: {msg}")
            if (type == 2):
                break

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        sendThread = threading.Thread(target=self.sendData)
        recvThread = threading.Thread(target=self.recvData)
        sendThread.start()
        recvThread.start()
        sendThread.join()
        recvThread.join()
    # end run
# end Sender

if __name__ == '__main__':
    sender = Sender(NE_ADDR, SEND_PORT, SEND_BIND_PORT)
    sender.run()
