import logging
import socket

from constants import *
from packet import Packet
from stash import Stash

class Receiver:
    def __init__(self, ne_addr, ne_port, bind_port):
        self.ne_addr = ne_addr
        self.ne_port = ne_port
        self.bind_port = bind_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_file = open(RECV_FILENAME, 'w')

        self.packet_num = None
        self.expected_packet_num = None

        # Receiver Stash
        self.stash = Stash()
    # end __init__

    def __del__(self):
        self.sock.close()
        self.recv_file.close()
    # end __del__

    def stashPacketIfPossible(self, packet_num, packet):
        futurePacketNum = packet_num - self.expected_packet_num - 1
        if 0 <= futurePacketNum < STASH_CAPACITY:
            self.stash.insert(futurePacketNum, packet)
        logging.info(f"insert stash = {self.stash}")
    # end stashPacketIfPossible

    def writeDataFromStashedPacketsWhilePossible(self):
        packet_num = None
        fin_bit = None
        while self.stash.head() is not None:
            packet_num, _, _, _, fin_bit, msg = self.stash.head().extract()
            # Store message
            if fin_bit == 0:
                self.recv_file.write(msg)
            self.expected_packet_num += 1
            self.stash.pop()
        logging.info(f"pop stash = {self.stash}")
        return packet_num, fin_bit
    # end writeDataFromStashedPacketsWhilePossible

    def complete3WayHandshake(self):
        while True:
            # Receive packet
            bytes = self.sock.recv(RECV_BUFSIZE)
            packet_num, ack_num, ack_bit, syn_bit, _, _ = Packet.decode(bytes).extract()
            logging.info("Packet received")

            if syn_bit == 1 and ack_bit == 0:
                self.expected_packet_num = packet_num + 1
                # Send SYN ACK packet
                packet = Packet(INIT_RECV_PACKET_NUM, self.expected_packet_num, 1, 1, 0, "")
                self.sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
                logging.info("SYN ACK Packet sent")
            elif syn_bit == 1 and ack_bit == 1:
                self.packet_num = ack_num
                break
            else:
                self.stashPacketIfPossible(packet_num, packet)

        self.writeDataFromStashedPacketsWhilePossible()
        logging.info(f"Handshake done {self.packet_num} {self.expected_packet_num}")
    # end complete3WayHandshake

    def run(self):
        self.sock.bind(('', self.bind_port))
        self.complete3WayHandshake()

        while True:
            # Receive message
            bytes = self.sock.recv(RECV_BUFSIZE)
            packet = Packet.decode(bytes)
            packet_num, _, _, _, fin_bit, msg = packet.extract()
            logging.info(f"Packet {packet_num} received")

            if self.expected_packet_num == packet_num:
                # Store message
                if fin_bit == 0:
                    self.recv_file.write(msg)
                self.expected_packet_num += 1
                ret_packet_num, ret_fin_bit = self.writeDataFromStashedPacketsWhilePossible()
                if ret_packet_num is not None:
                    packet_num = ret_packet_num
                    fin_bit = ret_fin_bit
                self.stash.pop()
            else:
                self.stashPacketIfPossible(packet_num, packet)

            # Send acknowledgement
            packet = Packet(self.packet_num, self.expected_packet_num, 1, 0, fin_bit, ACK_MSG)
            self.sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
            logging.info(f"Packet {self.expected_packet_num} sent")

            if fin_bit == 1 and self.expected_packet_num - 1 == packet_num:    # this works since FIN packets not dropped
                break
    # end run
# end Receiver

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    receiver = Receiver(NE_ADDR, RECV_PORT, RECV_BIND_PORT)
    receiver.run()
