import struct

from constants import *

class Packet:
    def __init__(self, type, seqnum, length, data):
        self.type = type
        self.seqnum = seqnum
        self.length = length
        self.data = data

    def __repr__(self):
        return f'Packet({self.type}, {self.seqnum}, {self.length}, {self.data})'
    
    def extract(self):
        return self.type, self.seqnum, self.length, self.data
    
    def encode(self):
        return struct.pack("!III", self.type, self.seqnum, self.length) + self.data.encode()

    @staticmethod
    def decode(bytes):
        type, seqnum, length = struct.unpack("!III", bytes[:PACKET_HEADER_SIZE])
        return Packet(type, seqnum, length, bytes[PACKET_HEADER_SIZE:].decode())


if __name__ == "__main__":
    msg = "Testing12345"
    packet1 = Packet(1, 0, len(msg), msg)
    print(packet1)
    packet_bytes = packet1.encode()
    print(packet_bytes)
    packet2 = Packet.decode(packet_bytes)
    print(packet2)
    type, seqnum, length, data = packet2.extract()
    print(type, seqnum, length, data)
