import logging
import struct

from constants import *

class Packet:
    def __init__(self, type, packet_num, length, data):
        self.type = type
        self.packet_num = packet_num
        self.length = length
        self.data = data
    # end __init__

    def __repr__(self):
        return f"Packet({self.type}, {self.packet_num}, {self.length}, {self.data})"
    # end __repr__
    
    def extract(self):
        return self.type, self.packet_num, self.length, self.data
    # end extract
    
    def encode(self):
        return struct.pack("!III", self.type, self.packet_num, self.length) + self.data.encode()
    # end encode

    @staticmethod
    def decode(bytes):
        type, packet_num, length = struct.unpack("!III", bytes[:HEADER_SIZE])
        return Packet(type, packet_num, length, bytes[HEADER_SIZE:].decode())
    # end decode
# end Packet

if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    msg = "Testing12345"
    packet1 = Packet(1, 0, len(msg), msg)
    logging.info(packet1)
    packet_bytes = packet1.encode()
    logging.info(packet_bytes)
    packet2 = Packet.decode(packet_bytes)
    logging.info(packet2)
    type, packet_num, length, data = packet2.extract()
    logging.info(type, packet_num, length, data)
