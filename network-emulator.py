import random
import socket
import threading

from constants import *
from packet import Packet

class NetworkEmulator:
    def __init__(self, send_addr, send_port, send_bind_port, recv_addr, recv_port, recv_bind_port):
        self.send_addr = send_addr
        self.send_port = send_port
        self.send_bind_port = send_bind_port
        self.recv_addr = recv_addr
        self.recv_port = recv_port
        self.recv_bind_port = recv_bind_port
    # end __init__
    
    def processPacket(self, thread_name, sock, dest_addr, dest_port, bytes):
        type, seqnum, _, _ = Packet.decode(bytes).extract()
        print(f"{thread_name}: Packet {seqnum} received")

        if (type == 1):
            # Packet may be dropped
            if (random.random() < PROB_DROP):
                print(f"{thread_name}: Packet {seqnum} dropped")
                return

        # Packet is sent
        sock.sendto(bytes, (dest_addr, dest_port))
        print(f"{thread_name}: Packet {seqnum} sent")
    # end processPacket

    def createChannel(self, thread_name, bind_port, dest_addr, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', bind_port))
        while True:
            bytes = sock.recv(RECV_BUFSIZE)
            self.processPacket(thread_name, sock, dest_addr, dest_port, bytes)
    # end createChannel
    
    def run(self):
        sendThread = threading.Thread(target=self.createChannel, args=("send", self.recv_bind_port, self.recv_addr, self.recv_port))
        recvThread = threading.Thread(target=self.createChannel, args=("recv", self.send_bind_port, self.send_addr, self.send_port))
        sendThread.start()
        recvThread.start()
    # end run
# end NetworkEmulator

if __name__ == '__main__':
    networkEmulator = NetworkEmulator(SEND_ADDR, RECV_BIND_PORT, SEND_PORT, RECV_ADDR, SEND_BIND_PORT, RECV_PORT)
    networkEmulator.run()
