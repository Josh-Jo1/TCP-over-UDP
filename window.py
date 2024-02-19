import logging

from packet import Packet

class Window:
    def __init__(self, capacity):
        self.size = 0
        self.window = [None] * capacity
    # end __init__
        
    def __repr__(self):
        formattedWindow = [None] * self.size
        for i in range(self.size):
            packet = self.window[i]
            packet_num, ack_num, _, _, _, _ = packet.extract()
            formattedWindow[i] = f"Packet({packet_num}, {ack_num})"
        return formattedWindow
    # end __repr__

    def push(self, packet):
        if type(packet) != Packet:
            logging.warning(f"{packet} is not of type Packet!")
            return
        self.window[self.size] = packet
        self.size += 1
    # end append

    def pop(self):
        if self.size == 0:
            logging.warning(f"Window is empty!")
            return
        self.size -= 1
        return self.window[self.size]
    # end pop

    def head(self):
        return self.window[0]
    # end head

    def size(self):
        return self.size
    # end size
# end Window
