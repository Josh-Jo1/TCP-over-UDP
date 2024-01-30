import socket
import threading

from constants import *
from packet import Packet

class NetworkEmulator:
    def __init__(self, send_addr, send_port, send_bind_port, recv_addr, recv_port, recv_bind_port):
        self.send_addr = send_addr
        self.send_port = send_port
        self.send_bind_port = send_bind_port
        self.recv_addr = recv_addr
        self.recv_port = recv_port
        self.recv_bind_port = recv_bind_port
    # end __init__

    def createChannel(self, bind_port, dest_addr, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', bind_port))
        while True:
            bytes = sock.recv(RECV_BUFSIZE)
            print(Packet.decode(bytes), end='\n\n')
            sock.sendto(bytes, (dest_addr, dest_port))
    # end createChannel
    
    def run(self):
        sendThread = threading.Thread(target=self.createChannel, args=(self.recv_bind_port, self.recv_addr, self.recv_port))
        recvThread = threading.Thread(target=self.createChannel, args=(self.send_bind_port, self.send_addr, self.send_port))
        sendThread.start()
        recvThread.start()
    # end run
# end NetworkEmulator

if __name__ == '__main__':
    networkEmulator = NetworkEmulator(SEND_ADDR, RECV_BIND_PORT, SEND_PORT, RECV_ADDR, SEND_BIND_PORT, RECV_PORT)
    networkEmulator.run()
