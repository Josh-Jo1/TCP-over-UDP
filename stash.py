import logging

from constants import *
from packet import Packet

class Stash:
    def __init__(self):
        self.size = 0
        self.headIdx = 0
        self.buffer: list[Packet] = [None] * STASH_CAPACITY
    # end __init__

    def __repr__(self):
        formattedBuffer = [None] * self.size
        formattedBufferIdx = 0
        i = self.headIdx
        while formattedBufferIdx < self.size:
            packet = self.buffer[i]
            if packet is not None:
                packet_num, ack_num, _, _, _, _ = packet.extract()
                formattedBuffer[formattedBufferIdx] = f"{i}: Packet({packet_num}, {ack_num})"
                formattedBufferIdx += 1
            i = (i + 1) % STASH_CAPACITY
        return '[' + ", ".join(formattedBuffer) + ']'
    # end __repr__

    def insert(self, index, packet):
        if not 0 <= index < STASH_CAPACITY:
            logging.warning(f"{index} out of range!")
            return
        if type(packet) != Packet:
            logging.warning(f"{packet} is not of type Packet!")
            return
        translatedIndex = (self.headIdx + index) % STASH_CAPACITY
        if self.buffer[translatedIndex] is None:
            self.buffer[translatedIndex] = packet
            self.size += 1
    # end insert

    def pop(self):
        if self.buffer[self.headIdx] is not None:
            self.size -= 1
            self.buffer[self.headIdx] = None
        self.headIdx = (self.headIdx + 1) % STASH_CAPACITY
    # end pop

    def head(self):
        return self.buffer[self.headIdx]
    # end head

    def getSize(self):
        return self.size
    # end size
# end Stash

if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    
    packet1 = Packet(1, 0, 0, 0, 0, "")
    packet2 = Packet(2, 0, 0, 0, 0, "")
    stash = Stash()
    
    print(stash)
    # Expect "[]"
    assert stash.getSize() == 0
    assert stash.head() == None
    
    stash.insert(1, packet1)
    assert stash.getSize() == 1
    assert stash.head() == None
    
    print(stash)
    # Expect "[1: Packet(1, 0)]"

    stash.insert(0, packet2)
    assert stash.getSize() == 2
    assert stash.head() == packet2
    
    print(stash)
    # Expect "[0: Packet(2, 0), 1: Packet(1, 0)]"
    
    stash.pop()
    assert stash.getSize() == 1
    assert stash.head() == packet1
    
    print(stash)
    # Expect "[0: Packet(1, 0)]"

    stash.insert(0, packet2)
    assert stash.getSize() == 1
    assert stash.head() == packet1

    stash.pop()
    assert stash.getSize() == 0
    assert stash.head() == None

    stash.pop()
    assert stash.getSize() == 0
    assert stash.head() == None
