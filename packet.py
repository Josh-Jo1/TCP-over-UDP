import logging
import struct

from constants import *

class Packet:
    def __init__(self, packet_num, ack_num, ack_bit, syn_bit, fin_bit, data):
        self.packet_num = packet_num
        self.ack_num = ack_num
        self.ack_bit = ack_bit
        self.syn_bit = syn_bit
        self.fin_bit = fin_bit
        self.data = data
    # end __init__

    def __repr__(self):
        return f"Packet({self.packet_num}, {self.ack_num}, {self.ack_bit}, {self.syn_bit}, {self.fin_bit}, {self.data})"
    # end __repr__
    
    def extract(self):
        return self.packet_num, self.ack_num, self.ack_bit, self.syn_bit, self.fin_bit, self.data
    # end extract
    
    def encode(self):
        return struct.pack("!IIbbb", self.packet_num, self.ack_num, self.ack_bit, self.syn_bit, self.fin_bit) + self.data.encode()
    # end encode

    @staticmethod
    def decode(bytes):
        packet_num, ack_num, ack_bit, syn_bit, fin_bit = struct.unpack("!IIbbb", bytes[:HEADER_SIZE])
        data = bytes[HEADER_SIZE:].decode()
        return Packet(packet_num, ack_num, ack_bit, syn_bit, fin_bit, data)
    # end decode
# end Packet

if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    msg = "Testing12345"
    packet1 = Packet(1, 3, 0, 1, 0, msg)
    logging.info(packet1)
    packet_bytes = packet1.encode()
    logging.info(packet_bytes)
    packet2 = Packet.decode(packet_bytes)
    logging.info(packet2)
    packet_num, ack_num, ack_bit, syn_bit, fin_bit, data = packet2.extract()
    logging.info(f"{packet_num}, {ack_num}, {ack_bit}, {syn_bit}, {fin_bit}, {data}")
