import logging
import socket
import time
from threading import Timer, Thread

from constants import *
from packet import Packet

class Receiver:
    def __init__(self, ne_addr, ne_port, bind_port):
        self.ne_addr = ne_addr
        self.ne_port = ne_port
        self.bind_port = bind_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_file = open(RECV_FILENAME, 'w')
    # end __init__

    def __del__(self):
        self.sock.close()
        self.recv_file.close()
    # end __del__

    def run(self):
        self.sock.bind(('', self.bind_port))

        # Receive handshake message
        bytes = self.sock.recv(RECV_BUFSIZE)
        packet_num, ack_num, _, _, _, _ = Packet.decode(bytes).extract()
        logging.info(f"Packet {packet_num} {ack_num} received")

        # Send handshake acknowledgement
        bytes = Packet(packet_num + 1, INIT_RECV_PACKET_NUM, 1, 1, 0, "").encode()
        self.sock.sendto(bytes, (self.ne_addr, self.ne_port))
        logging.info(f"Packet {packet_num + 1} {INIT_RECV_PACKET_NUM} sent")

        logging.info(f"Handshake done")


        while True:
            # Receive message
            bytes = self.sock.recv(RECV_BUFSIZE)
            packet_num, _, _, _, fin_bit, msg = Packet.decode(bytes).extract()
            logging.info(f"Packet {packet_num} received")

            # Store message
            if fin_bit == 0:
                self.recv_file.write(msg)

            # Send acknowledgement
            packet = Packet(packet_num + 1, 0, 1, 0, fin_bit, ACK_MSG)
            self.sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
            logging.info(f"Packet {packet_num} sent")

            if fin_bit == 1:
                break
    # end run
# end Receiver

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    receiver = Receiver(NE_ADDR, RECV_PORT, RECV_BIND_PORT)
    receiver.run()
