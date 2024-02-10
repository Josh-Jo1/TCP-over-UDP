import logging
import socket

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
        
        while True:
            # Receive message
            bytes = self.sock.recv(RECV_BUFSIZE)
            type, packet_num, _, msg = Packet.decode(bytes).extract()
            logging.info(f"Packet {packet_num} received")

            # Store message
            if type == DATA:
                self.recv_file.write(msg)

            # Send acknowledgement
            packet = Packet(type, packet_num, len(ACK_MSG), ACK_MSG)
            self.sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
            logging.info(f"Packet {packet_num} sent")

            if type == EOF:
                break
    # end run
# end Receiver

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    receiver = Receiver(NE_ADDR, RECV_PORT, RECV_BIND_PORT)
    receiver.run()
