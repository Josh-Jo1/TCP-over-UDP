import struct

HEADER_SIZE = 12

class Packet:
    def __init__(self, type, seqnum, length, data):
        self.type = type
        self.seqnum = seqnum
        self.length = length
        self.data = data

    def encode(self):
        return struct.pack("!III", self.type, self.seqnum, self.length) + self.data.encode()
    
    def __repr__(self):
        return f'Packet({self.type}, {self.seqnum}, {self.length}, {self.data})'

    @staticmethod
    def decode(bytes):
        type, seqnum, length = struct.unpack("!III", bytes[:HEADER_SIZE])
        return Packet(type, seqnum, length, bytes[HEADER_SIZE:].decode())


if __name__ == "__main__":
    msg = "Testing12345"
    packet1 = Packet(1, 0, len(msg), msg)
    print(packet1)
    packet_bytes = packet1.encode()
    print(packet_bytes)
    packet2 = Packet.decode(packet_bytes)
    print(packet2)
