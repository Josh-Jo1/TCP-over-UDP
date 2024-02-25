import logging

from constants import *
from packet import Packet

class Window:
    def __init__(self):
        self.size = 0
        self.headIdx = 0
        self.tailIdx = 0
        self.capacity = 1
        self.window: list[Packet] = [None] * MAX_CWND_CAPACITY
    # end __init__

    def __repr__(self):
        formattedWindow = [None] * self.size
        i = self.headIdx
        while i != self.tailIdx:
            packet = self.window[i]
            packet_num, ack_num, _, _, _, _ = packet.extract()
            formattedWindow[i - self.headIdx] = f"Packet({packet_num}, {ack_num})"
            i = (i + 1) % MAX_CWND_CAPACITY
        return '[' + ", ".join(formattedWindow) + ']'
    # end __repr__

    def push(self, packet):
        if self.size == self.capacity:
            logging.warning("Window is full!")
            return
        if type(packet) != Packet:
            logging.warning(f"{packet} is not of type Packet!")
            return
        self.window[self.tailIdx] = packet
        self.tailIdx = (self.tailIdx + 1) % MAX_CWND_CAPACITY
        self.size += 1
    # end append

    def pop(self):
        if self.size == 0:
            logging.warning("Window is empty!")
            return
        self.headIdx = (self.headIdx + 1) % MAX_CWND_CAPACITY
        self.size -= 1
    # end pop

    def head(self):
        if self.size == 0:
            logging.warning("Window is empty!")
            return None
        return self.window[self.headIdx]
    # end head

    def clear(self):
        self.headIdx = 0
        self.tailIdx = 0
        self.size = 0
    # end clear

    def getSize(self):
        return self.size
    # end size

    def getCapacity(self):
        return self.capacity
    # end getCapacity

    def setCapacity(self, value):
        if value > MAX_CWND_CAPACITY:
            self.capacity = MAX_CWND_CAPACITY
            logging.warning(f"Capacity set to {MAX_CWND_CAPACITY}")
            return False
        self.capacity = value
        return True
    # end setCapacity
# end Window

if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    
    packet1 = Packet(1, 0, 0, 0, 0, "")
    packet2 = Packet(2, 0, 0, 0, 0, "")
    cwnd = Window()
    
    print(cwnd)
    # Expect "[]"
    assert cwnd.getSize() == 0
    assert cwnd.getCapacity() == 1
    
    cwnd.push(packet1)
    assert cwnd.getSize() == 1
    assert cwnd.getCapacity() == 1
    assert cwnd.head() == packet1
    
    cwnd.push(packet2)
    # Expect log "Window is full!"
    assert cwnd.getSize() == 1
    assert cwnd.getCapacity() == 1
    assert cwnd.head() == packet1
    
    print(cwnd)
    # Expect "[Packet(1, 0)]"
    
    retval = cwnd.setCapacity(2)
    assert retval == True
    assert cwnd.getSize() == 1
    assert cwnd.getCapacity() == 2

    cwnd.push(packet2)
    assert cwnd.getSize() == 2
    assert cwnd.getCapacity() == 2
    assert cwnd.head() == packet1

    print(cwnd)
    # Expect "[Packet(1, 0), Packet(2, 0)]"
    
    cwnd.pop()
    assert cwnd.getSize() == 1
    assert cwnd.getCapacity() == 2
    assert cwnd.head() == packet2
    
    print(cwnd)
    # Expect "[Packet(2, 0)]"
    
    retval = cwnd.setCapacity(MAX_CWND_CAPACITY + 1)
    # Expect log "Capacity set to <MAX_CWND_CAPACITY>"
    assert retval == False
    assert cwnd.getSize() == 1
    assert cwnd.getCapacity() == MAX_CWND_CAPACITY
