import logging
import random
import socket
from threading import Thread 

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
        packet_num, ack_num, _, syn_bit, fin_bit, _ = Packet.decode(bytes).extract()
        logging.info(f"{thread_name}: Packet {packet_num} {ack_num} received")

        if (syn_bit == 0 and fin_bit == 0):     # data packet?
            # Packet may be dropped
            if (random.random() < PROB_DROP):
                logging.info(f"{thread_name}: Packet {packet_num} {ack_num} dropped")
                return

        # Packet is sent
        sock.sendto(bytes, (dest_addr, dest_port))
        logging.info(f"{thread_name}: Packet {packet_num} {ack_num} sent")
    # end processPacket

    def createChannel(self, thread_name, bind_port, dest_addr, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', bind_port))
        while True:
            bytes = sock.recv(RECV_BUFSIZE)
            self.processPacket(thread_name, sock, dest_addr, dest_port, bytes)
    # end createChannel
    
    def run(self):
        sendThread = Thread(target=self.createChannel, args=("send", self.recv_bind_port, self.recv_addr, self.recv_port))
        recvThread = Thread(target=self.createChannel, args=("recv", self.send_bind_port, self.send_addr, self.send_port))
        sendThread.start()
        recvThread.start()
    # end run
# end NetworkEmulator

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    networkEmulator = NetworkEmulator(SEND_ADDR, RECV_BIND_PORT, SEND_PORT, RECV_ADDR, SEND_BIND_PORT, RECV_PORT)
    networkEmulator.run()
